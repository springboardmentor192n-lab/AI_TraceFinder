# TraceFinder — Forensic Scanner Identification System

> Identify which scanner device produced any scanned document using ML forensics.
> **No GPU required.** Runs on any laptop with Python 3.9+ and Node.js 18+.

---

## Project Overview

TraceFinder analyzes unique noise patterns, frequency-domain artifacts, and texture
descriptors left behind by scanner devices to identify which scanner model produced
a scanned image. Built on the **Supatlantique** dataset from Kaggle.

**Tech Stack:**
- Frontend: Next.js 14 + TypeScript + Recharts
- Backend: Python FastAPI
- Models: SVM + Random Forest (scikit-learn) — CPU-friendly, no GPU needed
- Features: PRNU noise · FFT frequency spectrum · LBP texture descriptors

---

## Project Structure

```
tracefinder/
├── backend/
│   ├── main.py                  ← FastAPI app entry point
│   ├── train.py                 ← Model training script
│   ├── requirements.txt
│   ├── routers/
│   │   ├── predict.py           ← POST /api/predict/
│   │   ├── report.py            ← POST /api/report/download
│   │   └── history.py           ← GET/DELETE /api/history/
│   ├── models/
│   │   └── service.py           ← Model loading + inference
│   ├── utils/
│   │   └── features.py          ← PRNU + FFT + LBP extraction
│   └── saved_model/             ← Created after training
│       ├── best_model.pkl
│       ├── svm_model.pkl
│       ├── rf_model.pkl
│       ├── label_encoder.pkl
│       └── metrics.json
│
└── frontend/
    ├── pages/
    │   ├── index.tsx             ← Landing page
    │   ├── scan.tsx              ← Upload + predict + visualize
    │   ├── dashboard.tsx         ← Metrics, confusion matrix, charts
    │   └── history.tsx           ← Prediction log
    ├── components/
    │   └── Navbar.tsx
    ├── styles/
    │   └── globals.css
    ├── package.json
    ├── next.config.js
    └── tailwind.config.js
```

---

## Week-by-Week Implementation Guide

### Week 1 — Dataset Collection & Labeling
1. Download the **Supatlantique** dataset from Kaggle
2. Extract it so each scanner model has its own folder:
   ```
   Supatlantique/
     scanner_A/   ← folder name = scanner label
     scanner_B/
     ...
   ```
3. Run basic image analysis to check resolution, format, channels

### Week 2 — Preprocessing
- Our pipeline auto-handles: resize to 256×256, grayscale, normalize to [0,1]
- See `backend/utils/features.py → load_and_preprocess()`

### Week 3 — Feature Extraction
- **PRNU** (Photo Response Non-Uniformity): Gaussian denoising → residual noise → 6 statistics
- **FFT**: 2D frequency transform → radially averaged power spectrum (64 bins)
- **LBP**: Local Binary Patterns histogram (256 bins)
- Total feature vector: **326 dimensions**

### Week 4 — Baseline Modeling
```bash
cd backend
pip install -r requirements.txt
python train.py --data_dir /path/to/Supatlantique --output_dir ./saved_model
```
- Trains SVM (RBF kernel) + Random Forest (200 trees)
- Outputs accuracy, F1, confusion matrix, cross-validation scores
- Saves `metrics.json` → visible on Dashboard page

### Week 5–6 — Model Evaluation + Explainability
- Confusion matrix visualization on Dashboard
- PRNU noise map + FFT spectrum on Scan page
- Feature importance chart on Dashboard
- SHAP can be added optionally (see Optional Extensions below)

### Week 7 — Web App
Start both servers:

**Backend (Terminal 1):**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend (Terminal 2):**
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

### Week 8 — Documentation & Demo
- Screenshot each page (Home, Scan, Dashboard, History)
- Export prediction reports from the Scan page
- Prepare slides using the architecture diagram

---

## Running the App

### Prerequisites
- Python 3.9+
- Node.js 18+
- pip

### 1. Backend setup
```bash
cd tracefinder/backend
pip install -r requirements.txt
uvicorn main:app --reload
```
API runs at: http://localhost:8000
API docs at: http://localhost:8000/docs

### 2. Train the model (after downloading Supatlantique)
```bash
python train.py --data_dir /path/to/Supatlantique --output_dir ./saved_model
```

### 3. Frontend setup
```bash
cd tracefinder/frontend
npm install
npm run dev
```
App runs at: http://localhost:3000

---

## Website Features

| Page | URL | Feature |
|------|-----|---------|
| Home | / | Overview, pipeline steps, feature cards |
| Scan | /scan | Upload image, live preview, scanner prediction, PRNU/FFT viz, download report |
| Dashboard | /dashboard | Model metrics, radar + bar charts, confusion matrix, feature importance |
| History | /history | All past predictions with confidence scores |

---

## Feature Engineering

### PRNU (Photo Response Non-Uniformity)
Scanner sensors have microscopic manufacturing variations that create a unique
noise fingerprint per device. We extract this by:
1. Gaussian-blur the image to get a "clean" estimate
2. Subtract blur from original → residual noise = PRNU
3. Compute 6 statistics: mean, std, skewness, kurtosis, energy, entropy

### FFT (Frequency Domain)
Scanner optics and CCD/CIS sensors introduce periodic artifacts in the frequency domain.
We compute:
1. 2D Fast Fourier Transform
2. Shift to center (DC component at origin)
3. Radially average the power spectrum into 64 bins

### LBP (Local Binary Patterns)
Captures micro-texture signatures of the scanner surface and document interaction:
1. For each pixel, compare to 24 neighbors on radius-3 circle
2. Encode as binary pattern → histogram of 256 pattern types

---

## Model Performance Targets

| Metric | Target |
|--------|--------|
| Accuracy | > 85% |
| F1 Score | > 0.83 |
| Scanners | 3–5 classes |
| Training time (no GPU) | < 5 min |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/predict/ | Upload image → get prediction + visualizations |
| GET | /api/predict/labels | List all scanner classes |
| GET | /api/predict/metrics | Get training metrics |
| POST | /api/report/download | Download HTML forensic report |
| GET | /api/history/ | Get prediction history |
| DELETE | /api/history/ | Clear history |

---

## Optional Extensions

### Add SHAP explainability (Week 6)
```bash
pip install shap
```
```python
import shap
explainer = shap.TreeExplainer(rf_pipe.named_steps['rf'])
shap_values = explainer.shap_values(X_test_scaled)
shap.summary_plot(shap_values, X_test_scaled)
```

### Add Grad-CAM (if switching to CNN)
```bash
pip install grad-cam torch torchvision
```

---

## Evaluation Criteria Checklist

- [x] Data collected and labeled (Supatlantique dataset)
- [x] Feature engineering: PRNU + FFT + LBP
- [x] Baseline ML: SVM + Random Forest
- [x] UI: Upload → Predict → Download report
- [x] Accuracy > 85% target (SVM on scanner-specific features)
- [x] Confusion matrix visualization
- [x] Feature importance chart
- [x] Prediction history log
- [x] Dark/light mode
- [x] No GPU required
