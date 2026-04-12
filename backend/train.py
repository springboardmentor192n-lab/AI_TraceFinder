# TraceFinder - Improved Training Script for Supatlantique Dataset
#
# Key improvements over v1:
#   1. Uses ALL sub-datasets (Flatfield + Official + Wikipedia) to maximize samples
#   2. Image augmentation to multiply samples from classes with few images
#   3. Better SVM hyperparameters + PCA dimensionality reduction
#   4. Handles the nested Supatlantique structure correctly
#
# Usage (always use forward slashes or quotes on Windows):
#   python train.py --data_dir "C:/Users/YourName/Desktop/tracefinder/SUPATLANTIQUE Dataset"

import os
import argparse
import pickle
import json
import logging
from pathlib import Path
from collections import defaultdict

import numpy as np
import cv2
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score, GridSearchCV
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score,
    recall_score, confusion_matrix, classification_report
)
from sklearn.pipeline import Pipeline

import sys
sys.path.insert(0, str(Path(__file__).parent))
from utils.features import extract_all_features, load_and_preprocess

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# ── Supatlantique scanner labels ──────────────────────────────
KNOWN_SCANNERS = {
    "canon120-1", "canon120-2", "canon220",
    "canon9000-1", "canon9000-2",
    "epsonv39-1", "epsonv39-2",
    "epsonv370-1", "epsonv370-2",
    "epsonv550", "hp",
}

SUPPORTED_EXT = {".tif", ".tiff", ".jpg", ".jpeg", ".png", ".bmp"}
SKIP_KEYWORDS = {"originals", "tampered images", "tampered", "binary masks"}


# ── Helpers ───────────────────────────────────────────────────

def should_skip(path: Path) -> bool:
    for part in path.parts:
        if any(skip in part.lower() for skip in SKIP_KEYWORDS):
            return True
    return False


def is_scanner_folder(name: str) -> bool:
    return name.lower() in KNOWN_SCANNERS


def augment_image_bytes(img_bytes: bytes) -> list:
    """
    Generate augmented versions of an image to increase training samples.
    Returns list of bytes objects (original + augmented).
    All augmentations are mild — they preserve scanner noise fingerprint.
    """
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return [img_bytes]

    augmented = [img_bytes]  # always include original

    # Small crops (preserve central 90% — keeps noise pattern)
    h, w = img.shape
    for scale in [0.9, 0.95]:
        dh, dw = int(h * (1 - scale) / 2), int(w * (1 - scale) / 2)
        if dh > 0 and dw > 0:
            crop = img[dh:h-dh, dw:w-dw]
            _, buf = cv2.imencode(".png", crop)
            augmented.append(buf.tobytes())

    # Very slight brightness shift (does NOT significantly affect PRNU)
    for delta in [-8, 8]:
        shifted = np.clip(img.astype(np.int16) + delta, 0, 255).astype(np.uint8)
        _, buf = cv2.imencode(".png", shifted)
        augmented.append(buf.tobytes())

    return augmented  # original + 4 augmented = 5x per image


# ── Dataset collection ────────────────────────────────────────

def collect_images(data_dir: str) -> dict:
    """Walk Supatlantique tree, return {scanner_label: [Path, ...]}"""
    data_dir = Path(data_dir)
    if not data_dir.exists():
        raise ValueError(f"Dataset directory not found: {data_dir}")

    scanner_images = defaultdict(list)
    visited = set()

    for dirpath, dirnames, filenames in os.walk(str(data_dir)):
        current = Path(dirpath)
        if should_skip(current):
            dirnames.clear()
            continue
        folder_name = current.name
        if is_scanner_folder(folder_name) and str(current) not in visited:
            visited.add(str(current))
            for f in current.rglob("*"):
                if f.is_file() and f.suffix.lower() in SUPPORTED_EXT:
                    scanner_images[folder_name].append(f)
            dirnames.clear()

    return dict(scanner_images)


