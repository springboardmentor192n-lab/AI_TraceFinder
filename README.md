# TRACE_FINDER — SUPATLANTIQUE Forensics

Scanner Source Identification & Forgery Detection
11 scanners · Hybrid CNN + SVM · Streamlit Dashboard

## Quick Start
pip install -r requirements.txt
streamlit run forensics_app.py

## Artifact Placement
Place trained model files in artifacts/:
  scanner_hybrid.keras            (Cell 12)
  hybrid_label_encoder.pkl        (Cell 11)
  hybrid_feat_scaler.pkl          (Cell 11)
  scanner_fingerprints.pkl        (Cell 6)
  fp_keys.npy                     (Cell 6)
  artifacts_tamper_patch/
    patch_svm_sig_calibrated.pkl  (Cell 19)
    patch_scaler.pkl              (Cell 19)
    thresholds_patch.json         (Cell 19)

## HTML Pipeline Docs (open in browser)
  Flatfield.html        PRNU flatfield residual preprocessing
  Official.html         Official docs + PRNU/FFT/LBP features + PCA
  Originals.html        PDF-to-TIFF conversion + tamper manifest
  Tampered images.html  22-D patch features + SVM training + inference
  Wikipedia.html        Wikipedia preprocessing + Hybrid CNN training

## Notes
This repository contains the Streamlit app `forensics_app.py` and supporting model artifacts for local deployment.

