# 🧠 AI TraceFinder - Model Improvement Guide

## Executive Summary
This guide provides actionable strategies to improve scanner identification accuracy, detection rates, and overall model performance from 82% to target of 92%+.

---

## Current Model Architecture

### Existing Pipeline
1. **Image Preprocessing**
   - Resize to 256×256
   - Normalize pixel values
   - Apply Gaussian blur for noise reduction

2. **Feature Extraction**
   - PRNU analysis (Photo Response Non-Uniformity)
   - FFT analysis (frequency domain)
   - Texture features (LBP - Local Binary Patterns)
   - Statistical moments and entropy
   - Color channel analysis

3. **Classification**
   - Random Forest ensemble (scikit-learn)
   - ~15 scanner categories
   - Single model architecture

---

## Strategy 1: Advanced Feature Engineering

### A. Implement Multi-Scale PRNU Analysis
```python
# Current: Single-scale PRNU
# Improved: Multi-scale PRNU

def extract_multiscale_prnu(image):
    """Extract PRNU at different scales for robustness"""
    prnu_features = []

    # Extract PRNU at original scale
    prnu_orig = extract_prnu(image, scale=1.0)
    prnu_features.extend(prnu_orig)

    # Extract at 0.5x scale
    img_half = cv2.resize(image, (image.shape[1]//2, image.shape[0]//2))
    prnu_half = extract_prnu(img_half, scale=0.5)
    prnu_features.extend(prnu_half)

    # Extract at 2x scale
    img_double = cv2.resize(image, (image.shape[1]*2, image.shape[0]*2))
    prnu_double = extract_prnu(img_double, scale=2.0)
    prnu_features.extend(prnu_double)

    return np.array(prnu_features)
```

**Expected Improvement**: +3-5% accuracy

### B. Implement Color Channel Cross-Correlation
```python
def extract_color_channel_features(image):
    """Analyze color channel relationships"""
    b, g, r = cv2.split(image)

    # Cross-correlation between channels
    corr_rg = np.correlate(r.flatten(), g.flatten())
    corr_rb = np.correlate(r.flatten(), b.flatten())
    corr_gb = np.correlate(g.flatten(), b.flatten())

    # FFT comparison between channels
    fft_r = np.abs(np.fft.fft2(r))
    fft_g = np.abs(np.fft.fft2(g))
    fft_b = np.abs(np.fft.fft2(b))

    # Extract differences (scanners have distinct channel signatures)
    return np.hstack([
        np.array([corr_rg.max(), corr_rb.max(), corr_gb.max()]),
        np.array([np.std(fft_r - fft_g), np.std(fft_r - fft_b)])
    ])
```

**Expected Improvement**: +2-3% accuracy

### C. Edge and Gradient Enhancement
```python
def extract_edge_gradient_features(image):
    """Enhanced edge and gradient analysis"""
    # Edges at multiple scales
    edges_small = cv2.Canny(image, 50, 150)
    edges_large = cv2.Canny(image, 100, 300)

    # Gradients
    sobelx = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)

    # Spatial frequency patterns
    laplacian = cv2.Laplacian(image, cv2.CV_64F)

    return np.hstack([
        np.std(edges_small), np.max(edges_small),
        np.std(edges_large), np.max(edges_large),
        np.std(sobelx), np.std(sobely),
        np.std(laplacian), np.max(laplacian)
    ])
```

**Expected Improvement**: +1-2% accuracy

---

## Strategy 2: Implement Ensemble Methods

### A. Hybrid Classification Approach
```python
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler

class HybridScannerClassifier:
    def __init__(self):
        # Multiple diverse models
        self.rf_model = RandomForestClassifier(n_estimators=200, max_depth=20)
        self.gb_model = GradientBoostingClassifier(n_estimators=150, learning_rate=0.05)
        self.svm_model = SVC(kernel='rbf', probability=True)
        self.scaler = StandardScaler()

    def fit(self, X, y):
        X_scaled = self.scaler.fit_transform(X)
        self.rf_model.fit(X, y)
        self.gb_model.fit(X, y)
        self.svm_model.fit(X_scaled, y)

    def predict(self, X):
        X_scaled = self.scaler.transform(X)

        # Get predictions from all models
        rf_pred = self.rf_model.predict_proba(X)
        gb_pred = self.gb_model.predict_proba(X)
        svm_pred = self.svm_model.predict_proba(X_scaled)

        # Weighted ensemble voting (weights from CV performance)
        ensemble_pred = (0.4 * rf_pred + 0.35 * gb_pred + 0.25 * svm_pred)

        return np.argmax(ensemble_pred, axis=1)

    def predict_proba(self, X):
        X_scaled = self.scaler.transform(X)
        rf_pred = self.rf_model.predict_proba(X)
        gb_pred = self.gb_model.predict_proba(X)
        svm_pred = self.svm_model.predict_proba(X_scaled)
        return (0.4 * rf_pred + 0.35 * gb_pred + 0.25 * svm_pred)
```