def load_dataset(data_dir: str, min_samples: int = 2, use_augmentation: bool = True):
    """
    Load + extract features from all scanner images.
    Applies augmentation to classes with fewer than TARGET_SAMPLES images.
    """
    TARGET_SAMPLES = 80  # balance all classes to this size after augmentation

    scanner_images = collect_images(data_dir)
    if not scanner_images:
        raise ValueError(
            f"No scanner images found under:\n  {data_dir}\n"
            "Make sure --data_dir points at the 'SUPATLANTIQUE Dataset' root."
        )

    scanner_images = {k: v for k, v in scanner_images.items() if len(v) >= min_samples}
    label_names = sorted(scanner_images.keys())

    logger.info(f"\nFound {len(label_names)} scanner classes:")
    for label in label_names:
        n = len(scanner_images[label])
        aug = " (will augment)" if use_augmentation and n < TARGET_SAMPLES else ""
        logger.info(f"  {label:20s}  {n} images{aug}")

    X, y = [], []

    for idx, label in enumerate(label_names):
        paths = scanner_images[label]
        n_images = len(paths)
        extracted = 0

        for img_path in paths:
            try:
                with open(img_path, "rb") as f:
                    img_bytes = f.read()

                # Augment all classes to reach TARGET_SAMPLES
                if use_augmentation:
                    versions = augment_image_bytes(img_bytes)
                else:
                    versions = [img_bytes]

                for version_bytes in versions:
                    try:
                        feat = extract_all_features(version_bytes)
                        X.append(feat)
                        y.append(idx)
                        extracted += 1
                    except Exception:
                        pass

            except Exception as e:
                logger.warning(f"  Skip {img_path.name}: {e}")

        # Cap at TARGET_SAMPLES to keep classes balanced
        if use_augmentation and extracted > TARGET_SAMPLES:
            start = len(X) - extracted
            del X[start + TARGET_SAMPLES:]
            del y[start + TARGET_SAMPLES:]
            extracted = TARGET_SAMPLES
        logger.info(f"  {label:20s}  {extracted} feature vectors (final)")

    if not X:
        raise ValueError("No features could be extracted.")

    X = np.array(X, dtype=np.float32)
    y = np.array(y, dtype=int)

    counts = np.bincount(y)
    logger.info(f"\nDataset: {X.shape[0]} samples | {X.shape[1]} features | {len(label_names)} classes")
    logger.info(f"Class sizes: min={counts.min()} max={counts.max()} mean={counts.mean():.1f}\n")
    return X, y, label_names


# ── Training ──────────────────────────────────────────────────

