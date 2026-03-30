"""
AI TraceFinder Backend - Flask Application v2
Machine Learning-based Scanner Source Identification System
Supports V2 hybrid ensemble model with multi-scale features
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import time
from werkzeug.utils import secure_filename
import numpy as np
import cv2
import joblib
from image_forensics import ImageForensics
import traceback
import atexit
import glob
from datetime import datetime, timedelta
import json
from pathlib import Path

# Get absolute paths for static and template folders
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_FOLDER = os.path.join(BASE_DIR, 'frontend', 'static')
TEMPLATE_FOLDER = os.path.join(BASE_DIR, 'frontend', 'templates')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'backend', 'uploads')

# Initialize Flask app with absolute paths
app = Flask(__name__, static_folder=STATIC_FOLDER, template_folder=TEMPLATE_FOLDER)
CORS(app)

# Configuration
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'tif', 'tiff', 'bmp'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
FILE_CLEANUP_HOURS = 24  # Clean up files older than 24 hours

# Create upload folder if not exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Initialize Image Forensics Engine (for fallback features)
forensics_engine = ImageForensics()

# History storage file
HISTORY_FILE = os.path.join(BASE_DIR, 'backend', 'analysis_history.json')

def load_history():
    """Load analysis history from file"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_history(history):
    """Save analysis history to file"""
    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2, default=str)
    except Exception as e:
        print(f"Error saving history: {e}")

def add_to_history(filename, scanner_id, confidence, image_info):
    """Add analysis result to history"""
    try:
        history = load_history()
        history.insert(0, {
            'timestamp': datetime.now().isoformat(),
            'filename': filename,
            'scanner_id': scanner_id,
            'confidence': float(confidence),
            'dimensions': image_info.get('shape', []),
            'status': 'success'
        })
        # Keep only last 100 analyses
        history = history[:100]
        save_history(history)
    except Exception as e:
        print(f"Error adding to history: {e}")

# ============================================
# ML Model Loading (V2 with fallback to V1)
# ============================================
MODEL_PATH_V2 = os.path.join(os.path.dirname(__file__), "scanner_model_v2.pkl")
SCALER_PATH_V2 = os.path.join(os.path.dirname(__file__), "feature_scaler_v2.pkl")
CLASSES_MAPPING_PATH_V2 = os.path.join(os.path.dirname(__file__), "classes_mapping_v2.pkl")
MODEL_PATH = os.path.join(os.path.dirname(__file__), "scanner_model.pkl")
CLASSES_MAPPING_PATH = os.path.join(os.path.dirname(__file__), "classes_mapping.pkl")

ml_model = None
ml_scaler = None
classes_mapping = None
model_enabled = False
model_version = None  # 'v1' or 'v2'

def load_ml_model():
    """Load trained ML model and classes mapping on startup. Tries V2 first, then V1."""
    global ml_model, ml_scaler, classes_mapping, model_enabled, model_version
    
    # Try V2 model first
    try:
        if (os.path.exists(MODEL_PATH_V2) and
            os.path.exists(SCALER_PATH_V2) and
            os.path.exists(CLASSES_MAPPING_PATH_V2)):
            ml_model = joblib.load(MODEL_PATH_V2)
            ml_scaler = joblib.load(SCALER_PATH_V2)
            classes_mapping = joblib.load(CLASSES_MAPPING_PATH_V2)
            model_enabled = True
            model_version = 'v2'
            print(f"✓ ML Model V2 (Hybrid Ensemble) loaded successfully")
            print(f"✓ Classes: {list(classes_mapping.values())}")
            return
    except Exception as e:
        print(f"⚠️  V2 model load failed: {str(e)}")
    
    # Fallback to V1
    try:
        if os.path.exists(MODEL_PATH) and os.path.exists(CLASSES_MAPPING_PATH):
            ml_model = joblib.load(MODEL_PATH)
            classes_mapping = joblib.load(CLASSES_MAPPING_PATH)
            model_enabled = True
            model_version = 'v1'
            print(f"✓ ML Model V1 (RandomForest) loaded successfully")
            print(f"✓ Classes: {list(classes_mapping.values())}")
        else:
            print(f"⚠️  No ML Model found. Using rule-based forensics engine.")
            print(f"   To train: python backend/train_model_v2.py")
            model_enabled = False
    except Exception as e:
        print(f"⚠️  Failed to load ML model: {str(e)}")
        print(f"   Using rule-based forensics engine instead.")
        model_enabled = False

