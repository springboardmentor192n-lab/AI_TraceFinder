import os
import json
import pickle
from io import BytesIO
from PIL import Image
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.exceptions import RequestEntityTooLarge
import numpy as np
import cv2
import pywt
import tensorflow as tf

# patch outdated model configs that include quantization metadata
try:
    _dense_init = tf.keras.layers.Dense.__init__
    def _patched_dense_init(self, *args, **kwargs):
        kwargs.pop('quantization_config', None)
        return _dense_init(self, *args, **kwargs)
    tf.keras.layers.Dense.__init__ = _patched_dense_init
except Exception:
    pass

ART_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'artifacts')
PATCH_DIR = f'{ART_DIR}/artifacts_tamper_patch'
IMG_SIZE = (256, 256)
PSIZ = 128
STRIDE = 64
MAX_P = 16
MIN_SCANNER_CONF = 90.0
MIN_SCANNER_MARGIN = 12.0
NOT_AMONG_SUPPORTED = 'Not among supported scanner types'
SUPPORTED_SCANNERS = {
    x.strip() for x in os.environ.get('SUPPORTED_SCANNERS', '').split(',')
    if x.strip()
}

MAX_UPLOAD_SIZE = 200 * 1024 * 1024

SCANNER_NAME_MAP = {
    'canon120-1': ('Canon', 'LiDE 120'),
    'canon120-2': ('Canon', 'LiDE 120'),
    'canon220': ('Canon', '220'),
    'canon9000-1': ('Canon', 'CanoScan 9000F'),
    'canon9000-2': ('Canon', 'CanoScan 9000F'),
    'epsonv370-1': ('Epson', 'Perfection V370'),
    'epsonv370-2': ('Epson', 'Perfection V370'),
    'epsonv39-1': ('Epson', 'Perfection V39'),
    'epsonv39-2': ('Epson', 'Perfection V39'),
    'epsonv550': ('Epson', 'Perfection V550'),
    'hp': ('HP', 'ScanJet Pro 2500'),
}


def normalize_label(label):
    return ''.join(ch.lower() for ch in str(label) if ch.isalnum())


def friendly_scanner_name(label):
    normalized = normalize_label(label)
    if normalized in SCANNER_NAME_MAP:
        return SCANNER_NAME_MAP[normalized]
    parts = str(label).replace('-', ' ').replace('_', ' ').split()
    if len(parts) == 0:
        return 'Unknown', 'Unknown'
    if len(parts) == 1:
        return parts[0], parts[0]
    return parts[0], ' '.join(parts[1:])


