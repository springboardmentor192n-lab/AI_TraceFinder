# 🧠 TraceFinder – Scanner Source Identification & Forgery Detection

## 📌 Project Overview

TraceFinder is a digital forensic system that identifies the scanner used to capture a document and detects possible forgery using image analysis techniques.

The system uses **machine learning (SVM)** and **noise-based feature extraction** to analyze scanned documents and predict their source.

---

## 🎯 Objectives

- Identify the scanner brand/model used to scan a document
- Detect whether the document is:
  - Scanned
  - Digitally generated (PDF)
- Detect possible forgery using residual noise analysis
- Provide a user-friendly web interface using Streamlit

---

## 📂 Dataset

The project uses a structured dataset containing:

- **Flatfield Images** → Used to capture scanner noise patterns
- **Official Scans** → Real-world scanned documents
- **Wikipedia Scans** → Additional diverse scanned documents
- **Original PDFs** → Digital documents (no scanner noise)
- **Tampered Images** → Used for forgery detection

---

## ⚙️ Methodology

### 1. Preprocessing
- Convert images to grayscale
- Apply Gaussian Blur
- Extract residual noise

### 2. Feature Extraction
- Mean, Standard Deviation, Variance
- Histogram features

### 3. Model Training
- Algorithm: **Support Vector Machine (SVM)**
- Feature scaling using **StandardScaler**
- Evaluation using:
  - Accuracy
  - Confusion Matrix
  - Precision, Recall, F1-score

---

## 🖥️ Streamlit Application

Features:

- Upload image or PDF
- Detect scanner model
- Show confidence score
- Detect forgery
- Log predictions
- Download results

---

## 📊 Output Example

- Scanner Detected: Canon9000-1
- Confidence: 87.5%
- Forgery: Not Detected



---

## 🧪 Technologies Used

- Python
- OpenCV
- NumPy
- Scikit-learn
- Streamlit
- Pandas

---

## 📁 Project Structure
```
TraceMaker/
│── app.py
│── train_model.py
│── model.pkl
│── scaler.pkl
│── log.csv
│
└── Dataset/
├── Flatfield/
├── Official/
├── Wikipedia/
├── Tampered images/
```

