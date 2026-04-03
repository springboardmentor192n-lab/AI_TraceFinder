"""
TraceFinder Backend API with Authentication & Inference
Provides REST endpoints for user management and image analysis
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import numpy as np
import cv2
import pywt
import pickle
import json
import os
import logging
from PIL import Image
import tensorflow as tf
from datetime import datetime

# ================== CONFIGURATION ==================
APP_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(APP_DIR)
ART_DIR = os.path.join(PROJECT_DIR, 'artifacts')
PATCH_DIR = os.path.join(ART_DIR, 'artifacts_tamper_patch')

IMG_SIZE = (256, 256)
PSIZ = 128
STRIDE = 64
MAX_P = 16
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

# ================== LOGGING SETUP ==================
log_dir = os.path.join(PROJECT_DIR, 'logs')
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'api.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Patch TensorFlow warning
try:
    _dense_init = tf.keras.layers.Dense.__init__
    def _patched_dense_init(self, *args, **kwargs):
        kwargs.pop('quantization_config', None)
        return _dense_init(self, *args, **kwargs)
    tf.keras.layers.Dense.__init__ = _patched_dense_init
except Exception as e:
    logger.warning(f"Failed to patch TensorFlow Dense: {e}")

# ================== FLASK APP & DB SETUP ==================
app = Flask(__name__)
app.config['SECRET_KEY'] = 'tracefinder-secret-key-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(PROJECT_DIR, "tracefinder.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

CORS(app, supports_credentials=True)

# ================== DATABASE MODELS ==================
class User(UserMixin, db.Model):
    """User model for authentication"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    analyses = db.relationship('Analysis', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }


class Analysis(db.Model):
    """Analysis history model"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    tampered = db.Column(db.Boolean, nullable=False)
    tamper_score = db.Column(db.Float, nullable=False)
    top_scanner = db.Column(db.String(100), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'tampered': self.tampered,
            'tamper_score': self.tamper_score,
            'top_scanner': self.top_scanner,
            'confidence': self.confidence,
            'created_at': self.created_at.isoformat()
        }


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for login manager"""
    return User.query.get(int(user_id))

# ================== FEATURE EXTRACTION FUNCTIONS ==================

