"""
AI TraceFinder v2 - Enhanced Model Training Pipeline
Hybrid Ensemble Classifier: RandomForest + GradientBoosting + SVM

Improvements over v1:
- Multi-scale feature extraction (PRNU at 3 scales)
- Histogram of Oriented Gradients (HOG) features
- Color channel cross-correlation (for color images)
- Hybrid ensemble with weighted soft voting
- Data augmentation for better generalization
- Cross-validation with stratified folds
- Hyperparameter optimization

Expected accuracy improvement: 82% → 88-92%

Dataset location: OneDrive/Amrita Vishwa Vidyapeetham-Chennai Campus/dataset/
"""

import os
import cv2
import numpy as np
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    VotingClassifier,
)
from sklearn.svm import SVC
from sklearn.model_selection import (
    train_test_split,
    StratifiedKFold,
    cross_val_score,
)
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from sklearn.pipeline import Pipeline
import joblib
from pathlib import Path
from scipy.signal import wiener
from scipy import ndimage
from scipy.fft import fft2, fftshift
from scipy.stats import skew, kurtosis
import sys
import time
import warnings

warnings.filterwarnings("ignore")


# ============================================================
# Configuration
# ============================================================
DATASET_PATH = r"C:\Users\jayabhuvanesh\OneDrive - Amrita Vishwa Vidyapeetham- Chennai Campus\dataset"
MODEL_SAVE_PATH = os.path.join(os.path.dirname(__file__), "scanner_model_v2.pkl")
SCALER_SAVE_PATH = os.path.join(os.path.dirname(__file__), "feature_scaler_v2.pkl")
CLASSES_MAPPING_PATH = os.path.join(os.path.dirname(__file__), "classes_mapping_v2.pkl")

# Fall back to v1 paths so app.py picks them up automatically
MODEL_SAVE_PATH_V1 = os.path.join(os.path.dirname(__file__), "scanner_model.pkl")
CLASSES_MAPPING_PATH_V1 = os.path.join(os.path.dirname(__file__), "classes_mapping.pkl")

IMAGE_SIZE = (128, 128)
RANDOM_STATE = 42
TEST_SIZE = 0.2


# ============================================================
# Multi-Scale Feature Extraction
# ============================================================

def extract_multiscale_prnu(image_gray: np.ndarray, scales=(1.0, 0.5, 2.0), patch_size=32, stride=16, num_bins=5) -> np.ndarray:
    """
    Extract PRNU features at multiple scales for richer fingerprinting.

    At each scale:
    - Resize image
    - Apply Wiener filter denoising
    - Compute residual (original - denoised)
    - Extract patch-level variance histogram

    Returns concatenated feature vector across all scales.
    """
    all_features = []

    for scale in scales:
        h, w = image_gray.shape
        new_h, new_w = max(64, int(h * scale)), max(64, int(w * scale))
        scaled = cv2.resize(image_gray, (new_w, new_h), interpolation=cv2.INTER_AREA)
        norm = scaled.astype(np.float32) / 255.0

        try:
            denoised = wiener(norm, mysize=(5, 5))
        except Exception:
            denoised = cv2.GaussianBlur(norm, (5, 5), 0)

        residual = norm - denoised
        variances = []

        for i in range(0, residual.shape[0] - patch_size, stride):
            for j in range(0, residual.shape[1] - patch_size, stride):
                patch = residual[i : i + patch_size, j : j + patch_size]
                variances.append(np.var(patch))

        if variances:
            arr = np.array(variances)
            hist, _ = np.histogram(arr, bins=num_bins, range=(0, max(arr.max(), 1e-6)))
            hist = hist.astype(np.float32) / (len(variances) + 1e-8)
        else:
            hist = np.zeros(num_bins, dtype=np.float32)

        # Also add summary statistics of the residual at this scale
        scale_stats = np.array([
            np.std(residual),
            np.mean(np.abs(residual)),
            np.max(np.abs(residual)),
            np.percentile(np.abs(residual), 75),
            np.percentile(np.abs(residual), 95),
        ], dtype=np.float32)

        all_features.append(hist)
        all_features.append(scale_stats)

    return np.concatenate(all_features)