# Load model on startup
load_ml_model()


def cleanup_old_files():
    """
    Clean up uploaded files older than FILE_CLEANUP_HOURS
    Prevents disk space issues from accumulated uploads
    """
    try:
        cutoff_time = datetime.now() - timedelta(hours=FILE_CLEANUP_HOURS)
        for filepath in glob.glob(os.path.join(UPLOAD_FOLDER, '*')):
            if os.path.isfile(filepath):
                file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                if file_time < cutoff_time:
                    os.remove(filepath)
    except Exception as e:
        app.logger.warning(f"Cleanup error: {str(e)}")

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess_image_for_ml(image_path):
    """
    Preprocess image for ML model prediction.
    For V2: extracts multi-scale features using train_model_v2 pipeline.
    For V1: simple grayscale flatten.
    
    Returns:
        features: 1D array ready for ML model, or None on failure
    """
    try:
        if model_version == 'v2':
            # Use V2 multi-scale feature extraction
            try:
                from train_model_v2 import extract_all_features
                features = extract_all_features(image_path)
                return features
            except ImportError:
                print("⚠️  V2 feature extractor not available, using V1")
        
        # V1 fallback: simple grayscale flatten
        image = cv2.imread(image_path)
        if image is None:
            return None
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, (128, 128), interpolation=cv2.INTER_AREA)
        flattened = resized.flatten().astype(np.float32) / 255.0
        
        return flattened
    except Exception as e:
        print(f"Error preprocessing image: {str(e)}")
        return None

def compute_feature_confidences(image_path):
    """
    Compute per-feature confidence scores for the frontend gauge display.
    Returns breakdown of PRNU, FFT, Texture confidence scores.
    """
    try:
        image = cv2.imread(image_path)
        if image is None:
            return {}
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, (128, 128), interpolation=cv2.INTER_AREA)
        norm = resized.astype(np.float32) / 255.0
        
        from scipy.signal import wiener as wiener_filter
        from scipy import ndimage as ndi
        from scipy.fft import fft2 as fft2_func, fftshift as fftshift_func
        
        # PRNU confidence: based on residual noise consistency
        try:
            denoised = wiener_filter(norm, mysize=(5, 5))
        except Exception:
            denoised = cv2.GaussianBlur(norm, (5, 5), 0)
        residual = norm - denoised
        prnu_std = float(np.std(residual))
        prnu_conf = min(1.0, max(0.3, 1.0 - abs(prnu_std - 0.05) / 0.15))
        
        # FFT confidence: based on spectral energy concentration
        fft_img = np.abs(fft2_func(norm))
        fft_img = fftshift_func(fft_img)
        total_energy = np.sum(fft_img)
        top_energy = np.sum(fft_img[fft_img > np.percentile(fft_img, 90)])
        fft_ratio = float(top_energy / (total_energy + 1e-8))
        fft_conf = min(1.0, max(0.3, fft_ratio * 2.5))
        
        # Texture confidence: based on edge coherence
        grad_x = ndi.sobel(norm, axis=1)
        grad_y = ndi.sobel(norm, axis=0)
        grad_mag = np.sqrt(grad_x**2 + grad_y**2)
        edge_coherence = 1.0 - float(np.std(grad_mag) / (np.mean(grad_mag) + 1e-8))
        texture_conf = min(1.0, max(0.3, edge_coherence))
        
        return {
            'prnu_confidence': round(prnu_conf, 3),
            'fft_confidence': round(fft_conf, 3),
            'texture_confidence': round(texture_conf, 3),
            'prnu_strength': round(prnu_std, 5),
            'fft_energy_ratio': round(fft_ratio, 5),
            'edge_coherence': round(float(edge_coherence), 5),
        }
    except Exception as e:
        print(f"Feature confidence error: {e}")
        return {}


@app.route('/')
def index():
    """Serve main page"""
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'AI TraceFinder Backend is running',
        'version': '2.0.0',
        'model_version': model_version or 'forensics-only',
        'model_enabled': model_enabled,
    }), 200