def load_residual(img_bgr):
    """Extract residual from image using Haar wavelet"""
    try:
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY) if img_bgr.ndim == 3 else img_bgr
        gray = cv2.resize(gray, IMG_SIZE, interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
        cA, (cH, cV, cD) = pywt.dwt2(gray, 'haar')
        cH.fill(0); cV.fill(0); cD.fill(0)
        return (gray - pywt.idwt2((cA, (cH, cV, cD)), 'haar')).astype(np.float32)
    except Exception as e:
        logger.error(f"Error in load_residual: {e}")
        raise


def extract_patches(res):
    """Extract patches from residual"""
    try:
        H, W = res.shape
        coords = [(y, x) for y in range(0, H-PSIZ+1, STRIDE) for x in range(0, W-PSIZ+1, STRIDE)]
        np.random.RandomState(42).shuffle(coords)
        return [res[y:y+PSIZ, x:x+PSIZ] for y, x in coords[:MAX_P]]
    except Exception as e:
        logger.error(f"Error in extract_patches: {e}")
        raise


def corr2d(a, b):
    """2D cross-correlation normalized"""
    try:
        a = a.ravel().astype(np.float32); a -= a.mean()
        b = b.ravel().astype(np.float32); b -= b.mean()
        d = np.linalg.norm(a) * np.linalg.norm(b)
        return float((a @ b) / d) if d > 0 else 0.0
    except Exception as e:
        logger.error(f"Error in corr2d: {e}")
        return 0.0


def fft_radial(img, K=6):
    """FFT radial binning"""
    try:
        mag = np.abs(np.fft.fftshift(np.fft.fft2(img)))
        h, w = mag.shape; cy, cx = h//2, w//2
        yy = np.arange(h).reshape(-1,1); xx = np.arange(w).reshape(1,-1)
        r = np.sqrt((yy-cy)**2 + (xx-cx)**2)
        bins = np.linspace(0, r.max()+1e-6, K+1)
        return np.array([float(mag[(r>=bins[i])&(r<bins[i+1])].mean()) for i in range(K)], dtype=np.float32)
    except Exception as e:
        logger.error(f"Error in fft_radial: {e}")
        raise


def lbp_hist(img, P=8, R=1.0):
    """Local Binary Pattern histogram"""
    try:
        rng = float(np.ptp(img))
        g = np.zeros_like(img, np.float32) if rng<1e-12 else (img-float(np.min(img)))/(rng+1e-8)
        codes = cv2.calcHist([((g*255).astype(np.uint8))], [0], None, [P+2], [0, P+2])
        hist = codes.ravel().astype(np.float32)
        if hist.sum() > 0:
            hist /= hist.sum()
        return hist
    except Exception as e:
        logger.error(f"Error in lbp_hist: {e}")
        raise


def res_stats(img):
    """Residual statistics: mean, std, absolute mean"""
    try:
        return np.array([img.mean(), img.std(), np.mean(np.abs(img))], dtype=np.float32)
    except Exception as e:
        logger.error(f"Error in res_stats: {e}")
        raise


def fft_resample(img):
    """FFT resampling features"""
    try:
        mag = np.abs(np.fft.fftshift(np.fft.fft2(img)))
        h, w = mag.shape; cy, cx = h//2, w//2
        yy = np.arange(h).reshape(-1,1); xx = np.arange(w).reshape(1,-1)
        r = np.sqrt((yy-cy)**2+(xx-cx)**2); rmax = r.max()+1e-6
        e1 = float(mag[(r>=.25*rmax)&(r<.35*rmax)].mean())
        e2 = float(mag[(r>=.35*rmax)&(r<.50*rmax)].mean())
        return np.array([e1, e2, e2/(e1+1e-8)], dtype=np.float32)
    except Exception as e:
        logger.error(f"Error in fft_resample: {e}")
        raise


def patch_feat(p):
    """Patch-level feature extraction"""
    try:
        return np.concatenate([lbp_hist(p,8,1.0), fft_radial(p,6), res_stats(p), fft_resample(p)])
    except Exception as e:
        logger.error(f"Error in patch_feat: {e}")
        raise


def scanner_feats(res, fps, fp_keys, scaler):
    """Scanner fingerprint features"""
    try:
        v = np.array([corr2d(res, fps[k]) for k in fp_keys] + fft_radial(res,6).tolist() + lbp_hist(res,8,1.0).tolist(), dtype=np.float32).reshape(1,-1)
        return scaler.transform(v)
    except Exception as e:
        logger.error(f"Error in scanner_feats: {e}")
        raise

# ================== MODEL LOADING ==================
ARTS = None
MISSING = []


def load_arts():
    """Load all model artifacts once"""
    global ARTS, MISSING
    if ARTS is not None:
        return ARTS

    required = {
        'model': os.path.join(ART_DIR, 'scanner_hybrid.keras'),
        'le': os.path.join(ART_DIR, 'hybrid_label_encoder.pkl'),
        'scaler': os.path.join(ART_DIR, 'hybrid_feat_scaler.pkl'),
        'fps': os.path.join(ART_DIR, 'scanner_fingerprints.pkl'),
        'fpk': os.path.join(ART_DIR, 'fp_keys.npy')
    }

    missing = [k for k,v in required.items() if not os.path.exists(v)]
    if missing:
        MISSING = missing
        logger.error(f"Missing required artifacts: {missing}")
        return None

    try:
        arts = {
            'model': tf.keras.models.load_model(required['model']),
            'le': pickle.load(open(required['le'],'rb')),
            'scaler': pickle.load(open(required['scaler'],'rb')),
            'fps': pickle.load(open(required['fps'],'rb')),
            'fp_keys': np.load(required['fpk'], allow_pickle=True).tolist(),
            'patch_support': False
        }

        optional = {
            'psvm': os.path.join(PATCH_DIR, 'patch_svm_sig_calibrated.pkl'),
            'psc': os.path.join(PATCH_DIR, 'patch_scaler.pkl'),
            'pthr': os.path.join(PATCH_DIR, 'thresholds_patch.json')
        }
        if all(os.path.exists(p) for p in optional.values()):
            arts.update({
                'psvm': pickle.load(open(optional['psvm'],'rb')),
                'psc': pickle.load(open(optional['psc'],'rb')),
                'pthr': json.load(open(optional['pthr'],'r')),
                'patch_support': True
            })
            logger.info("Patch support enabled")
        else:
            arts.update({'psvm': None, 'psc': None, 'pthr': None})

        ARTS = arts
        logger.info("All artifacts loaded successfully")
        return arts

    except Exception as e:
        logger.error(f"Error loading artifacts: {e}")
        raise


def run_inference(img_bgr, arts):
    """Run full inference pipeline with error handling"""
    try:
        res = load_residual(img_bgr)
        x_img = np.expand_dims(res, axis=(0,-1)).astype(np.float32)
        x_ft = scanner_feats(res, arts['fps'], arts['fp_keys'], arts['scaler'])
        
        probs = arts['model'].predict([x_img, x_ft], verbose=0).ravel()
        top_idx = np.argsort(probs)[::-1][:3]
        top3 = [(arts['le'].classes_[i], float(probs[i]*100.0)) for i in top_idx]

        patch_support = arts.get('patch_support', False)
        score = 0.0
        tampered = False
        thr = 0.0

        if patch_support:
            patches = extract_patches(res)
            if patches:
                pf = np.array([patch_feat(p) for p in patches], dtype=np.float32)
                pp = arts['psvm'].predict_proba(arts['psc'].transform(pf))[:,1]
                k = max(1, int(len(pp)*0.30))
                score = float(np.mean(np.sort(pp)[::-1][:k]))
                thr = float(arts['pthr'].get('overall', arts['pthr'].get('default', 0.5)))
                tampered = score >= thr

        logger.info(f"Inference complete: tampered={tampered}, score={score:.4f}")
        
        return {
            'top3': top3,
            'tamper': float(score),
            'threshold': float(thr),
            'tampered': bool(tampered),
            'patch_support': patch_support
        }
    except Exception as e:
        logger.error(f"Inference error: {e}")
        raise


# ================== AUTHENTICATION ENDPOINTS ==================
@app.route('/api/register', methods=['POST'])
def register():
    """Register new user"""
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('email') or not data.get('password'):
            logger.warning("Register attempt with missing fields")
            return jsonify({'error': 'missing required fields'}), 400
        
        username = data['username'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        
        if len(username) < 3:
            return jsonify({'error': 'username must be at least 3 characters'}), 400
        if len(password) < 6:
            return jsonify({'error': 'password must be at least 6 characters'}), 400
        
        if User.query.filter_by(username=username).first():
            logger.warning(f"Register attempt with duplicate username: {username}")
            return jsonify({'error': 'username already exists'}), 400
        
        if User.query.filter_by(email=email).first():
            logger.warning(f"Register attempt with duplicate email: {email}")
            return jsonify({'error': 'email already registered'}), 400
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"User registered: {username}")
        return jsonify({'message': 'user created successfully', 'user': user.to_dict()}), 201
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Register error: {e}")
        return jsonify({'error': 'registration failed', 'details': str(e)}), 500


@app.route('/api/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'error': 'missing username or password'}), 400
        
        user = User.query.filter_by(username=data['username']).first()
        
        if not user or not user.check_password(data['password']):
            logger.warning(f"Failed login attempt for: {data.get('username')}")
            return jsonify({'error': 'invalid username or password'}), 401
        
        login_user(user)
        logger.info(f"User logged in: {user.username}")
        return jsonify({'message': 'logged in successfully', 'user': user.to_dict()}), 200
    
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'login failed', 'details': str(e)}), 500