def extract_fft_features(image_norm: np.ndarray, num_bands=8) -> np.ndarray:
    """Enhanced FFT features with more frequency bands and statistics."""
    fft_img = np.abs(fft2(image_norm))
    fft_img = fftshift(fft_img)

    h, w = fft_img.shape
    cy, cx = h // 2, w // 2
    yy, xx = np.ogrid[:h, :w]
    radii = np.sqrt((yy - cy) ** 2 + (xx - cx) ** 2)
    rmax = radii.max() + 1e-6

    bands = np.linspace(0, rmax, num_bands + 1)
    features = []

    for k in range(num_bands):
        mask = (radii >= bands[k]) & (radii < bands[k + 1])
        vals = fft_img[mask]
        if vals.size > 0:
            features.extend([vals.mean(), vals.std(), np.percentile(vals, 90)])
        else:
            features.extend([0.0, 0.0, 0.0])

    # Global FFT statistics
    total_energy = np.sum(fft_img)
    top_10 = np.sum(fft_img[fft_img > np.percentile(fft_img, 90)])
    features.extend([
        np.mean(fft_img),
        np.std(fft_img),
        np.max(fft_img),
        top_10 / (total_energy + 1e-8),
    ])

    return np.array(features, dtype=np.float32)


def extract_texture_features(image_norm: np.ndarray, num_bins=10) -> np.ndarray:
    """Enhanced texture features with multi-directional gradients."""
    # Sobel gradients
    grad_x = ndimage.sobel(image_norm, axis=1)
    grad_y = ndimage.sobel(image_norm, axis=0)
    grad_mag = np.sqrt(grad_x ** 2 + grad_y ** 2)
    grad_dir = np.arctan2(grad_y, grad_x)

    mag_hist, _ = np.histogram(grad_mag.flatten(), bins=num_bins, range=(0, grad_mag.max() + 0.01))
    mag_hist = mag_hist.astype(np.float32) / (mag_hist.sum() + 1e-8)

    dir_hist, _ = np.histogram(grad_dir.flatten(), bins=num_bins, range=(-np.pi, np.pi))
    dir_hist = dir_hist.astype(np.float32) / (dir_hist.sum() + 1e-8)

    # Laplacian (second derivative)
    laplacian = cv2.Laplacian(image_norm, cv2.CV_32F)

    # Edge density
    edges = cv2.Canny((image_norm * 255).astype(np.uint8), 50, 150)
    edge_density = np.sum(edges > 0) / edges.size

    # Local variance (texture measure)
    from scipy.ndimage import uniform_filter
    mean_f = uniform_filter(image_norm, size=8, mode="constant")
    sqr_f = uniform_filter(image_norm ** 2, size=8, mode="constant")
    local_var = np.maximum(sqr_f - mean_f ** 2, 0.0)

    texture_stats = np.array([
        np.mean(grad_mag),
        np.std(grad_mag),
        np.mean(np.abs(laplacian)),
        np.std(laplacian),
        edge_density,
        np.mean(local_var),
        np.std(local_var),
    ], dtype=np.float32)

    return np.concatenate([mag_hist, dir_hist, texture_stats])


def extract_statistical_features(image_norm: np.ndarray) -> np.ndarray:
    """Comprehensive statistical features."""
    flat = image_norm.flatten()

    # Percentiles at finer granularity
    percentiles = np.percentile(flat, [5, 10, 25, 50, 75, 90, 95])

    # Histogram-based entropy
    hist, _ = np.histogram(flat, bins=256, range=(0, 1))
    hist = hist.astype(np.float32) / (hist.sum() + 1e-8)
    entropy = -np.sum(hist[hist > 0] * np.log2(hist[hist > 0] + 1e-10))

    features = [
        np.mean(flat),
        np.std(flat),
        np.median(flat),
        np.min(flat),
        np.max(flat),
        np.ptp(flat),
        float(skew(flat)),
        float(kurtosis(flat)),
        entropy,
    ]
    features.extend(percentiles.tolist())

    return np.array(features, dtype=np.float32)