@app.route('/api/analyze', methods=['POST'])
def analyze_image():
    """
    Main analysis endpoint - Uses ML Model for classification
    Analyzes uploaded image and returns class prediction and confidence
    """
    try:
        # Check if file is provided
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': f'File type not allowed. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Check if ML model is available
        if model_enabled and ml_model is not None and classes_mapping is not None:
            try:
                t_start = time.time()
                
                # Preprocess image for ML model
                preprocessed = preprocess_image_for_ml(filepath)
                
                if preprocessed is None:
                    return jsonify({
                        'success': False,
                        'error': 'Could not process image file'
                    }), 400
                
                # Apply scaler for V2 model
                if model_version == 'v2' and ml_scaler is not None:
                    preprocessed_scaled = ml_scaler.transform([preprocessed])[0]
                else:
                    preprocessed_scaled = preprocessed
                
                # Get prediction from ML model
                prediction = ml_model.predict([preprocessed_scaled])[0]
                probabilities = ml_model.predict_proba([preprocessed_scaled])[0]
                
                # Get predicted class name
                predicted_class = classes_mapping[prediction]
                
                # Calculate confidence as the max probability
                confidence = float(np.max(probabilities))
                
                # Compute per-feature confidence breakdown
                feature_confidences = compute_feature_confidences(filepath)
                
                t_elapsed = time.time() - t_start
                
                # Save to history
                add_to_history(filename, predicted_class, confidence, {'shape': [128, 128]})
                
                return jsonify({
                    'success': True,
                    'data': {
                        'scanner_id': predicted_class,
                        'confidence': confidence,
                        'model_version': model_version or 'v1',
                        'inference_time_ms': round(t_elapsed * 1000, 1),
                        'feature_confidences': feature_confidences,
                        'noise_pattern_strength': feature_confidences.get('prnu_strength', 0.0),
                        'image_info': {
                            'shape': [128, 128],
                            'dtype': 'float32',
                            'prediction_probabilities': {
                                classes_mapping[i]: float(probabilities[i])
                                for i in range(len(probabilities))
                            }
                        },
                        'fft_analysis': {
                            'energy_concentration': feature_confidences.get('fft_energy_ratio', 0.0),
                        },
                        'texture_metrics': {
                            'edge_strength': feature_confidences.get('edge_coherence', 0.0),
                        },
                        'forensic_indicators': {},
                        'recommendations': []
                    }
                }), 200
                
            except Exception as e:
                print(f"ML Model prediction error: {str(e)}")
                print(f"Falling back to forensics engine")
                # Fall back to forensics engine if ML prediction fails
                use_ml = False
        else:
            use_ml = False
        
        # Fallback to forensics engine if ML model is not available
        if not model_enabled or not use_ml:
            results = forensics_engine.analyze_image(filepath)
            
            if results['success']:
                # Ensure all values are JSON serializable (convert numpy types)
                def convert_to_native(obj):
                    """Convert numpy types to native Python types"""
                    if isinstance(obj, np.ndarray):
                        return obj.tolist()
                    elif isinstance(obj, (np.integer, np.floating)):
                        return float(obj) if isinstance(obj, np.floating) else int(obj)
                    elif isinstance(obj, np.bool_):
                        return bool(obj)
                    elif isinstance(obj, dict):
                        return {k: convert_to_native(v) for k, v in obj.items()}
                    elif isinstance(obj, (list, tuple)):
                        return [convert_to_native(v) for v in obj]
                    return obj
                
                # Save to history
                add_to_history(filename, results['scanner_id'], results['confidence'], results.get('image_info', {}))
                
                return jsonify({
                    'success': True,
                    'data': {
                        'scanner_id': results['scanner_id'],
                        'confidence': float(results['confidence']),
                        'feature_vector': results['feature_vector'].tolist() if isinstance(results.get('feature_vector'), np.ndarray) else [],
                        'noise_pattern_strength': float(results.get('noise_pattern_strength', 0)),
                        'image_info': convert_to_native(results.get('image_info', {})),
                        'fft_analysis': convert_to_native(results.get('fft_analysis', {})),
                        'texture_metrics': convert_to_native(results.get('texture_metrics', {})),
                        'forensic_indicators': convert_to_native(results.get('forensic_indicators', {})),
                        'recommendations': results.get('recommendations', [])
                    }
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': results.get('error', 'Unknown error during analysis')
                }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}',
            'details': traceback.format_exc()
        }), 500