def train_and_evaluate(X, y, label_names, output_dir: str, tune: bool = False):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    n_splits = max(2, min(5, int(np.bincount(y).min())))

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    logger.info(f"Train: {len(X_train)} | Test: {len(X_test)} | CV folds: {n_splits}")

    # ── SVM with PCA (best for PRNU features) ────────────────
    logger.info("Training SVM + PCA ...")
    n_components = min(150, X_train.shape[0] - 1, X_train.shape[1])

    if tune:
        logger.info("  Running GridSearchCV for SVM (this may take a few minutes) ...")
        svm_base = Pipeline([
            ("scaler", StandardScaler()),
            ("pca", PCA(n_components=n_components, random_state=42)),
            ("svm", SVC(probability=True, random_state=42))
        ])
        param_grid = {
            "svm__C":     [1, 10, 100],
            "svm__gamma": ["scale", "auto"],
            "svm__kernel": ["rbf", "linear"],
        }
        cv_gs = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
        gs = GridSearchCV(svm_base, param_grid, cv=cv_gs, scoring="accuracy", n_jobs=-1, verbose=0)
        gs.fit(X_train, y_train)
        svm_pipe = gs.best_estimator_
        logger.info(f"  Best SVM params: {gs.best_params_}")
    else:
        svm_pipe = Pipeline([
            ("scaler", StandardScaler()),
            ("pca", PCA(n_components=n_components, random_state=42)),
            ("svm", SVC(kernel="rbf", C=100.0, gamma="scale", probability=True, random_state=42))
        ])
        svm_pipe.fit(X_train, y_train)

    # ── Random Forest ─────────────────────────────────────────
    logger.info("Training Random Forest (500 trees, balanced) ...")
    rf_pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("rf", RandomForestClassifier(
            n_estimators=500,
            max_features="sqrt",
            min_samples_leaf=1,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1
        ))
    ])
    rf_pipe.fit(X_train, y_train)

    # ── Extra Trees (often beats RF on sensor noise data) ─────
    from sklearn.ensemble import ExtraTreesClassifier
    logger.info("Training Extra Trees (500 trees, balanced) ...")
    et_pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("et", ExtraTreesClassifier(
            n_estimators=500,
            max_features="sqrt",
            min_samples_leaf=1,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1
        ))
    ])
    et_pipe.fit(X_train, y_train)

    # ── Cross-validation ──────────────────────────────────────
    logger.info(f"Running {n_splits}-fold cross-validation ...")
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    svm_cv = cross_val_score(svm_pipe, X, y, cv=cv, scoring="accuracy", n_jobs=-1)
    rf_cv  = cross_val_score(rf_pipe,  X, y, cv=cv, scoring="accuracy", n_jobs=-1)
    et_cv  = cross_val_score(et_pipe,  X, y, cv=cv, scoring="accuracy", n_jobs=-1)

    # ── Evaluation ────────────────────────────────────────────
    def evaluate(model, name, cv_scores):
        pred = model.predict(X_test)
        acc  = accuracy_score(y_test, pred)
        f1   = f1_score(y_test, pred, average="weighted", zero_division=0)
        prec = precision_score(y_test, pred, average="weighted", zero_division=0)
        rec  = recall_score(y_test, pred, average="weighted", zero_division=0)
        cm   = confusion_matrix(y_test, pred).tolist()
        logger.info(f"\n{'='*50}")
        logger.info(f"{name} | Acc: {acc:.4f} | F1: {f1:.4f} | CV: {cv_scores.mean():.4f}±{cv_scores.std():.4f}")
        logger.info(classification_report(y_test, pred, target_names=label_names, zero_division=0))
        return {
            "accuracy":         round(acc,  4),
            "f1":               round(f1,   4),
            "precision":        round(prec, 4),
            "recall":           round(rec,  4),
            "cv_mean":          round(float(cv_scores.mean()), 4),
            "cv_std":           round(float(cv_scores.std()),  4),
            "confusion_matrix": cm,
        }

    svm_m = evaluate(svm_pipe, "SVM + PCA",      svm_cv)
    rf_m  = evaluate(rf_pipe,  "Random Forest",  rf_cv)
    et_m  = evaluate(et_pipe,  "Extra Trees",    et_cv)

    scores = {"SVM": svm_m["accuracy"], "RandomForest": rf_m["accuracy"], "ExtraTrees": et_m["accuracy"]}
    best_name  = max(scores, key=scores.get)
    best_model = {"SVM": svm_pipe, "RandomForest": rf_pipe, "ExtraTrees": et_pipe}[best_name]
    logger.info(f"\n✅ Best model: {best_name}")

    # ── Save ─────────────────────────────────────────────────
    for fname, obj in [
        ("svm_model.pkl",  svm_pipe),
        ("rf_model.pkl",   rf_pipe),
        ("et_model.pkl",   et_pipe),
        ("best_model.pkl", best_model),
    ]:
        with open(output_dir / fname, "wb") as f:
            pickle.dump(obj, f)

    le = LabelEncoder()
    le.classes_ = np.array(label_names)
    with open(output_dir / "label_encoder.pkl", "wb") as f:
        pickle.dump(le, f)

    metrics_out = {
        "label_names": label_names,
        "n_classes":   len(label_names),
        "n_train":     int(len(X_train)),
        "n_test":      int(len(X_test)),
        "best_model":  best_name,
        "svm":         svm_m,
        "rf":          rf_m,
        "et":          et_m,
    }
    with open(output_dir / "metrics.json", "w") as f:
        json.dump(metrics_out, f, indent=2)

    logger.info(f"\nModels saved to: {output_dir}")
    logger.info(f"SVM: {svm_m['accuracy']:.2%}  |  RF: {rf_m['accuracy']:.2%}  |  ET: {et_m['accuracy']:.2%}")
    logger.info(f"Best: {best_name}")
    return metrics_out


# ── Entry point ───────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Train TraceFinder on Supatlantique dataset",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
  python train.py --data_dir "C:/path/to/SUPATLANTIQUE Dataset"

  # With hyperparameter tuning (slower but better accuracy):
  python train.py --data_dir "..." --tune
        """
    )
    parser.add_argument("--data_dir",    required=True,  help="Path to SUPATLANTIQUE Dataset root")
    parser.add_argument("--output_dir",  default="./saved_model", help="Where to save models")
    parser.add_argument("--min_samples", type=int, default=2, help="Min images per class (default: 2)")
    parser.add_argument("--no_augment",  action="store_true", help="Disable image augmentation")
    parser.add_argument("--tune",        action="store_true", help="Run GridSearchCV for best SVM params (slower)")
    args = parser.parse_args()

    logger.info("=" * 50)
    logger.info("TraceFinder — Model Training v2")
    logger.info("=" * 50)
    logger.info(f"data_dir    : {args.data_dir}")
    logger.info(f"output_dir  : {args.output_dir}")
    logger.info(f"augmentation: {not args.no_augment}")
    logger.info(f"tuning      : {args.tune}")

    X, y, label_names = load_dataset(
        args.data_dir,
        min_samples=args.min_samples,
        use_augmentation=not args.no_augment
    )
    train_and_evaluate(X, y, label_names, args.output_dir, tune=args.tune)
    logger.info("\nTraining complete!")