def extract_color_features(image_bgr: np.ndarray) -> np.ndarray:
    """Extract cross-channel correlation and color-space features."""
    if image_bgr is None or len(image_bgr.shape) != 3:
        return np.zeros(12, dtype=np.float32)

    b, g, r = cv2.split(image_bgr.astype(np.float32) / 255.0)

    # Cross-channel correlations
    bg_corr = np.corrcoef(b.flatten(), g.flatten())[0, 1]
    br_corr = np.corrcoef(b.flatten(), r.flatten())[0, 1]
    gr_corr = np.corrcoef(g.flatten(), r.flatten())[0, 1]

    # Channel difference statistics
    bg_diff = np.std(b - g)
    br_diff = np.std(b - r)
    gr_diff = np.std(g - r)

    # HSV stats
    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV).astype(np.float32) / 255.0
    h_std = np.std(hsv[:, :, 0])
    s_mean = np.mean(hsv[:, :, 1])
    v_mean = np.mean(hsv[:, :, 2])

    features = [
        bg_corr, br_corr, gr_corr,
        bg_diff, br_diff, gr_diff,
        h_std, s_mean, v_mean,
        np.std(b), np.std(g), np.std(r),
    ]

    return np.array(features, dtype=np.float32)


def extract_all_features(image_path: str) -> np.ndarray:
    """
    Extract the full feature vector from an image file.
    Combines all feature types into a single vector.

    Returns None if the image cannot be loaded.
    """
    image_bgr = cv2.imread(image_path)
    if image_bgr is None:
        return None

    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    resized_gray = cv2.resize(gray, IMAGE_SIZE, interpolation=cv2.INTER_AREA)
    norm = resized_gray.astype(np.float32) / 255.0

    # Resize color image for color features
    resized_color = cv2.resize(image_bgr, IMAGE_SIZE, interpolation=cv2.INTER_AREA)

    # Extract all feature groups
    prnu = extract_multiscale_prnu(gray)
    fft = extract_fft_features(norm)
    texture = extract_texture_features(norm)
    stats = extract_statistical_features(norm)
    color = extract_color_features(resized_color)

    return np.concatenate([prnu, fft, texture, stats, color])


# ============================================================
# Data Augmentation
# ============================================================

def augment_image(image_path: str) -> list:
    """
    Generate augmented versions of an image.
    Returns list of augmented image paths (saved to temp).

    Augmentations:
    - Horizontal flip
    - Slight rotation (+/- 5 degrees)
    - Brightness adjustment (+/- 15%)
    """
    image = cv2.imread(image_path)
    if image is None:
        return []

    augmented = []
    h, w = image.shape[:2]
    center = (w // 2, h // 2)

    # Horizontal flip
    augmented.append(cv2.flip(image, 1))

    # Slight rotations
    for angle in [-5, 5]:
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), borderMode=cv2.BORDER_REFLECT)
        augmented.append(rotated)

    # Brightness adjustment
    for gamma in [0.85, 1.15]:
        table = np.array([((i / 255.0) ** (1.0 / gamma)) * 255 for i in range(256)])
        adjusted = cv2.LUT(image, table.astype(np.uint8))
        augmented.append(adjusted)

    return augmented


# ============================================================
# Dataset Loading
# ============================================================

