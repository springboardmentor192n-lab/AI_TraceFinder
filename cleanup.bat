@echo off
REM TraceFinder Workspace Cleanup Script
REM This script removes duplicate and unnecessary files

echo ========================================
echo TraceFinder Workspace Cleanup
echo ========================================
echo.

cd /d C:\Users\tejap\Downloads\Trace_finder-20260402T041728Z-1-001\Trace_finder

REM Duplicate model files
echo Removing duplicate model files...
del /F /Q "scanner_hybrid (2).keras" 2>nul
del /F /Q "scanner_hybrid_final (1).keras" 2>nul
del /F /Q "scanner_hybrid_final.keras" 2>nul
del /F /Q "scanner_model.keras" 2>nul

REM Old HTML files
echo Removing old HTML files...
del /F /Q "Flatfield.html" 2>nul
del /F /Q "Official.html" 2>nul
del /F /Q "Official_1.html" 2>nul
del /F /Q "Originals.html" 2>nul
del /F /Q "Originals_1.html" 2>nul
del /F /Q "tracefinder.html" 2>nul

REM Duplicate pickle files
echo Removing duplicate pickle files...
del /F /Q "scanner_fingerprints (2).pkl" 2>nul
del /F /Q "scanner_fingerprints (3).pkl" 2>nul

REM Old Python apps
echo Removing old Python applications...
del /F /Q "app.py" 2>nul
del /F /Q "forensics_app.py" 2>nul
del /F /Q "model_inspector.py" 2>nul
del /F /Q "notebook.ipynb" 2>nul

REM Unnecessary data files
echo Removing unnecessary data files...
del /F /Q "flatfield_residuals.pkl" 2>nul
del /F /Q "official_wiki_residuals.pkl" 2>nul
del /F /Q "enhanced_features.pkl" 2>nul
del /F /Q "features.pkl" 2>nul
del /F /Q "hybrid_training_history.pkl" 2>nul

REM Temporary files
echo Removing temporary files...
del /F /Q "load_test_output.txt" 2>nul
del /F /Q "files.zip" 2>nul
del /F /Q "requirements.txt.txt" 2>nul
del /F /Q "Trace_finder-20260402T041728Z-1-001.zip" 2>nul

REM Remove duplicate root-level artifacts (keep in artifacts/ folder)
echo Removing root-level duplicate artifacts...
del /F /Q "fp_keys.npy" 2>nul
del /F /Q "hybrid_feat_scaler.pkl" 2>nul
del /F /Q "hybrid_label_encoder.pkl" 2>nul

REM Directories
echo Removing redundant directories...
rmdir /S /Q "frontend" 2>nul
rmdir /S /Q ".venv-1" 2>nul

REM Cleanup scripts themselves
del /F /Q "cleanup.py" 2>nul
del /F /Q "cleanup.ps1" 2>nul

echo.
echo ========================================
echo ✓ Cleanup complete!
echo ========================================
echo.
dir | find /c /v ""
echo Total files remaining in directory
echo.
pause