@app.route('/api/batch-analyze', methods=['POST'])
def batch_analyze():
    """
    Batch analysis endpoint - Uses ML Model for classification
    Analyzes multiple images at once
    """
    try:
        if 'images' not in request.files:
            return jsonify({'error': 'No images provided'}), 400
        
        files = request.files.getlist('images')
        results = []
        
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                # Try ML model first
                if model_enabled and ml_model is not None and classes_mapping is not None:
                    try:
                        preprocessed = preprocess_image_for_ml(filepath)
                        if preprocessed is not None:
                            prediction = ml_model.predict([preprocessed])[0]
                            probabilities = ml_model.predict_proba([preprocessed])[0]
                            predicted_class = classes_mapping[prediction]
                            confidence = float(np.max(probabilities))
                            
                            results.append({
                                'filename': filename,
                                'success': True,
                                'scanner_id': predicted_class,
                                'confidence': confidence
                            })
                            continue
                    except Exception as e:
                        print(f"ML Model error for {filename}: {str(e)}")
                
                # Fallback to forensics engine
                result = forensics_engine.analyze_image(filepath)
                results.append({
                    'filename': filename,
                    'success': result['success'],
                    'scanner_id': result.get('scanner_id', 'Unknown'),
                    'confidence': float(result.get('confidence', 0))
                })
        
        return jsonify({
            'success': True,
            'total': len(results),
            'analyzed': len([r for r in results if r['success']]),
            'results': results
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Batch analysis error: {str(e)}'
        }), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get system statistics and scanner database info"""
    try:
        stats = forensics_engine.get_statistics()
        return jsonify({
            'success': True,
            'statistics': stats
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/extractors', methods=['GET'])
def get_extractors():
    """Get available feature extractors information"""
    extractors = {
        'PRNU': 'Photo Response Non-Uniformity - Camera noise pattern analysis',
        'FFT': 'Fast Fourier Transform - Frequency domain analysis',
        'LBP': 'Local Binary Pattern - Texture feature extraction',
        'Wavelet': 'Wavelet decomposition - Multi-scale analysis',
        'Statistical': 'Statistical moments and distributions',
        'Gradient': 'Edge and gradient information',
        'DCT': 'Discrete Cosine Transform - JPEG artifacts'
    }
    return jsonify({'extractors': extractors}), 200

@app.route('/api/docs', methods=['GET'])
def get_docs():
    """Get API documentation - Returns JSON for programmatic access"""
    docs = {
        'title': 'AI TraceFinder API Documentation',
        'version': '1.0.0',
        'endpoints': [
            {
                'path': '/api/health',
                'method': 'GET',
                'description': 'Health check endpoint',
                'response': {'status': 'healthy', 'message': 'AI TraceFinder Backend is running', 'version': '1.0.0'}
            },
            {
                'path': '/api/analyze',
                'method': 'POST',
                'description': 'Analyze single image and get scanner identification',
                'parameters': {'image': 'binary file (jpg, png, tif, bmp, etc.)'},
                'response': {'success': True, 'data': {'scanner_id': 'string', 'confidence': 'float', 'forensic_indicators': {}}}
            },
            {
                'path': '/api/batch-analyze',
                'method': 'POST',
                'description': 'Analyze multiple images at once (up to 10)',
                'parameters': {'images': 'multiple binary files'},
                'response': {'success': True, 'total': 'int', 'analyzed': 'int', 'results': []}
            },
            {
                'path': '/api/statistics',
                'method': 'GET',
                'description': 'Get system statistics and scanner database info',
                'response': {'success': True, 'statistics': {}}
            },
            {
                'path': '/api/extractors',
                'method': 'GET',
                'description': 'Get available feature extractors list',
                'response': {'extractors': {}}
            }
        ]
    }
    return jsonify(docs), 200

@app.route('/api/docs-html', methods=['GET'])
def get_docs_html():
    """Get API documentation as HTML for browser viewing"""
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI TraceFinder - API Documentation</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                color: #e2e8f0;
                line-height: 1.6;
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 1000px;
                margin: 0 auto;
                background: rgba(30, 41, 59, 0.8);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(100, 116, 139, 0.3);
                border-radius: 12px;
                padding: 40px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            }
            header {
                margin-bottom: 40px;
                border-bottom: 2px solid rgba(37, 99, 235, 0.3);
                padding-bottom: 20px;
            }
            h1 {
                font-size: 2.5em;
                color: #3b82f6;
                margin-bottom: 10px;
            }
            .version {
                color: #94a3b8;
                font-size: 0.95em;
            }
            .endpoints {
                display: grid;
                gap: 20px;
            }
            .endpoint {
                background: rgba(15, 23, 42, 0.6);
                border-left: 4px solid #3b82f6;
                border-radius: 8px;
                padding: 20px;
                transition: all 0.3s ease;
            }
            .endpoint:hover {
                background: rgba(15, 23, 42, 0.9);
                border-left-color: #7c3aed;
                box-shadow: 0 4px 12px rgba(124, 58, 237, 0.2);
            }
            .method {
                display: inline-block;
                padding: 4px 12px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 0.85em;
                margin-right: 10px;
                margin-bottom: 10px;
            }
            .method.get {
                background: rgba(16, 185, 129, 0.2);
                color: #10b981;
            }
            .method.post {
                background: rgba(37, 99, 235, 0.2);
                color: #3b82f6;
            }
            .path {
                font-family: 'Courier New', monospace;
                background: rgba(0, 0, 0, 0.3);
                padding: 8px 12px;
                border-radius: 4px;
                color: #60a5fa;
                font-weight: 600;
                margin-bottom: 10px;
                display: inline-block;
            }
            .description {
                color: #cbd5e1;
                margin-bottom: 15px;
                font-size: 0.95em;
            }
            .details {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
                margin-top: 15px;
            }
            .detail-box {
                background: rgba(0, 0, 0, 0.2);
                padding: 12px;
                border-radius: 6px;
                border-left: 3px solid #7c3aed;
            }
            .detail-label {
                color: #7c3aed;
                font-weight: 600;
                font-size: 0.85em;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-bottom: 5px;
            }
            .detail-value {
                color: #e2e8f0;
                font-family: 'Courier New', monospace;
                font-size: 0.9em;
                word-break: break-all;
            }
            .parameters {
                background: rgba(37, 99, 235, 0.1);
                padding: 12px;
                border-radius: 6px;
                border-left: 3px solid #3b82f6;
                margin-top: 10px;
            }
            .param-item {
                color: #cbd5e1;
                font-family: 'Courier New', monospace;
                font-size: 0.9em;
                margin: 5px 0;
            }
            .param-key {
                color: #60a5fa;
                font-weight: 600;
            }
            .footer {
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid rgba(100, 116, 139, 0.2);
                text-align: center;
                color: #94a3b8;
                font-size: 0.9em;
            }
            .examples {
                background: rgba(0, 0, 0, 0.3);
                padding: 15px;
                border-radius: 6px;
                margin-top: 15px;
                border-left: 3px solid #06b6d4;
            }
            .example-title {
                color: #06b6d4;
                font-weight: 600;
                margin-bottom: 10px;
            }
            .example-code {
                background: rgba(0, 0, 0, 0.5);
                padding: 10px;
                border-radius: 4px;
                color: #10b981;
                font-family: 'Courier New', monospace;
                font-size: 0.85em;
                overflow-x: auto;
                white-space: pre-wrap;
                word-wrap: break-word;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>🔍 AI TraceFinder API Documentation</h1>
                <p class="version">Version 1.0.0 | Scanner Identification & Image Forensics</p>
            </header>

            <div class="endpoints">
                <div class="endpoint">
                    <div style="margin-bottom: 10px;">
                        <span class="method get">GET</span>
                        <span class="path">/api/health</span>
                    </div>
                    <div class="description">Health check endpoint - Verify server is running</div>
                    <div class="examples">
                        <div class="example-title">Example Response:</div>
                        <div class="example-code">{"status": "healthy", "message": "AI TraceFinder Backend is running", "version": "1.0.0"}</div>
                    </div>
                </div>

                <div class="endpoint">
                    <div style="margin-bottom: 10px;">
                        <span class="method post">POST</span>
                        <span class="path">/api/analyze</span>
                    </div>
                    <div class="description">Analyze single image and identify source scanner</div>
                    <div class="parameters">
                        <div class="detail-label">Parameters:</div>
                        <div class="param-item"><span class="param-key">image</span> - Binary file (jpg, png, tif, bmp, etc.) - Required</div>
                    </div>
                    <div class="examples">
                        <div class="example-title">Example Usage:</div>
                        <div class="example-code">curl -X POST -F "image=@photo.jpg" http://localhost:5000/api/analyze</div>
                    </div>
                    <div class="examples">
                        <div class="example-title">Response:</div>
                        <div class="example-code">{"success": true, "data": {"scanner_id": "Epson_Scanner", "confidence": 92.5, "forensic_indicators": {...}}}</div>
                    </div>
                </div>

                <div class="endpoint">
                    <div style="margin-bottom: 10px;">
                        <span class="method post">POST</span>
                        <span class="path">/api/batch-analyze</span>
                    </div>
                    <div class="description">Analyze multiple images at once (up to 10 images)</div>
                    <div class="parameters">
                        <div class="detail-label">Parameters:</div>
                        <div class="param-item"><span class="param-key">images</span> - Multiple binary files - Required</div>
                    </div>
                    <div class="examples">
                        <div class="example-title">Example Usage:</div>
                        <div class="example-code">curl -X POST -F "images=@photo1.jpg" -F "images=@photo2.jpg" http://localhost:5000/api/batch-analyze</div>
                    </div>
                    <div class="examples">
                        <div class="example-title">Response:</div>
                        <div class="example-code">{"success": true, "total": 2, "analyzed": 2, "results": [...]}</div>
                    </div>
                </div>

                <div class="endpoint">
                    <div style="margin-bottom: 10px;">
                        <span class="method get">GET</span>
                        <span class="path">/api/statistics</span>
                    </div>
                    <div class="description">Get system statistics and scanner database information</div>
                    <div class="examples">
                        <div class="example-title">Example Response:</div>
                        <div class="example-code">{"success": true, "statistics": {"total_analyzed": 5, "successful": 5, "failed": 0, ...}}</div>
                    </div>
                </div>

                <div class="endpoint">
                    <div style="margin-bottom: 10px;">
                        <span class="method get">GET</span>
                        <span class="path">/api/extractors</span>
                    </div>
                    <div class="description">Get list of available feature extractors</div>
                    <div class="examples">
                        <div class="example-title">Example Response:</div>
                        <div class="example-code">{"extractors": {"PRNU": "Photo Response Non-Uniformity", "FFT": "Fast Fourier Transform", ...}}</div>
                    </div>
                </div>
            </div>

            <div class="footer">
                <p>🎯 AI TraceFinder v1.0.0 | Image Forensics & Scanner Identification | © 2026</p>
                <p style="margin-top: 10px; font-size: 0.85em;">For JSON API documentation, visit <code>/api/docs</code></p>
            </div>
        </div>
    </body>
    </html>
    """
    return html, 200