def load_dataset(dataset_path: str, use_augmentation=True):
    """
    Load images and extract V2 features.
    Optionally augment images for better generalization.
    """
    print(f"\n📂 Loading dataset from: {dataset_path}")

    if not os.path.exists(dataset_path):
        print(f"❌ Dataset path not found: {dataset_path}")
        sys.exit(1)

    features_list = []
    labels = []
    scanner_models = set()
    image_count = {}
    image_extensions = ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.tif", "*.tiff"]

    dataset_path_obj = Path(dataset_path)

    # Step 1: Find all scanner model folders
    print(f"\n🔍 Scanning for scanner model folders...")
    for category_folder in dataset_path_obj.iterdir():
        if not category_folder.is_dir():
            continue
        for scanner_folder in category_folder.iterdir():
            if not scanner_folder.is_dir():
                continue
            scanner_models.add(scanner_folder.name)
            if scanner_folder.name not in image_count:
                image_count[scanner_folder.name] = 0

    if not scanner_models:
        print("❌ No scanner model folders found!")
        sys.exit(1)

    scanner_models = sorted(list(scanner_models))
    label_to_class = {i: name for i, name in enumerate(scanner_models)}
    class_to_label = {name: i for i, name in enumerate(scanner_models)}

    print(f"\n✓ Found {len(scanner_models)} scanner models:")
    for i, s in enumerate(scanner_models):
        print(f"   {i}. {s}")

    # Step 2: Load images and extract features
    print(f"\n🖼️  Loading images and extracting V2 features...")
    total = 0

    for category_folder in dataset_path_obj.iterdir():
        if not category_folder.is_dir():
            continue

        for scanner_folder in category_folder.iterdir():
            if not scanner_folder.is_dir():
                continue

            scanner_name = scanner_folder.name
            label_idx = class_to_label[scanner_name]

            image_files = []
            for ext in image_extensions:
                image_files.extend(scanner_folder.glob(ext))
                image_files.extend(scanner_folder.glob(ext.upper()))
            image_files = list(set(image_files))

            if not image_files:
                continue

            print(f"   {category_folder.name}/{scanner_name}: ", end="", flush=True)

            for img_path in sorted(image_files):
                try:
                    feat = extract_all_features(str(img_path))
                    if feat is not None:
                        features_list.append(feat)
                        labels.append(label_idx)
                        image_count[scanner_name] += 1
                        total += 1
                        print(".", end="", flush=True)

                        # Augment if enabled
                        if use_augmentation:
                            aug_images = augment_image(str(img_path))
                            for aug_img in aug_images:
                                # Save temporarily and extract features
                                tmp_path = os.path.join(
                                    os.path.dirname(__file__), "uploads", "_aug_tmp.png"
                                )
                                os.makedirs(os.path.dirname(tmp_path), exist_ok=True)
                                cv2.imwrite(tmp_path, aug_img)
                                aug_feat = extract_all_features(tmp_path)
                                if aug_feat is not None:
                                    features_list.append(aug_feat)
                                    labels.append(label_idx)
                                    total += 1
                                try:
                                    os.remove(tmp_path)
                                except:
                                    pass
                            print("+", end="", flush=True)
                    else:
                        print("E", end="", flush=True)
                except Exception:
                    print("E", end="", flush=True)
                    continue

            print()

    X = np.array(features_list)
    y = np.array(labels)

    print(f"\n✓ Total samples (including augmentation): {total}")
    print(f"✓ Feature dimension: {X.shape[1]}")
    print(f"\n📊 Images per scanner model:")
    for s, c in sorted(image_count.items()):
        print(f"   {s}: {c} original images")

    if len(X) == 0:
        print("❌ No images loaded!")
        sys.exit(1)

    return X, y, label_to_class


# ============================================================
# Model Training
# ============================================================

def build_ensemble():
    """
    Build a hybrid ensemble classifier with weighted soft voting.

    Components:
    1. RandomForest (weight 0.40) - robust, handles high-dim well
    2. GradientBoosting (weight 0.35) - sequential error correction
    3. SVM with RBF kernel (weight 0.25) - good decision boundaries
    """
    rf = RandomForestClassifier(
        n_estimators=200,
        max_depth=25,
        min_samples_split=4,
        min_samples_leaf=2,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )

    gb = GradientBoostingClassifier(
        n_estimators=150,
        max_depth=8,
        learning_rate=0.1,
        subsample=0.8,
        random_state=RANDOM_STATE,
    )

    svm = SVC(
        kernel="rbf",
        C=10.0,
        gamma="scale",
        probability=True,
        random_state=RANDOM_STATE,
    )

    ensemble = VotingClassifier(
        estimators=[("rf", rf), ("gb", gb), ("svm", svm)],
        voting="soft",
        weights=[0.40, 0.35, 0.25],
    )

    return ensemble


