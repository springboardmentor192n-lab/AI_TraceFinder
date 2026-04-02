import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MODEL_FILES = [
    'scanner_hybrid (2).keras',
    'scanner_hybrid_final (1).keras',
    'scanner_hybrid_final.keras',
]
ARTIFACT_FILES = [
    'fp_keys.npy',
    'hybrid_feat_scaler.pkl',
    'hybrid_label_encoder.pkl',
    'hybrid_training_history.pkl',
    'enhanced_features.pkl',
    'features.pkl',
    'flatfield_residuals.pkl',
    'official_wiki_residuals.pkl',
    'scanner_fingerprints (2).pkl',
    'scanner_fingerprints (3).pkl',
]


def verify_files(file_list):
    found = []
    missing = []

    for name in file_list:
        path = ROOT / name
        if path.exists():
            found.append((name, path.stat().st_size))
        else:
            missing.append(name)

    return found, missing


def print_report():
    print('Trace Finder model artifact verification')
    print('Working directory:', ROOT)
    print()

    found_models, missing_models = verify_files(MODEL_FILES)
    found_artifacts, missing_artifacts = verify_files(ARTIFACT_FILES)

    print('Saved models:')
    if found_models:
        for name, size in found_models:
            print(f'  - {name} ({size:,} bytes)')
    else:
        print('  - None found')

    if missing_models:
        print('\nMissing saved models:')
        for name in missing_models:
            print(f'  - {name}')

    print('\nSupporting artifacts:')
    if found_artifacts:
        for name, size in found_artifacts:
            print(f'  - {name} ({size:,} bytes)')
    else:
        print('  - None found')

    if missing_artifacts:
        print('\nMissing artifacts:')
        for name in missing_artifacts:
            print(f'  - {name}')

    print('\nArchive note:')
    zip_path = ROOT / 'Trace_finder-20260402T041728Z-1-001.zip'
    if zip_path.exists():
        print(f'  - ZIP archive found: {zip_path.name}')
    else:
        print('  - ZIP archive not found in workspace root')


if __name__ == '__main__':
    print_report()
