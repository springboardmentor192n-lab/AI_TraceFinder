# TraceFinder Workspace Cleanup Guide

## 📋 Files to Delete (Duplicates & Unnecessary)

### ❌ Duplicate Model Files (in root - use artifacts/ instead)
- `scanner_hybrid (2).keras`
- `scanner_hybrid_final (1).keras`
- `scanner_hybrid_final.keras`
- `scanner_model.keras`
- `fp_keys.npy`
- `hybrid_feat_scaler.pkl`
- `hybrid_label_encoder.pkl`
- `scanner_fingerprints (2).pkl`
- `scanner_fingerprints (3).pkl`

### ❌ Old/Redundant HTML Files
- `Flatfield.html`
- `Official.html`
- `Official_1.html`
- `Originals.html`
- `Originals_1.html`
- `tracefinder.html` (old version - use tracefinder_auth.html)

### ❌ Old/Redundant Python Applications
- `app.py` (use backend/api.py)
- `forensics_app.py` (old Streamlit app)
- `model_inspector.py` (debug tool)
- `notebook.ipynb` (old notebook)

### ❌ Unnecessary Data Files
- `flatfield_residuals.pkl`
- `official_wiki_residuals.pkl`
- `enhanced_features.pkl`
- `features.pkl`
- `hybrid_training_history.pkl`

### ❌ Temporary/Archive Files
- `load_test_output.txt`
- `files.zip`
- `requirements.txt.txt` (duplicate)
- `Trace_finder-20260402T041728Z-1-001.zip`

### ❌ Redundant Directories
- `frontend/` (duplicate of UI files)
- `.venv-1/` (old virtualenv)
- `__pycache__/` (Python cache)

---

## ✅ Files to Keep (Core Application)

### Working Application Code
- `backend/api.py` → Main Flask API
- `backend/preprocessing.py` → Image preprocessing
- `backend/identification.py` → Scanner ID logic
- `backend/features.py` → Feature extraction
- `backend/residual.py` → Residual analysis

### Frontend UI
- `tracefinder_auth.html` → Main UI with authentication
- `index.html` → Fallback basic UI

### Model Artifacts (for inference)
- `artifacts/scanner_hybrid.keras` → ML model
- `artifacts/hybrid_label_encoder.pkl` → Label encoder
- `artifacts/hybrid_feat_scaler.pkl` → Feature scaler
- `artifacts/scanner_fingerprints.pkl` → Scanner fingerprints database
- `artifacts/fp_keys.npy` → Fingerprint keys

### Configuration & Dependencies
- `requirements.txt` → Python dependencies
- `.gitignore` → Git config
- `.env` (if needed for secrets)

### Documentation & Tests
- `README.md` → Project overview
- `BACKEND_SETUP.md` → Setup instructions
- `COMPLETION_SUMMARY.md` → Progress summary
- `test_api.py` → API test script
- `quickstart.py` → Quick start script
- `LICENSE` → License

### Infrastructure
- `.git/` → Version control
- `logs/` → Application logs
- `tracefinder.db` → SQLite database

---

## 🚀 Cleanup Steps

### Option 1: Manual Deletion (GUI)
1. Open File Explorer
2. Navigate to `C:\Users\tejap\Downloads\Trace_finder-20260402T041728Z-1-001\Trace_finder`
3. Delete files listed above by right-clicking → Delete
4. Empty Recycle Bin

### Option 2: Command Line (PowerShell)
Run in PowerShell as Administrator:

```powershell
cd C:\Users\tejap\Downloads\Trace_finder-20260402T041728Z-1-001\Trace_finder

# Duplicate models
Remove-Item "scanner_hybrid (2).keras" -Force
Remove-Item "scanner_hybrid_final (1).keras" -Force
Remove-Item "scanner_hybrid_final.keras" -Force
Remove-Item "scanner_model.keras" -Force

# Old HTML
Remove-Item "Flatfield.html" -Force
Remove-Item "Official.html" -Force
Remove-Item "Official_1.html" -Force
Remove-Item "Originals.html" -Force
Remove-Item "Originals_1.html" -Force
Remove-Item "tracefinder.html" -Force

# Old Python
Remove-Item "app.py" -Force
Remove-Item "forensics_app.py" -Force
Remove-Item "model_inspector.py" -Force
Remove-Item "notebook.ipynb" -Force

# Data files
Remove-Item "flatfield_residuals.pkl" -Force
Remove-Item "official_wiki_residuals.pkl" -Force
Remove-Item "enhanced_features.pkl" -Force
Remove-Item "features.pkl" -Force
Remove-Item "hybrid_training_history.pkl" -Force

# Temp files
Remove-Item "load_test_output.txt" -Force
Remove-Item "files.zip" -Force
Remove-Item "requirements.txt.txt" -Force
Remove-Item "Trace_finder-20260402T041728Z-1-001.zip" -Force

# Cleanup scripts
Remove-Item "cleanup.py" -Force
Remove-Item "cleanup.ps1" -Force

# Directories
Remove-Item "frontend" -Recurse -Force
Remove-Item ".venv-1" -Recurse -Force
```

---

## ✅ Verification Checklist

After cleanup, your root directory should contain:

- ✅ `.git/` (version control)
- ✅ `.gitattributes`, `.gitignore`
- ✅ `.venv/` (active Python environment)
- ✅ `artifacts/` (model files)
- ✅ `backend/` (API code)
- ✅ `logs/` (application logs)
- ✅ `index.html`, `tracefinder_auth.html`
- ✅ `test_api.py`, `quickstart.py`
- ✅ `requirements.txt`
- ✅ `tracefinder.db`
- ✅ `README.md`, `LICENSE`
- ✅ `BACKEND_SETUP.md`, `COMPLETION_SUMMARY.md`

**Approximate size after cleanup:** ~50-100 MB (vs 500+ MB+ before)

---

## 🎯 Next Steps

1. **Cleanup workspace** using option above
2. **Verify** directory structure matches checklist
3. **Run application:**
   ```bash
   python backend/api.py
   # In another terminal:
   python -m http.server 8000
   ```
4. **Test:** `http://127.0.0.1:8000/tracefinder_auth.html`

---

Generated: 2026-04-02