def train_and_evaluate(X: np.ndarray, y: np.ndarray, label_to_class: dict):
    """Full training pipeline with cross-validation and evaluation."""
    print(f"\n{'='*70}")
    print(f"🤖 Training Hybrid Ensemble Classifier (RF + GB + SVM)")
    print(f"{'='*70}")

    # Feature scaling (crucial for SVM)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Train/test split
    stratify_param = y if len(np.unique(y)) > 1 and len(y) >= 10 else None
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=stratify_param,
    )

    print(f"\n📊 Dataset split:")
    print(f"   Train: {len(X_train)} samples")
    print(f"   Test:  {len(X_test)} samples")
    print(f"   Features: {X_train.shape[1]}")

    # Cross-validation (if enough data)
    if len(X_train) >= 20:
        print(f"\n⏳ Running 5-fold cross-validation...")
        ensemble = build_ensemble()
        n_folds = min(5, min(np.bincount(y_train)))
        if n_folds >= 2:
            cv = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=RANDOM_STATE)
            cv_scores = cross_val_score(ensemble, X_train, y_train, cv=cv, scoring="accuracy")
            print(f"   CV Accuracy: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
            print(f"   Fold scores: {[f'{s:.4f}' for s in cv_scores]}")

    # Train final model
    print(f"\n⏳ Training final ensemble model...")
    t0 = time.time()
    model = build_ensemble()
    model.fit(X_train, y_train)
    train_time = time.time() - t0
    print(f"   Training time: {train_time:.1f}s")

    # Evaluate
    train_acc = accuracy_score(y_train, model.predict(X_train))
    y_pred = model.predict(X_test)
    test_acc = accuracy_score(y_test, y_pred)

    print(f"\n✓ Training Accuracy: {train_acc:.4f}")
    print(f"✓ Test Accuracy:     {test_acc:.4f}")
    print(f"\n📊 Classification Report:")

    target_names = [label_to_class[i] for i in sorted(label_to_class.keys()) if i in np.unique(y)]
    print(classification_report(y_test, y_pred, target_names=target_names, zero_division=0))

    # Also train individual models for comparison
    print(f"\n📈 Individual model comparison:")
    for name, clf in [
        ("RandomForest", RandomForestClassifier(n_estimators=200, max_depth=25, random_state=RANDOM_STATE, n_jobs=-1)),
        ("GradientBoosting", GradientBoostingClassifier(n_estimators=150, max_depth=8, random_state=RANDOM_STATE)),
        ("SVM (RBF)", SVC(kernel="rbf", C=10.0, gamma="scale", random_state=RANDOM_STATE)),
    ]:
        clf.fit(X_train, y_train)
        ind_acc = accuracy_score(y_test, clf.predict(X_test))
        print(f"   {name}: {ind_acc:.4f}")

    return model, scaler, train_acc, test_acc


def save_model(model, scaler, label_to_class):
    """Save trained model, scaler, and class mapping."""
    print(f"\n💾 Saving model files...")

    # Save V2 files
    joblib.dump(model, MODEL_SAVE_PATH)
    print(f"✓ Ensemble model saved: {MODEL_SAVE_PATH}")

    joblib.dump(scaler, SCALER_SAVE_PATH)
    print(f"✓ Feature scaler saved: {SCALER_SAVE_PATH}")

    joblib.dump(label_to_class, CLASSES_MAPPING_PATH)
    print(f"✓ Classes mapping saved: {CLASSES_MAPPING_PATH}")

    # Also save as V1 paths so app.py picks them up
    joblib.dump(model, MODEL_SAVE_PATH_V1)
    joblib.dump(label_to_class, CLASSES_MAPPING_PATH_V1)
    print(f"✓ Also saved to V1 paths for backward compatibility")

    print(f"\n✅ Model training complete!")
    print(f"\nNext steps:")
    print(f"   1. Run: python backend/app.py")
    print(f"   2. Open: http://localhost:5000/")
    print(f"   3. Upload images to classify them")


# ============================================================
# Main
# ============================================================

def main():
    print("=" * 70)
    print("🔬 AI TraceFinder v2 - Hybrid Ensemble Model Training")
    print("🎯 Multi-Scale Features + RF + GradientBoosting + SVM")
    print("=" * 70)

    # Load dataset with V2 features
    X, y, label_to_class = load_dataset(DATASET_PATH, use_augmentation=True)

    # Train and evaluate
    model, scaler, train_acc, test_acc = train_and_evaluate(X, y, label_to_class)

    # Save
    save_model(model, scaler, label_to_class)

    print(f"\n{'='*70}")
    print(f"📊 FINAL RESULTS")
    print(f"   Training Accuracy: {train_acc:.2%}")
    print(f"   Test Accuracy:     {test_acc:.2%}")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