**Expected Improvement**: +4-6% accuracy

### B. Per-Class Confidence Adjustment
```python
def calibrate_confidence_thresholds(model, val_X, val_y):
    """Calibrate per-class confidence for balanced predictions"""

    probas = model.predict_proba(val_X)
    predictions = np.argmax(probas, axis=1)

    # Calculate per-class statistics
    class_thresholds = {}
    for class_id in np.unique(val_y):
        class_mask = val_y == class_id
        class_probas = probas[class_mask, class_id]

        # Use 70th percentile as threshold
        threshold = np.percentile(class_probas, 70)
        class_thresholds[class_id] = threshold

    return class_thresholds
```

**Expected Improvement**: +1-2% accuracy

---

## Strategy 3: Deep Learning Integration

### A. Fine-Tuned CNN for Feature Extraction
```python
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout

def create_scanner_model():
    """Create fine-tuned CNN for scanner identification"""

    # Load pre-trained MobileNetV2
    base_model = MobileNetV2(
        input_shape=(256, 256, 3),
        include_top=False,
        weights='imagenet'
    )

    # Freeze base layers
    base_model.trainable = False

    # Add custom layers
    model = tf.keras.Sequential([
        base_model,
        GlobalAveragePooling2D(),
        Dense(512, activation='relu'),
        Dropout(0.5),
        Dense(256, activation='relu'),
        Dropout(0.3),
        Dense(15, activation='softmax')  # 15 scanner types
    ])

    # Compile
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
        loss='categorical_crossentropy',
        metrics=['accuracy', tf.keras.metrics.F1Score()]
    )

    return model
```

**Expected Improvement**: +5-8% accuracy

### B. Data Augmentation Strategy
```python
from tensorflow.keras.preprocessing.image import ImageDataGenerator

def create_augmentation_pipeline():
    """Create data augmentation for robustness"""

    return ImageDataGenerator(
        rotation_range=15,
        width_shift_range=0.1,
        height_shift_range=0.1,
        zoom_range=0.2,
        horizontal_flip=True,
        brightness_range=[0.8, 1.2],
        fill_mode='nearest',
        shear_range=0.1
    )
```

**Expected Improvement**: +2-3% accuracy due to robust training

---

## Strategy 4: Optimize Training Process

### A. K-Fold Cross-Validation
```python
from sklearn.model_selection import StratifiedKFold

def perform_kfold_training(X, y, n_splits=5):
    """K-fold validation for robust model evaluation"""

    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    scores = []

    for fold, (train_idx, val_idx) in enumerate(skf.split(X, y)):
        X_train, X_val = X[train_idx], X[val_idx]
        y_train, y_val = y[train_idx], y[val_idx]

        model = HybridScannerClassifier()
        model.fit(X_train, y_train)

        score = model.score(X_val, y_val)
        scores.append(score)
        print(f"Fold {fold+1}: {score:.4f}")

    print(f"Mean Accuracy: {np.mean(scores):.4f} (+/- {np.std(scores):.4f})")
    return model, scores
```

### B. Hyperparameter Optimization
```python
from sklearn.model_selection import GridSearchCV

def optimize_hyperparameters(X_train, y_train):
    """Grid search for optimal hyperparameters"""

    param_grid = {
        'n_estimators': [100, 150, 200],
        'max_depth': [15, 20, 25],
        'min_samples_split': [5, 10, 15],
        'learning_rate': [0.01, 0.05, 0.1]
    }

    rf = RandomForestClassifier(random_state=42)
    grid_search = GridSearchCV(rf, param_grid, cv=5, n_jobs=-1, verbose=1)
    grid_search.fit(X_train, y_train)

    print(f"Best parameters: {grid_search.best_params_}")
    print(f"Best CV score: {grid_search.best_score_:.4f}")

    return grid_search.best_estimator_
```

