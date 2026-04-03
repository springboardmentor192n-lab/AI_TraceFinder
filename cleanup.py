#!/usr/bin/env python3
"""Clean up TraceFinder workspace - remove duplicates and unnecessary files"""
import os
import shutil

os.chdir(r'C:\Users\tejap\Downloads\Trace_finder-20260402T041728Z-1-001\Trace_finder')

# Files to delete
to_delete = [
    # Duplicate model files
    'scanner_hybrid (2).keras',
    'scanner_hybrid_final (1).keras',
    'scanner_hybrid_final.keras',
    'scanner_model.keras',
    'fp_keys.npy',  # duplicate in artifacts/
    'hybrid_feat_scaler.pkl',  # duplicate in artifacts/
    'hybrid_label_encoder.pkl',  # duplicate in artifacts/
    'scanner_fingerprints (2).pkl',
    'scanner_fingerprints (3).pkl',
    
    # Old HTML files
    'Flatfield.html',
    'Official.html',
    'Official_1.html',
    'Originals.html',
    'Originals_1.html',
    'tracefinder.html',
    
    # Old Python apps
    'app.py',
    'forensics_app.py',
    'model_inspector.py',
    'notebook.ipynb',
    
    # Unnecessary data files
    'flatfield_residuals.pkl',
    'official_wiki_residuals.pkl',
    'enhanced_features.pkl',
    'features.pkl',
    'hybrid_training_history.pkl',
    
    # Temp/archive files
    'load_test_output.txt',
    'files.zip',
    'requirements.txt.txt',
    'Trace_finder-20260402T041728Z-1-001.zip',
    'cleanup.ps1',
]

# Directories to delete
dirs_to_delete = [
    'frontend',
    '.venv-1',
    '__pycache__',
]

deleted_count = 0
failed = []

# Delete files
for file in to_delete:
    try:
        if os.path.exists(file):
            os.remove(file)
            print(f'✓ Deleted: {file}')
            deleted_count += 1
    except Exception as e:
        failed.append(f'{file}: {e}')
        print(f'✗ Failed to delete {file}: {e}')

# Delete directories
for dir_path in dirs_to_delete:
    try:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
            print(f'✓ Deleted directory: {dir_path}')
            deleted_count += 1
    except Exception as e:
        failed.append(f'{dir_path}/: {e}')
        print(f'✗ Failed to delete {dir_path}: {e}')

print(f'\n✅ Cleanup complete! Deleted {deleted_count} items.')
if failed:
    print(f'⚠️  {len(failed)} items failed to delete - may need manual removal')
    for item in failed:
        print(f'  - {item}')
