from pathlib import Path
import pickle

import numpy as np
from sklearn.ensemble import RandomForestClassifier

from app import extract_scanner_features, load_image_file


ROOT_DIR = Path(__file__).resolve().parent
SAMPLE_DATASET_DIR = ROOT_DIR / 'sample_dataset'
MODEL_PATH = ROOT_DIR / 'scanner_model.pkl'
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp'}


def iter_training_images():
    for scanner_dir in sorted(SAMPLE_DATASET_DIR.iterdir()):
        if not scanner_dir.is_dir():
            continue
        for image_path in sorted(scanner_dir.iterdir()):
            if image_path.suffix.lower() in IMAGE_EXTENSIONS:
                yield scanner_dir.name, image_path


def main():
    scanner_names = []
    scanner_to_label = {}
    features = []
    labels = []

    for scanner_name, image_path in iter_training_images():
        if scanner_name not in scanner_to_label:
            scanner_to_label[scanner_name] = len(scanner_names)
            scanner_names.append(scanner_name)

        image = load_image_file(image_path)
        features.append(extract_scanner_features(image))
        labels.append(scanner_to_label[scanner_name])
        print(f'Loaded {scanner_name}: {image_path.name}')

    if not features:
        raise RuntimeError(f'No training images found in {SAMPLE_DATASET_DIR}')

    x_train = np.vstack(features).astype(np.float32)
    y_train = np.asarray(labels, dtype=np.int64)

    classifier = RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        n_jobs=1,
        class_weight='balanced',
        bootstrap=False,
    )
    classifier.fit(x_train, y_train)

    accuracy = float(classifier.score(x_train, y_train))
    model_bundle = {
        'classifier': classifier,
        'scanner_names': scanner_names,
        'is_trained': True,
        'feature_count': int(x_train.shape[1]),
        'training_samples': int(x_train.shape[0]),
        'training_accuracy': accuracy,
    }

    with MODEL_PATH.open('wb') as fh:
        pickle.dump(model_bundle, fh)

    print(f'Saved model: {MODEL_PATH}')
    print(f'Scanners: {scanner_names}')
    print(f'Training samples: {x_train.shape[0]}')
    print(f'Feature count: {x_train.shape[1]}')
    print(f'Training accuracy: {accuracy:.3f}')


if __name__ == '__main__':
    main()