**Expected Improvement**: +1-3% accuracy

---

## Strategy 5: Specialized Detectors

### A. Implement Camera/Scanner Category Specific Models
```python
class CategorySpecificClassifier:
    def __init__(self):
        # Separate models for different scanner types
        self.dslr_model = RandomForestClassifier(n_estimators=100)
        self.smartphone_model = RandomForestClassifier(n_estimators=100)
        self.scanner_model = RandomForestClassifier(n_estimators=100)

    def fit(self, X, y, categories):
        """categories: list indicating device type for each sample"""
        for idx, category in enumerate(np.unique(categories)):
            mask = categories == category
            if category == 'dslr':
                self.dslr_model.fit(X[mask], y[mask])
            elif category == 'smartphone':
                self.smartphone_model.fit(X[mask], y[mask])
            else:
                self.scanner_model.fit(X[mask], y[mask])
```

**Expected Improvement**: +2-3% accuracy

---

## Implementation Roadmap

### Phase 1: Feature Engineering (Week 1-2)
- [ ] Implement multi-scale PRNU
- [ ] Add color channel features
- [ ] Add edge gradient features
- [ ] Retrain and test (Target: 85%)

### Phase 2: Ensemble Methods (Week 2-3)
- [ ] Train Random Forest ensemble
- [ ] Train Gradient Boosting model
- [ ] Train SVM classifier
- [ ] Implement weighted voting (Target: 88%)

### Phase 3: Deep Learning (Week 3-4)
- [ ] Fine-tune MobileNetV2
- [ ] Implement data augmentation
- [ ] Train CNN model (Target: 90%)

### Phase 4: Optimization (Week 4-5)
- [ ] Hyperparameter tuning
- [ ] K-fold cross-validation
- [ ] Performance benchmarking (Target: 92%+)

---

## Evaluation Metrics

### Track During Development
```python
from sklearn.metrics import precision_recall_fscore_support, confusion_matrix

def detailed_evaluation(y_true, y_pred, class_names):
    """Comprehensive model evaluation"""

    # Per-class metrics
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average=None
    )

    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred)

    # Overall metrics
    accuracy = np.mean(y_true == y_pred)

    print(f"Overall Accuracy: {accuracy:.4f}")
    print("\nPer-Class Performance:")
    for i, name in enumerate(class_names):
        print(f"{name}: P={precision[i]:.3f}, R={recall[i]:.3f}, F1={f1[i]:.3f}")

    return {
        'accuracy': accuracy,
        'per_class_precision': precision,
        'per_class_recall': recall,
        'per_class_f1': f1,
        'confusion_matrix': cm
    }
```

---

## Expected Results

| Strategy | Individual Gain | Cumulative |
|----------|-----------------|-----------|
| Multi-scale PRNU | +3-5% | 85-87% |
| + Ensemble Methods | +4-6% | 89-93% |
| + Deep Learning | +2-4% | 91-97% |
| + Optimization | +1-2% | 92-98% |

**Target**: **92%+ accuracy** achievable by combining all strategies

---

## Testing & Validation

### Create Comprehensive Test Set
```python
def create_test_suite(test_images_dir):
    """Create diverse test cases"""

    test_cases = {
        'clean_images': [],
        'jpeg_compressed': [],
        'resized': [],
        'cropped': [],
        'noisy': [],
        'rotated': []
    }

    # Build test cases for each category
    # Test robustness across variations

    return test_cases
```

---

## Performance Benchmarking

### Track metrics over time
```python
import csv
from datetime import datetime

def log_performance(model_version, accuracy, f1_score, inference_time):
    """Log model performance for tracking"""

    with open('model_performance.csv', 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['timestamp', 'version', 'accuracy', 'f1', 'time'])
        writer.writerow({
            'timestamp': datetime.now(),
            'version': model_version,
            'accuracy': accuracy,
            'f1': f1_score,
            'time': inference_time
        })
```

---

**Next Steps**:
1. Run baseline evaluation of current model
2. Implement Phase 1 features
3. Validate improvements
4. Move to Phase 2

**Last Updated**: March 30, 2026