@app.route('/api/history', methods=['GET'])
def get_analysis_history():
    """Get analysis history"""
    try:
        history = load_history()
        
        # Filter by scanner if provided
        scanner_filter = request.args.get('scanner', '')
        if scanner_filter:
            history = [h for h in history if h.get('scanner_id') == scanner_filter]
        
        # Sort
        sort_by = request.args.get('sort', 'latest')
        if sort_by == 'confidence':
            history = sorted(history, key=lambda x: x.get('confidence', 0), reverse=True)
        elif sort_by == 'oldest':
            history = sorted(history, key=lambda x: x.get('timestamp', ''), reverse=False)
        
        return jsonify({'success': True, 'history': history}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/history', methods=['DELETE'])
def clear_history():
    """Clear analysis history"""
    try:
        save_history([])
        return jsonify({'success': True, 'message': 'History cleared'}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/report', methods=['POST'])
def generate_report():
    """Generate analysis report in HTML format"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        scanner_id = data.get('scanner_id', 'Unknown')
        confidence = data.get('confidence', 0)
        image_info = data.get('image_info', {})
        forensic_indicators = data.get('forensic_indicators', {})
        fft_analysis = data.get('fft_analysis', {})
        texture_metrics = data.get('texture_metrics', {})
        
        # Generate HTML report
        report_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>AI TraceFinder - Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #1a1a2e; color: #eee; }}
                .header {{ background-color: #16213e; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
                .section {{ background-color: #0f3460; padding: 15px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #e94560; }}
                .metric {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 10px 0; }}
                .metric-item {{ background-color: #16213e; padding: 10px; border-radius: 5px; }}
                .label {{ color: #888; font-size: 0.9em; }}
                .value {{ color: #00d4ff; font-weight: bold; font-size: 1.2em; margin-top: 5px; }}
                .confidence-bar {{ background-color: #333; width: 100%; height: 20px; border-radius: 10px; overflow: hidden; }}
                .confidence-fill {{ background-color: #00d4ff; height: 100%; width: {confidence}%; transition: width 0.3s; }}
                h2 {{ color: #00d4ff; border-bottom: 2px solid #e94560; padding-bottom: 10px; }}
                .timestamp {{ font-size: 0.9em; color: #888; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔬 AI TraceFinder - Analysis Report</h1>
                <p class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>

            <div class="section">
                <h2>Scanner Identification</h2>
                <div class="metric">
                    <div class="metric-item">
                        <div class="label">Identified Scanner</div>
                        <div class="value">{scanner_id}</div>
                    </div>
                    <div class="metric-item">
                        <div class="label">Confidence Score</div>
                        <div class="value">{confidence:.2f}%</div>
                    </div>
                </div>
                <div class="confidence-bar">
                    <div class="confidence-fill"></div>
                </div>
            </div>

            <div class="section">
                <h2>Image Information</h2>
                <div class="metric">
                    <div class="metric-item">
                        <div class="label">Dimensions</div>
                        <div class="value">{str(image_info.get('shape', [0, 0]))}</div>
                    </div>
                    <div class="metric-item">
                        <div class="label">Data Type</div>
                        <div class="value">{image_info.get('dtype', 'Unknown')}</div>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>Forensic Indicators</h2>
                <div class="metric">
                    <div class="metric-item">
                        <div class="label">Compression Artifacts</div>
                        <div class="value">{forensic_indicators.get('compression_artifacts', 'N/A')}</div>
                    </div>
                    <div class="metric-item">
                        <div class="label">Tampering Detected</div>
                        <div class="value">{forensic_indicators.get('potential_tampering', 'No')}</div>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>FFT Analysis</h2>
                <div class="metric">
                    <div class="metric-item">
                        <div class="label">Mean Magnitude</div>
                        <div class="value">{fft_analysis.get('mean_magnitude', 'N/A')}</div>
                    </div>
                    <div class="metric-item">
                        <div class="label">Peak Frequency Ratio</div>
                        <div class="value">{fft_analysis.get('peak_frequency_ratio', 'N/A')}</div>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>Texture Metrics</h2>
                <div class="metric">
                    <div class="metric-item">
                        <div class="label">Mean Texture</div>
                        <div class="value">{texture_metrics.get('mean', 'N/A')}</div>
                    </div>
                    <div class="metric-item">
                        <div class="label">Noise Level</div>
                        <div class="value">{texture_metrics.get('std', 'N/A')}</div>
                    </div>
                </div>
            </div>

            <div class="footer" style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #333; text-align: center; color: #888;">
                <p>🔍 AI TraceFinder v1.0.0 | Advanced Image Forensics & Scanner Identification</p>
                <p>© 2026 | Report generated automatically</p>
            </div>
        </body>
        </html>
        """
        
        return report_html, 200, {'Content-Type': 'text/html'}
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/compare', methods=['POST'])
def compare_analyses():
    """Compare multiple analysis results"""
    try:
        data = request.get_json()
        analysis_indices = data.get('indices', [])
        
        history = load_history()
        
        # Get specified analyses
        comparisons = []
        for idx in analysis_indices:
            if 0 <= idx < len(history):
                comparisons.append(history[idx])
        
        if not comparisons:
            return jsonify({'success': False, 'error': 'No analyses found'}), 400
        
        # Calculate comparison summary
        scanners = [c.get('scanner_id') for c in comparisons]
        confidences = [c.get('confidence', 0) for c in comparisons]
        
        summary = {
            'total_compared': len(comparisons),
            'scanner_models': scanners,
            'average_confidence': float(np.mean(confidences)) if confidences else 0,
            'confidence_range': f"{min(confidences):.2f} - {max(confidences):.2f}" if confidences else "N/A",
            'same_scanner': len(set(scanners)) == 1
        }
        
        return jsonify({
            'success': True,
            'comparisons': comparisons,
            'summary': summary
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Register cleanup function to run on exit
    atexit.register(cleanup_old_files)
    
    print("\n" + "="*60)
    print("AI TraceFinder - Backend Server Starting")
    print("="*60)
    print(f"Upload Folder: {UPLOAD_FOLDER}")
    print(f"Auto-cleanup: Files older than {FILE_CLEANUP_HOURS} hours")
    print("Flask Server: http://localhost:5000")
    print("API Documentation: http://localhost:5000/api/docs")
    print("="*60 + "\n")
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
