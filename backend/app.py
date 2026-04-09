import os
import datetime
import random
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
@app.route('/')
def home():
    return "TraceFinder Backend is LIVE and UPDATED!"

# CORS Configuration
CORS(app, resources={r"/*": {"origins": "*"}})

# Configuration
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Mock Labels (Since we aren't loading the model to save RAM)
# Replace these with 5 of your actual scanner names for realism
MOCK_SCANNERS = [
    "Canon CanoScan 9000F",
    "HP ScanJet Pro 3000",
    "Epson Perfection V600",
    "Fujitsu ScanSnap iX500",
    "Brother ADS-2700W"
]

@app.route('/')
def home():
    return "TraceFinder Backend is LIVE! (Running in Demo Mode for Free Tier)"

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        # --- SIMULATION LOGIC (No PyTorch needed) ---
        # We simulate the result to save memory on the free tier

        # 1. Pick a random scanner as the main prediction
        predicted_label = random.choice(MOCK_SCANNERS)

        # 2. Generate a realistic confidence (e.g., 96-99%)
        confidence = round(random.uniform(96.5, 99.8), 2)

        # 3. Build Top 5 predictions
        top5_results = []
        remaining = 100.0 - confidence

        # Main prediction
        top5_results.append({"label": predicted_label, "value": confidence})

        # Other predictions
        other_scanners = [s for s in MOCK_SCANNERS if s != predicted_label]
        random.shuffle(other_scanners)

        # Distribute remaining %
        current_rem = remaining
        for i, scanner in enumerate(other_scanners[:4]):
            val = round(random.uniform(0.1, current_rem / 2), 2)
            top5_results.append({"label": scanner, "value": val})
            current_rem -= val

        # Ensure total is 100
        top5_results[-1]['value'] = round(current_rem + top5_results[-1]['value'], 2)

        # 4. Mock Metrics
        metrics = {
            "prnu_quality": round(float(np.random.uniform(0.75, 0.98)), 2),
            "noise_intensity": round(float(np.random.uniform(30, 85)), 2),
            "image_quality_score": round(float(np.random.uniform(80, 99)), 1),
            "metadata_intact": bool(np.random.choice([True, False]))
        }

        result = {
            "id": int(np.random.randint(10000, 99999)),
            "scanner": predicted_label,
            "confidence": confidence,
            "predictions": top5_results,
            "metrics": metrics,
            "artifacts": ["Noise Pattern Extracted", "Deep Feature Analysis", "PRNU Estimation"],
            "filename": filename,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "success"
        }

        # Clean up file
        if os.path.exists(filepath):
            os.remove(filepath)

        return jsonify(result)

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)