import os
import datetime
import random
import numpy as np
import torch
import cv2
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from PIL import Image, ExifTags
from scanner_pipeline import ScannerPipeline

# -------------------------------------------------------
# Flask App Initialization
# -------------------------------------------------------
app = Flask(__name__)

# Enable CORS for all origins (Update with frontend URL in production)
CORS(app, resources={r"/*": {"origins": "*"}})

# -------------------------------------------------------
# Configuration
# -------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
MODEL_PATH = os.path.join(BASE_DIR, "model", "deep_scanner_cnn.pth")
LABEL_MAP_PATH = os.path.join(BASE_DIR, "model", "label_map_cnn.npy")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# -------------------------------------------------------
# Initialize Scanner Pipeline
# -------------------------------------------------------
print("🚀 Initializing Scanner Pipeline...")
PIPELINE = ScannerPipeline(
    model_path=MODEL_PATH,
    label_map_path=LABEL_MAP_PATH,
    device="cpu"
)

model = PIPELINE.model
idx_to_label = PIPELINE.idx_to_label
print("✅ Pipeline initialized successfully!")

# -------------------------------------------------------
# Helper Functions for Forensic Metrics
# -------------------------------------------------------
def compute_residual(image_path, img_size=32):
    """Compute noise residual using Gaussian denoising."""
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None

    denoised = cv2.GaussianBlur(img, (5, 5), 0)
    residual = img.astype(np.float32) - denoised.astype(np.float32)
    residual = cv2.resize(residual, (img_size, img_size))
    return residual


def compute_prnu_quality(residual):
    """Estimate PRNU quality using normalized variance."""
    if residual is None:
        return 0.0
    variance = np.var(residual)
    normalized = min(max(variance / 50.0, 0), 1)
    return round(float(normalized), 2)


def compute_noise_intensity(residual):
    """Calculate noise intensity from residual."""
    if residual is None:
        return 0.0
    return round(float(np.std(residual)), 2)


def compute_image_quality(image_path):
    """Estimate image quality using Laplacian variance."""
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return 0.0

    variance = cv2.Laplacian(img, cv2.CV_64F).var()
    score = min(100, variance / 10)
    return round(float(score), 1)


def check_metadata(image_path):
    """Check if metadata exists in the image."""
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        return bool(exif_data)
    except Exception:
        return False


# -------------------------------------------------------
# Health Check Route
# -------------------------------------------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "TraceFinder Backend is Running!",
        "status": "success"
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200


# -------------------------------------------------------
# Prediction Endpoint
# -------------------------------------------------------
@app.route("/predict", methods=["POST"])
def predict():
    if model is None:
        return jsonify({"error": "Model not loaded"}), 500

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    try:
        # -------------------------------------------------------
        # Extract Features Using Pipeline
        # -------------------------------------------------------
        input_tensor = PIPELINE.extract_residual(filepath)

        with torch.no_grad():
            outputs = model(input_tensor)
            probs = torch.nn.functional.softmax(outputs, dim=1)
            top5_probs, top5_indices = torch.topk(probs, 5)

        # -------------------------------------------------------
        # Prepare Predictions
        # -------------------------------------------------------
        top5_results = []
        main_prob = top5_probs[0][0].item()
        main_idx = top5_indices[0][0].item()
        predicted_label = idx_to_label.get(main_idx, "Unknown")

        for i in range(5):
            idx = top5_indices[0][i].item()
            prob = top5_probs[0][i].item()
            label = idx_to_label.get(idx, "Unknown Scanner")

            top5_results.append({
                "label": str(label),
                "value": round(prob * 100, 2)
            })

        confidence = round(main_prob * 100, 2)

        # -------------------------------------------------------
        # Compute Forensic Metrics
        # -------------------------------------------------------
        residual = compute_residual(filepath)

        metrics = {
            "prnu_quality": compute_prnu_quality(residual),
            "noise_intensity": compute_noise_intensity(residual),
            "image_quality_score": compute_image_quality(filepath),
            "metadata_intact": check_metadata(filepath)
        }

        # -------------------------------------------------------
        # Construct Response
        # -------------------------------------------------------
        result = {
            "id": int(np.random.randint(10000, 99999)),
            "scanner": str(predicted_label),
            "confidence": confidence,
            "predictions": top5_results,
            "metrics": metrics,
            "artifacts": [
                "Noise Pattern Extracted",
                "Deep Feature Analysis",
                "PRNU Estimation",
                "Texture Descriptor"
            ],
            "filename": filename,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "success"
        }

        return jsonify(result)

    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"error": str(e)}), 500

    finally:
        # Clean up uploaded file
        if os.path.exists(filepath):
            os.remove(filepath)


# -------------------------------------------------------
# Run Application (Local Development Only)
# -------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)