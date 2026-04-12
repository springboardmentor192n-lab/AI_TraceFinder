import os
import datetime
import numpy as np
import torch
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from scanner_pipeline import ScannerPipeline

# Initialize Flask App
app = Flask(__name__)

# --- CORS Configuration ---
CORS(app, resources={r"/*": {"origins": "*"}})

# --- Configuration ---
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024  # 20MB limit

# --- Initialize Pipeline ---
PIPELINE = ScannerPipeline(
    model_path="model/deep_scanner_cnn.pth",
    label_map_path="model/label_map_cnn.npy"
)

model = PIPELINE.model
idx_to_label = PIPELINE.idx_to_label

# --- Health Check Route ---
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "TraceFinder Backend is Running",
        "status": "success"
    })

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "model_loaded": model is not None
    })

# --- Prediction Route ---
@app.route("/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if model is None:
        return jsonify({"error": "Model not loaded"}), 500

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    try:
        # --- FIX: Unpack both tensor AND metrics from pipeline ---
        input_tensor, metrics = PIPELINE.extract_residual(filepath)

        # Run inference
        with torch.no_grad():
            outputs = model(input_tensor)
            probs = torch.nn.functional.softmax(outputs, dim=1)
            top5_probs, top5_indices = torch.topk(probs, 5)

        # Prepare predictions
        top5_results = []
        for i in range(5):
            idx = top5_indices[0][i].item()
            prob = top5_probs[0][i].item()
            label = idx_to_label.get(idx, "Unknown Scanner")

            top5_results.append({
                "label": str(label),
                "value": round(prob * 100, 2)
            })

        main_idx = top5_indices[0][0].item()
        main_prob = top5_probs[0][0].item()

        predicted_label = idx_to_label.get(main_idx, "Unknown")
        confidence = round(main_prob * 100, 2)

        # Use the metrics passed from the pipeline (calculated on raw data)
        result = {
            "id": int(np.random.randint(10000, 99999)),
            "scanner": str(predicted_label),
            "confidence": confidence,
            "predictions": top5_results,
            "metrics": metrics, # <--- Use the metrics dict here
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
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)