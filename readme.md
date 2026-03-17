# 🔍 TraceFinder – Scanner Identification System (Phase 1: Data Pipeline + Preparation)

## 📌 Project Overview

TraceFinder is an AI-powered forensic system designed to:

* Identify the **scanner device** used to digitize a document
* Detect **forgery and tampering** in scanned documents *(future phase)*

This repository currently implements **Phase 1: Scanner Fingerprint Learning Pipeline**, which focuses on building a robust dataset and training-ready pipeline for **scanner identification using deep learning**.

---

## 🎯 Objective (Current Phase)

The goal of this phase is to:

* Extract **scanner-specific noise patterns (fingerprints)**
* Build a **high-quality dataset of image patches**
* Prepare a **memory-efficient deep learning pipeline**
* Enable training of a CNN model for **scanner classification**

---

## 📂 Dataset Used

We used the **SUPATLANTIQUE Scanner Dataset**, which contains:

* Scanned documents from multiple scanner devices
* Multiple resolutions (150 DPI, 300 DPI)
* Flatfield images (sensor calibration)
* Tampered images (for future forgery detection)

---

## ⚙️ Step-by-Step Implementation

---

### 1️⃣ Dataset Understanding & Exploration (EDA)

We analyzed the dataset structure and extracted key insights:

* Identified **scanner-wise folder hierarchy**
* Verified **image formats (.tif)**
* Analyzed:

  * Image resolutions
  * Class distribution
  * Sample visualizations
* Detected **class imbalance**

⚠️ Identified weak classes:

* `Canon9000-2`
* `EpsonV39-2`

These had extremely low samples and were removed.

---

### 2️⃣ Dataset Restructuring

Original dataset was deeply nested.

We converted it into a clean ML-friendly structure:

```text
dataset_clean/
    Canon120-1/
    Canon120-2/
    Canon220/
    Canon9000-1/
    EpsonV370-1/
    EpsonV370-2/
    EpsonV39-1/
    HP/
```

✔ Each folder = one scanner class
✔ All images consolidated into class folders

---

### 3️⃣ Noise Residual Extraction (Core Forensics Step)

To isolate scanner fingerprints, we removed document content.

Method:

```text
Residual = Original Image − Gaussian Blurred Image
```

This step extracts:

* Sensor noise (PRNU)
* Scan-line artifacts
* Frequency distortions

Output:

```text
dataset_residual/
```

✔ This ensures the model learns **scanner noise, not document text**

---

### 4️⃣ Patch Extraction (Key Scaling Step)

Instead of using full images, we extracted patches.

Configuration:

```text
Patch size: 128 × 128
Patches per image: 500
```

Reason:

* Scanner fingerprints are **local patterns**
* Improves generalization
* Prevents model from learning layout/text

Output:

```text
dataset_patches/
```

Dataset size after extraction:

```text
~87,000+ patches
```

---

### 5️⃣ Dataset Balancing

We addressed imbalance:

* Removed extremely small classes
* Achieved balanced distribution across 8 scanners

Final classes:

```text
Canon120-1
Canon120-2
Canon220
Canon9000-1
EpsonV370-1
EpsonV370-2
EpsonV39-1
HP
```

---

### 6️⃣ Train / Validation / Test Split

We split the dataset into:

```text
Train: 70%
Validation: 15%
Test: 15%
```

Final structure:

```text
dataset_final/
    train/
    val/
    test/
```

✔ Ensures proper evaluation and prevents overfitting

---

### 7️⃣ PyTorch Dataset (Memory-Efficient Design)

We implemented a custom Dataset class:

* Stores **file paths only**
* Loads images **on demand**
* Prevents RAM overload

Key features:

```text
Lazy loading
Label mapping (class_to_idx)
Grayscale conversion
Transform support
```

---

### 8️⃣ DataLoader Optimization

Configured DataLoaders for stable training:

```python
train_loader:
    batch_size = 32
    shuffle = True
    num_workers = 0
    pin_memory = True

val/test_loader:
    batch_size = 64
    shuffle = False
```

✔ Avoids multiprocessing crashes (Windows/Jupyter safe)
✔ Efficient batch loading

---

### 9️⃣ Data Pipeline Validation

We validated the pipeline:

```text
Batch shape: [32, 1, 128, 128]
Labels shape: [32]
Dataset size: ~87k samples
```

✔ Confirms correct preprocessing and loading

---

## 🧠 Key Design Decisions

* Used **noise residuals** to focus on scanner fingerprints
* Used **patch-based learning** instead of full images
* Removed **weak classes** to stabilize training
* Built **memory-safe PyTorch pipeline**
* Ensured **balanced multi-class classification setup**

---

## 📊 Current Project Status

```text
Dataset Preparation        ✅ Completed
EDA                        ✅ Completed
Noise Extraction           ✅ Completed
Patch Extraction           ✅ Completed
Dataset Balancing          ✅ Completed
Train/Test Split           ✅ Completed
PyTorch Data Pipeline      ✅ Completed

Model Training             🔜 Next
Forgery Detection          🔜 Future Phase
Deployment                 🔜 Final Phase
```

---

## 🚀 Next Steps

* Build CNN model for scanner classification
* Train using extracted patches
* Evaluate using accuracy + confusion matrix
* Integrate forgery detection module

---

## 🧩 Final Goal

The complete system will:

```text
Input: Scanned document
Output:
    Scanner Model
    Forgery Status
    Forgery Type (Copy-move / Splicing / Retouching)
```

---

## 💡 Summary

This phase establishes a **high-quality forensic data pipeline** that enables:

* Robust scanner fingerprint learning
* Scalable deep learning training
* Foundation for advanced forgery detection

---