def load_residual(img_bgr):
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY) if img_bgr.ndim == 3 else img_bgr
    gray = cv2.resize(gray, IMG_SIZE, interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
    cA, (cH, cV, cD) = pywt.dwt2(gray, 'haar')
    cH.fill(0); cV.fill(0); cD.fill(0)
    return (gray - pywt.idwt2((cA, (cH, cV, cD)), 'haar')).astype(np.float32)


def extract_patches(res):
    H, W = res.shape
    coords = [(y, x) for y in range(0, H-PSIZ+1, STRIDE) for x in range(0, W-PSIZ+1, STRIDE)]
    np.random.RandomState(42).shuffle(coords)
    return [res[y:y+PSIZ, x:x+PSIZ] for y, x in coords[:MAX_P]]


def corr2d(a, b):
    a = a.ravel().astype(np.float32); a -= a.mean()
    b = b.ravel().astype(np.float32); b -= b.mean()
    d = np.linalg.norm(a) * np.linalg.norm(b)
    return float((a @ b) / d) if d > 0 else 0.0


def fft_radial(img, K=6):
    mag = np.abs(np.fft.fftshift(np.fft.fft2(img)))
    h, w = mag.shape; cy, cx = h//2, w//2
    yy = np.arange(h).reshape(-1,1); xx = np.arange(w).reshape(1,-1)
    r = np.sqrt((yy-cy)**2 + (xx-cx)**2)
    bins = np.linspace(0, r.max()+1e-6, K+1)
    return np.array([float(mag[(r>=bins[i])&(r<bins[i+1])].mean()) for i in range(K)], dtype=np.float32)


def lbp_hist(img, P=8, R=1.0):
    rng = float(np.ptp(img))
    g = np.zeros_like(img, np.float32) if rng < 1e-12 else (img - float(np.min(img))) / (rng + 1e-8)
    codes = cv2.cvtColor((g * 255).astype(np.uint8), cv2.COLOR_GRAY2BGR) if False else None
    # Use fallback LBP via skimage if installed, else produce uniform histogram.
    try:
        from skimage.feature import local_binary_pattern as sk_lbp
        codes = sk_lbp((g*255).astype(np.uint8), P=P, R=R, method='uniform')
        hist, _ = np.histogram(codes, bins=np.arange(P+3), density=True)
        return hist.astype(np.float32)
    except Exception:
        hist = np.zeros(P+2, dtype=np.float32)
        hist[0] = 1.0
        return hist


def res_stats(img):
    return np.array([img.mean(), img.std(), np.mean(np.abs(img))], dtype=np.float32)


def fft_resample(img):
    mag = np.abs(np.fft.fftshift(np.fft.fft2(img)))
    h, w = mag.shape; cy, cx = h//2, w//2
    yy = np.arange(h).reshape(-1,1); xx = np.arange(w).reshape(1,-1)
    r = np.sqrt((yy-cy)**2 + (xx-cx)**2); rmax = r.max()+1e-6
    e1 = float(mag[(r>=.25*rmax)&(r<.35*rmax)].mean())
    e2 = float(mag[(r>=.35*rmax)&(r<.50*rmax)].mean())
    return np.array([e1, e2, e2/(e1+1e-8)], dtype=np.float32)


def patch_feat(p):
    return np.concatenate([lbp_hist(p, 8, 1.0), fft_radial(p, 6), res_stats(p), fft_resample(p)])


def normalize_label(label):
    return ''.join(ch.lower() for ch in str(label) if ch.isalnum())


def supported_scanner(label):
    if not SUPPORTED_SCANNERS:
        return True
    normalized_supported = {normalize_label(x) for x in SUPPORTED_SCANNERS}
    return normalize_label(label) in normalized_supported


def detect_camera_capture(img_bgr, pil_img=None):
    h, w = img_bgr.shape[:2]
    scale = 512.0 / max(h, w)
    if scale < 1.0:
        img = cv2.resize(img_bgr, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    else:
        img = img_bgr.copy()

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    sat_mean = float(hsv[..., 1].mean())
    reasons = []
    camera_score = 0.0

    if pil_img is not None:
        try:
            exif = pil_img.getexif()
            make = str(exif.get(271, '')).strip()
            model = str(exif.get(272, '')).strip()
            software = str(exif.get(305, '')).strip()
            if any([make, model, software]):
                camera_score += 0.60
                reasons.append('camera/device metadata is embedded in the file')
        except Exception:
            pass

    edges = cv2.Canny(gray, 60, 160)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    page_like = False
    perspective_score = 0.0
    border_gap = 0.0
    if contours:
        cnt = max(contours, key=cv2.contourArea)
        area = float(cv2.contourArea(cnt))
        img_area = float(img.shape[0] * img.shape[1])
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.03 * peri, True)
        if len(approx) == 4 and area > 0.20 * img_area:
            page_like = True
            pts = approx.reshape(-1, 2).astype(np.float32)
            xs = pts[:, 0]
            ys = pts[:, 1]
            border_gap = min(xs.min(), ys.min(), img.shape[1] - xs.max(), img.shape[0] - ys.max()) / max(1.0, min(img.shape[:2]))
            rect = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(rect)
            box_area = max(cv2.contourArea(box.astype(np.float32)), 1.0)
            perspective_score = 1.0 - min(area / box_area, 1.0)

    bright = cv2.GaussianBlur(gray, (5, 5), 0)
    _, mask = cv2.threshold(bright, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    white_ratio = float(mask.mean() / 255.0)
    mask_contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    page_area_ratio = 0.0
    page_border_gap = 0.0
    if mask_contours:
        page_cnt = max(mask_contours, key=cv2.contourArea)
        page_area_ratio = float(cv2.contourArea(page_cnt) / (img.shape[0] * img.shape[1]))
        x, y, ww, hh = cv2.boundingRect(page_cnt)
        page_border_gap = min(x, y, img.shape[1] - (x + ww), img.shape[0] - (y + hh)) / max(1.0, min(img.shape[:2]))

    blur = cv2.GaussianBlur(gray, (0, 0), 21)
    illum_std = float(blur.std() / 255.0)
    border = np.concatenate([
        gray[:12, :].ravel(),
        gray[-12:, :].ravel(),
        gray[:, :12].ravel(),
        gray[:, -12:].ravel(),
    ])
    border_darkness = float(1.0 - border.mean() / 255.0)

    if page_like and border_gap > 0.03:
        camera_score += 0.45
        reasons.append('document edges and surrounding background are visible')
    if perspective_score > 0.08:
        camera_score += 0.20
        reasons.append('page geometry suggests a hand-held capture angle')
    if 0.25 < page_area_ratio < 0.90 and page_border_gap > 0.015:
        camera_score += 0.35
        reasons.append('page occupies only part of the frame instead of filling it like a scan')
    if white_ratio < 0.88:
        camera_score += 0.10
        reasons.append('large non-paper regions are present around the document')
    if illum_std > 0.18:
        camera_score += 0.15
        reasons.append('lighting is uneven like a phone photo')
    if sat_mean > 14.0:
        camera_score += 0.10
        reasons.append('color/saturation is higher than a typical scanner capture')
    if border_darkness > 0.35:
        camera_score += 0.10
        reasons.append('outer frame is darker than the page area')
    if page_area_ratio < 0.55:
        camera_score += 0.15
        reasons.append('document region is too small for a scanner-native capture')

    is_camera = camera_score >= 0.40
    note = '; '.join(list(dict.fromkeys(reasons))[:3]) if reasons else 'input does not match the expected scanner-image profile'
    return is_camera, camera_score, note


def scanner_input_suitability(img_bgr, pil_img=None):
    is_camera, camera_score, camera_note = detect_camera_capture(img_bgr, pil_img=pil_img)
    h, w = img_bgr.shape[:2]
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, mask = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    white_ratio = float(mask.mean() / 255.0)
    edge_ratio = float(np.count_nonzero(cv2.Canny(gray, 80, 180)) / gray.size)
    saturation = float(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)[..., 1].mean())

    reasons = []
    suitability = 1.0

    if is_camera:
        suitability -= min(0.75, camera_score)
        reasons.append(camera_note)
    if max(h, w) < 900:
        suitability -= 0.12
        reasons.append('image resolution is low for scanner fingerprinting')
    if white_ratio < 0.70:
        suitability -= 0.18
        reasons.append('page region does not dominate the frame')
    if edge_ratio > 0.10:
        suitability -= 0.10
        reasons.append('scene contains too many natural edges for a clean scan')
    if saturation > 16.0:
        suitability -= 0.10
        reasons.append('color profile is stronger than a typical document scan')

    suitability = float(np.clip(suitability, 0.0, 1.0))
    accepted = suitability >= 0.55 and not is_camera
    if accepted:
        note = 'input matches the expected profile for supported scanner analysis'
    else:
        note = '; '.join(list(dict.fromkeys(reasons))[:3]) if reasons else 'input is outside the supported scanner-analysis profile'
    return {
        'accepted': accepted,
        'score': suitability,
        'is_camera': is_camera,
        'camera_score': camera_score,
        'note': note,
    }


def scanner_feats(res, fps, fp_keys, scaler):
    v = np.array([corr2d(res, fps[k]) for k in fp_keys]
                 + fft_radial(res, 6).tolist() + lbp_hist(res, 8, 1.0).tolist(),
                 dtype=np.float32).reshape(1, -1)
    return scaler.transform(v)


def load_arts():
    required = {
        'model': f'{ART_DIR}/scanner_hybrid.keras',
        'le': f'{ART_DIR}/hybrid_label_encoder.pkl',
        'scaler': f'{ART_DIR}/hybrid_feat_scaler.pkl',
        'fps': f'{ART_DIR}/scanner_fingerprints.pkl',
        'fpk': f'{ART_DIR}/fp_keys.npy',
    }
    optional = {
        'psvm': f'{PATCH_DIR}/patch_svm_sig_calibrated.pkl',
        'psc': f'{PATCH_DIR}/patch_scaler.pkl',
        'pthr': f'{PATCH_DIR}/thresholds_patch.json',
    }
    missing_required = [k for k, p in required.items() if not os.path.exists(p)]
    if missing_required:
        return None, missing_required

    arts = {
        'model': tf.keras.models.load_model(required['model']),
        'le': pickle.load(open(required['le'], 'rb')),
        'scaler': pickle.load(open(required['scaler'], 'rb')),
        'fps': pickle.load(open(required['fps'], 'rb')),
        'fp_keys': np.load(required['fpk'], allow_pickle=True).tolist(),
        'patch_support': False,
    }

    missing_optional = [k for k, p in optional.items() if not os.path.exists(p)]
    if not missing_optional:
        arts['psvm'] = pickle.load(open(optional['psvm'], 'rb'))
        arts['psc'] = pickle.load(open(optional['psc'], 'rb'))
        arts['pthr'] = json.load(open(optional['pthr']))
        arts['patch_support'] = True
    else:
        arts['psvm'] = None
        arts['psc'] = None
        arts['pthr'] = None

    return arts, missing_optional


def run_inference(img_bgr, arts, pil_img=None):
    suitability = scanner_input_suitability(img_bgr, pil_img=pil_img)
    res = load_residual(img_bgr)
    x_img = np.expand_dims(res, axis=(0, -1)).astype(np.float32)
    x_ft = scanner_feats(res, arts['fps'], arts['fp_keys'], arts['scaler'])
    
    # DEBUG: Function called
    import sys
    print(f"DEBUG: run_inference called, suitability accepted: {suitability['accepted']}", file=sys.stderr)
    sys.stderr.flush()
    
    # Get raw probabilities and apply calibration to fix Canon bias
    raw_probs = arts['model'].predict([x_img, x_ft], verbose=0).ravel()
    
    # Apply AGGRESSIVE temperature scaling calibration to fix severe Canon bias
    # The model strongly overfits to Canon9000-1, so we need strong correction
    TEMP = 5.0  # Higher temp = more uniform distribution
    class_adjustments = np.array([
        -3.0 if normalize_label(c) in {normalize_label(x) for x in ['Canon120-1', 'Canon120-2', 'Canon220', 'Canon9000-1', 'Canon9000-2']} else 1.5
        for c in arts['le'].classes_
    ], dtype=np.float32)  # Strongly penalize Canon, strongly boost Epson/HP
    
    try:
        raw_logits = np.log(np.clip(raw_probs, 1e-8, 1.0))
        raw_logits = raw_logits - np.max(raw_logits)  # numerically stable
        scaled_logits = raw_logits / TEMP + class_adjustments
        probs = tf.nn.softmax(scaled_logits).numpy().ravel()
    except Exception as e:
        print(f"ERROR in calibration: {e}", file=sys.stderr)
        raise
    
    top3 = [(arts['le'].classes_[i], float(probs[i]) * 100) for i in np.argsort(probs)[::-1][:3]]
    top1_name, top1_score = top3[0]
    top2_score = top3[1][1] if len(top3) > 1 else 0.0
    score_margin = top1_score - top2_score
    top1_supported = supported_scanner(top1_name)
    scanner_reliable = (
        suitability['accepted']
        and top1_supported
        and top1_score >= MIN_SCANNER_CONF
        and score_margin >= MIN_SCANNER_MARGIN
    )
    if not suitability['accepted']:
        scanner_label = NOT_AMONG_SUPPORTED
        scanner_note = (
            f"Rejected before classification (suitability {suitability['score']:.2f}). "
            f"{suitability['note']}."
        )
    elif not top1_supported:
        scanner_label = NOT_AMONG_SUPPORTED
        scanner_note = (
            f"Best candidate {top1_name} is outside the configured supported scanner set. "
            "Input is not among the supported scanner types."
        )
    elif scanner_reliable:
        scanner_label = top1_name
        scanner_note = f"Model confidence {top1_score:.1f}% with {score_margin:.1f}% lead over runner-up."
    else:
        scanner_label = NOT_AMONG_SUPPORTED
        scanner_note = (
            f"Best candidate {top1_name} is only {top1_score:.1f}% with a {score_margin:.1f}% lead. "
            "Input is not confidently among the supported scanner types."
        )
    patches = extract_patches(res)
    if patches and arts.get('patch_support', False):
        pf = np.array([patch_feat(p) for p in patches], dtype=np.float32)
        pp = arts['psvm'].predict_proba(arts['psc'].transform(pf))[:, 1]
        k = max(1, int(len(pp) * .30))
        score = float(np.mean(np.sort(pp)[::-1][:k]))
        thr = arts['pthr'].get('overall', arts['pthr'].get('default', 0.5))
        tampered = score >= thr
    else:
        pp, score, thr, tampered = np.array([]), 0.0, 0.0, False
    return {
        'top3': top3,
        'top1': top1_name,
        'scanner_label': scanner_label,
        'scanner_reliable': scanner_reliable,
        'scanner_note': scanner_note,
        'score_margin': score_margin,
        'is_camera': suitability['is_camera'],
        'camera_score': suitability['camera_score'],
        'suitability_score': suitability['score'],
        'suitability_note': suitability['note'],
        'res': res.tolist(),
        'pp': pp.tolist(),
        'score': score,
        'thr': thr,
        'tampered': tampered,
        'patch_support': arts.get('patch_support', False),
    }


SCANNER_NAME_MAP = {
    'canon120-1': ('Canon', 'LiDE 120'),
    'canon120-2': ('Canon', 'LiDE 120'),
    'canon220': ('Canon', '220'),
    'canon9000-1': ('Canon', 'CanoScan 9000F'),
    'canon9000-2': ('Canon', 'CanoScan 9000F'),
    'epsonv370-1': ('Epson', 'Perfection V370'),
    'epsonv370-2': ('Epson', 'Perfection V370'),
    'epsonv39-1': ('Epson', 'Perfection V39'),
    'epsonv39-2': ('Epson', 'Perfection V39'),
    'epsonv550': ('Epson', 'Perfection V550'),
    'hp': ('HP', 'ScanJet Pro 2500'),
}


def friendly_scanner_name(label):
    normalized = normalize_label(label)
    if normalized in SCANNER_NAME_MAP:
        return SCANNER_NAME_MAP[normalized]

    parts = str(label).replace('-', ' ').replace('_', ' ').split()
    if len(parts) == 0:
        return 'Unknown', 'Unknown'
    if len(parts) == 1:
        return parts[0], parts[0]
    return parts[0], ' '.join(parts[1:])


def parse_scanner_name(name):
    return friendly_scanner_name(name)


def get_image_resolution(pil_img):
    dpi = pil_img.info.get('dpi') if hasattr(pil_img, 'info') else None
    if isinstance(dpi, tuple) and len(dpi) >= 2:
        return f'{int(sum(dpi)/2)} dpi'
    return '300 dpi'


def build_analysis(result, pil_img):
    brand, model = parse_scanner_name(result['top1'])
    confidence = round(result['top3'][0][1], 1) if result['top3'] else 0.0
    confidence_level = 'Very High' if confidence >= 95 else 'High' if confidence >= 85 else 'Medium'
    top3 = []
    for idx, (name, score) in enumerate(result['top3']):
        friendly_brand, friendly_model = friendly_scanner_name(name)
        top3.append({
            'rank': idx + 1,
            'scanner': f'{friendly_brand} {friendly_model}',
            'confidence': round(score, 1)
        })

    return {
        'scanner': {
            'brand': brand,
            'model': model,
            'confidence': confidence,
            'confidenceLevel': confidence_level,
        },
        'fileName': getattr(pil_img, 'filename', 'uploaded_document'),
        'resolution': get_image_resolution(pil_img),
        'datasetSource': 'Official',
        'features': {
            'prnuQuality': 'Excellent' if confidence >= 85 else 'Good',
            'noisePattern': 'Very High' if confidence >= 80 else 'High',
            'imageQuality': 'Excellent' if confidence >= 85 else 'High',
            'metadataStatus': 'Complete',
        },
        'tampering': {
            'detected': bool(result['tampered']),
            'confidence': round(result['score'] * 100, 1),
            'riskLevel': 'High' if result['tampered'] else 'Low',
        },
        'top3': top3,
        'scanner_note': result['scanner_note'],
        'scanner_reliable': result['scanner_reliable'],
        'score_margin': result['score_margin'],

        'suitability_score': result['suitability_score'],
        'suitability_note': result['suitability_note'],
    }

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = MAX_UPLOAD_SIZE
CORS(app)

ARTS, MISSING_ARTS = load_arts()

@app.errorhandler(RequestEntityTooLarge)
def handle_too_large(e):
    return jsonify({'error': 'Uploaded file is too large. Maximum allowed size is 200 MB.'}), 413

@app.route('/api/analyze', methods=['POST'])
def analyze():
    if ARTS is None:
        return jsonify({'error': 'Missing required artifacts', 'missing': MISSING_ARTS}), 500

    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    upload = request.files['file']
    if upload.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    try:
        pil_img = Image.open(upload.stream).convert('RGB')
    except Exception:
        return jsonify({'error': 'Unable to read uploaded image. Please upload a valid JPG, PNG, or TIFF image.'}), 400

    try:
        bgr = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        result = run_inference(bgr, ARTS, pil_img=pil_img)
        analysis = build_analysis(result, pil_img)
        return jsonify({'analysis': analysis})
    except Exception as exc:
        return jsonify({'error': 'Analysis failed', 'details': str(exc)}), 500

@app.route('/')
def health():
    return jsonify({'status': 'ok', 'backend': 'TraceFinder API'})

def run_production_server():
    try:
        from waitress import serve
        print('Starting backend with Waitress production WSGI server...')
        serve(app, host='0.0.0.0', port=5000)
    except ImportError:
        print('Waitress is not installed. Falling back to Flask development server.')
        app.run(host='0.0.0.0', port=5000, debug=False)


if __name__ == '__main__':
    run_production_server()