@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    """Logout user"""
    try:
        username = current_user.username
        logout_user()
        logger.info(f"User logged out: {username}")
        return jsonify({'message': 'logged out successfully'}), 200
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({'error': 'logout failed', 'details': str(e)}), 500


@app.route('/api/me', methods=['GET'])
@login_required
def get_me():
    """Get current user info"""
    return jsonify(current_user.to_dict()), 200


# ================== ANALYSIS ENDPOINTS ==================
@app.route('/health', methods=['GET'])
@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        arts = load_arts()
        logger.info("Health check performed")
        return jsonify({
            'status': 'ok',
            'model_ready': bool(arts) and not MISSING,
            'missing_artifacts': MISSING,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500


@app.route('/analyze', methods=['POST'])
@app.route('/api/analyze', methods=['POST'])
@login_required
def analyze():
    """Analyze image with full error handling"""
    try:
        arts = load_arts()
        if arts is None:
            logger.error("Analyze called with missing artifacts")
            return jsonify({'error': 'model resources missing', 'missing': MISSING}), 400

        if 'file' not in request.files:
            logger.warning("Analyze call with no file")
            return jsonify({'error': 'no file uploaded'}), 400

        file = request.files['file']
        
        # Validate file
        if file.filename == '':
            logger.warning("Analyze call with empty filename")
            return jsonify({'error': 'no file selected'}), 400
        
        if not file.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.tif', '.tiff')):
            logger.warning(f"Invalid file type: {file.filename}")
            return jsonify({'error': 'unsupported image format. use jpg, png, or tiff'}), 400
        
        # Check file size
        file.seek(0, 2)
        file_length = file.tell()
        file.seek(0)
        
        if file_length > MAX_FILE_SIZE:
            logger.warning(f"File too large: {file_length} bytes")
            return jsonify({'error': f'file too large (max {MAX_FILE_SIZE/1024/1024:.0f} MB)'}), 400

        try:
            img = Image.open(file.stream).convert('RGB')
            img = np.array(img)
            
            if img.ndim == 2:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            else:
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        
        except Exception as e:
            logger.error(f"Image load error: {e}")
            return jsonify({'error': 'invalid image format', 'details': str(e)}), 400

        try:
            result = run_inference(img, arts)
            
            # Save to history
            top_scanner = result['top3'][0][0] if result['top3'] else 'unknown'
            confidence = result['top3'][0][1] if result['top3'] else 0.0
            
            analysis = Analysis(
                user_id=current_user.id,
                filename=file.filename,
                tampered=result['tampered'],
                tamper_score=result['tamper'],
                top_scanner=top_scanner,
                confidence=confidence
            )
            db.session.add(analysis)
            db.session.commit()
            
            logger.info(f"Analysis saved for user {current_user.username}: {file.filename}")
            return jsonify({**result, 'analysis_id': analysis.id}), 200
        
        except Exception as e:
            logger.error(f"Inference error: {e}")
            return jsonify({'error': 'inference failed', 'details': str(e)}), 500

    except Exception as e:
        logger.error(f"Analyze endpoint error: {e}")
        return jsonify({'error': 'analysis failed', 'details': str(e)}), 500


@app.route('/api/test/analyze', methods=['POST'])
def test_analyze():
    """Test analyze endpoint (no authentication required for testing)"""
    try:
        arts = load_arts()
        if arts is None:
            return jsonify({'error': 'model resources missing', 'missing': MISSING}), 400

        if 'file' not in request.files:
            return jsonify({'error': 'no file uploaded'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'no file selected'}), 400
        
        if not file.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.tif', '.tiff')):
            return jsonify({'error': 'unsupported image format. use jpg, png, or tiff'}), 400
        
        file.seek(0, 2)
        file_length = file.tell()
        file.seek(0)
        
        if file_length > MAX_FILE_SIZE:
            return jsonify({'error': f'file too large (max {MAX_FILE_SIZE/1024/1024:.0f} MB)'}), 400

        try:
            img = Image.open(file.stream).convert('RGB')
            img = np.array(img)
            
            if img.ndim == 2:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            else:
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        
        except Exception as e:
            return jsonify({'error': 'invalid image format', 'details': str(e)}), 400

        try:
            result = run_inference(img, arts)
            logger.info(f"Test analysis completed: {file.filename}")
            return jsonify({**result, 'test': True, 'note': 'Test endpoint - no auth required'}), 200
        
        except Exception as e:
            logger.error(f"Test inference error: {e}")
            return jsonify({'error': 'inference failed', 'details': str(e)}), 500

    except Exception as e:
        logger.error(f"Test analyze endpoint error: {e}")
        return jsonify({'error': 'analysis failed', 'details': str(e)}), 500


@app.route('/api/history', methods=['GET'])
@login_required
def get_history():
    """Get user's analysis history"""
    try:
        limit = int(request.args.get('limit', 50))
        analyses = Analysis.query.filter_by(user_id=current_user.id).order_by(
            Analysis.created_at.desc()
        ).limit(limit).all()
        
        return jsonify({
            'count': len(analyses),
            'analyses': [a.to_dict() for a in analyses]
        }), 200
    
    except Exception as e:
        logger.error(f"History fetch error: {e}")
        return jsonify({'error': 'failed to fetch history', 'details': str(e)}), 500


@app.route('/api/analysis/<int:analysis_id>', methods=['GET'])
@login_required
def get_analysis(analysis_id):
    """Get specific analysis result"""
    try:
        analysis = Analysis.query.filter_by(id=analysis_id, user_id=current_user.id).first()
        
        if not analysis:
            return jsonify({'error': 'analysis not found'}), 404
        
        return jsonify(analysis.to_dict()), 200
    
    except Exception as e:
        logger.error(f"Analysis fetch error: {e}")
        return jsonify({'error': 'failed to fetch analysis', 'details': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
@login_required
def get_stats():
    """Get user statistics"""
    try:
        total = Analysis.query.filter_by(user_id=current_user.id).count()
        tampered = Analysis.query.filter_by(user_id=current_user.id, tampered=True).count()
        avg_score = db.session.query(
            db.func.avg(Analysis.tamper_score)
        ).filter_by(user_id=current_user.id).scalar() or 0.0
        
        return jsonify({
            'total_analyses': total,
            'tampered_count': tampered,
            'authentic_count': total - tampered,
            'avg_tamper_score': float(avg_score)
        }), 200
    
    except Exception as e:
        logger.error(f"Stats fetch error: {e}")
        return jsonify({'error': 'failed to fetch stats', 'details': str(e)}), 500


# ================== ERROR HANDLERS ==================
@app.errorhandler(404)
def not_found(error):
    logger.warning(f"404 error: {request.path}")
    return jsonify({'error': 'endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 error: {error}")
    db.session.rollback()
    return jsonify({'error': 'internal server error'}), 500


# ================== DATABASE INITIALIZATION ==================
def init_db():
    """Initialize database"""
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database initialized")
        except Exception as e:
            logger.error(f"Database init error: {e}")


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=False)
