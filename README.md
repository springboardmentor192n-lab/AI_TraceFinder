# 🔍 Scanner Identification & Tampering Detection Project

## 📌 Project Overview

This project focuses on identifying the source scanner device of a document and detecting possible image tampering using AI and image processing techniques. Each scanner leaves unique noise patterns, which are analyzed to trace the origin and verify authenticity.

---

## 🎯 Objectives

* Identify the scanner device used to scan a document
* Extract and analyze scanner-specific noise patterns (residuals)
* Detect tampered or manipulated images
* Classify types of tampering (copy-move, splicing, retouching)

---

## ⚙️ Technologies Used

* **Python**
* **Google Colab**
* **OpenCV, NumPy, SciPy**
* **Scikit-image (LBP, filters)**
* **Matplotlib, Seaborn**
* **Machine Learning & Image Processing Techniques**

---

## 🧠 Methodology

1. **Data Collection & Preprocessing**

   * Convert images to grayscale, resize, normalize
   * Remove content using denoising techniques
   * Extract residual noise patterns

2. **Scanner Fingerprint Extraction**

   * Use flatfield images to compute unique scanner fingerprints
   * Average residual noise to capture consistent patterns

3. **Feature Extraction**

   * Correlation with scanner fingerprints
   * FFT (frequency features)
   * LBP (texture features)
   * Statistical texture analysis

4. **Feature Visualization**

   * PCA for dimensionality reduction
   * t-SNE for clustering
   * Heatmaps for feature comparison

---

## 📊 Results

* Successfully extracted scanner-specific noise patterns
* Generated unique fingerprints for each scanner
* Visualizations show clear clustering of different scanners
* Features effectively distinguish between scanner devices

---

## 🚀 Progress

* ✅ Milestone 1: Dataset Collection & Preprocessing
* ✅ Milestone 2: Feature Extraction & Visualization
* 🔄 Next: Model Training & Scanner Prediction

---

## 📁 Project Structure

```
AI_TRACEFINDER/
│
├── notebooks/
├── data/
├── outputs/
├── results/
└── README.md
```

---

## ▶️ How to Run

1. Open the notebook in Google Colab
2. Mount Google Drive
3. Run the cells step-by-step
4. Load saved `.pkl` files to skip preprocessing

---

## 📌 Note

Due to large size, the full dataset is not included. Only processed outputs and results are provided.

---

## 👩‍💻 Author

**Jaya Kumari**
