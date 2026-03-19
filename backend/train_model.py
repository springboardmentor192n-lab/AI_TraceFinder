"""
Machine Learning Model Training Script
Trains a RandomForestClassifier on the dataset
Prepared images are resized to 128x128, converted to grayscale, and flattened

Dataset location: OneDrive/Amrita Vishwa Vidyapeetham-Chennai Campus/dataset/
Classes: Scanner model names (e.g., Canon_DR_C225, Epson_V600, HP_ScanJet, etc.)

Dataset structure:
  dataset/
    Official/
      Canon_DR_C225/
        image1.jpg
      Epson_V600/
        image1.jpg
    Flatfield/
      Canon_DR_C225/
        image1.jpg
      Epson_V600/
        image1.jpg
    Originals/
      HP_ScanJet/
        image1.jpg

Labels extracted: Canon_DR_C225, Epson_V600, HP_ScanJet, etc.
"""

import os
import cv2
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
from pathlib import Path
import sys

# Configuration
DATASET_PATH = r"C:\Users\jayabhuvanesh\OneDrive - Amrita Vishwa Vidyapeetham- Chennai Campus\dataset"
MODEL_SAVE_PATH = os.path.join(os.path.dirname(__file__), "scanner_model.pkl")
CLASSES_MAPPING_PATH = os.path.join(os.path.dirname(__file__), "classes_mapping.pkl")

# Image preprocessing parameters
IMAGE_SIZE = (128, 128)
GRAYSCALE = True

# Model parameters
RANDOM_STATE = 42
TEST_SIZE = 0.2
N_ESTIMATORS = 100


def load_dataset(dataset_path):
    """
    Load images from dataset folders with hierarchical structure.
    
    Dataset structure (2-level hierarchy):
      dataset/
        Category1/  (Official, Flatfield, Originals, etc.)
          ScannerModel1/  <- Extract this as LABEL
            image1.jpg
            image2.jpg
          ScannerModel2/
            image1.jpg
        Category2/
          ScannerModel1/
            image1.jpg
    
    Args:
        dataset_path: Path to dataset root folder
        
    Returns:
        images: List of flattened image arrays
        labels: List of class labels (scanner model indices)
        label_to_class: Dictionary mapping label indices to scanner model names
    """
    print(f"\n📂 Loading dataset from: {dataset_path}")
    
    # Check if path exists
    if not os.path.exists(dataset_path):
        print(f"❌ Dataset path not found: {dataset_path}")
        print(f"✓ Please ensure the dataset is at: {dataset_path}")
        sys.exit(1)
    
    images = []
    labels = []
    scanner_models = set()
    image_count_per_scanner = {}
    
    # Supported image extensions
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tif', '*.tiff']
    
    # Step 1: Find all unique scanner model folders
    print(f"\n🔍 Scanning for scanner model folders...")
    
    dataset_path_obj = Path(dataset_path)
    
    # Iterate through all directories at level 1 (categories)
    for category_folder in dataset_path_obj.iterdir():
        if not category_folder.is_dir():
            continue
        
        category_name = category_folder.name
        print(f"\n   📁 Category: {category_name}")
        
        # Iterate through all directories at level 2 (scanner models)
        for scanner_folder in category_folder.iterdir():
            if not scanner_folder.is_dir():
                continue
            
            scanner_name = scanner_folder.name
            scanner_models.add(scanner_name)
            if scanner_name not in image_count_per_scanner:
                image_count_per_scanner[scanner_name] = 0
    
    if not scanner_models:
        print(f"\n❌ No scanner model folders found in dataset!")
        print(f"   Expected structure: dataset/Category/ScannerModel/images/")
        sys.exit(1)
    
    # Sort scanner models for consistent label ordering
    scanner_models = sorted(list(scanner_models))
    label_to_class = {i: name for i, name in enumerate(scanner_models)}
    class_to_label = {name: i for i, name in enumerate(scanner_models)}
    
    print(f"\n✓ Found {len(scanner_models)} unique scanner models:")
    for i, scanner in enumerate(scanner_models):
        print(f"   {i}. {scanner}")
    
    # Step 2: Load images from scanner model folders
    print(f"\n🖼️  Loading images from all categories and scanner models...")
    total_images = 0
    
    for category_folder in dataset_path_obj.iterdir():
        if not category_folder.is_dir():
            continue
        
        category_name = category_folder.name
        
        for scanner_folder in category_folder.iterdir():
            if not scanner_folder.is_dir():
                continue
            
            scanner_name = scanner_folder.name
            label_idx = class_to_label[scanner_name]
            
            # Find all image files in this scanner folder
            image_files = []
            for ext in image_extensions:
                image_files.extend(scanner_folder.glob(ext))
                image_files.extend(scanner_folder.glob(ext.upper()))
            
            image_files = list(set(image_files))  # Remove duplicates
            
            if not image_files:
                continue
            
            print(f"   {category_name}/{scanner_name}: ", end="", flush=True)
            
            # Process each image
            for image_path in sorted(image_files):
                try:
                    # Read image
                    image = cv2.imread(str(image_path))
                    
                    if image is None:
                        print("E", end="", flush=True)
                        continue
                    
                    # Convert to grayscale
                    if GRAYSCALE:
                        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    else:
                        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    
                    # Resize to standard size
                    image = cv2.resize(image, IMAGE_SIZE, interpolation=cv2.INTER_AREA)
                    
                    # Flatten to 1D array
                    flattened = image.flatten()
                    
                    # Normalize pixel values to [0, 1]
                    flattened = flattened.astype(np.float32) / 255.0
                    
                    # Add to dataset
                    images.append(flattened)
                    labels.append(label_idx)
                    image_count_per_scanner[scanner_name] += 1
                    total_images += 1
                    
                    print(".", end="", flush=True)
                    
                except Exception as e:
                    print("E", end="", flush=True)
                    continue
            
            print()  # New line after each scanner
    
    # Convert to numpy arrays
    images = np.array(images)
    labels = np.array(labels)
        
    
    print(f"\n✓ Total images loaded: {total_images}")
    print(f"✓ Feature dimension: {images.shape[1]}")
    print(f"\n📊 Images per scanner model:")
    for scanner, count in sorted(image_count_per_scanner.items()):
        print(f"   {scanner}: {count} images")
    
    if len(images) == 0:
        print("❌ No images could be loaded from the dataset!")
        sys.exit(1)
    
    return images, labels, label_to_class



def train_model(X_train, y_train, X_test, y_test):
    """
    Train RandomForestClassifier
    
    Args:
        X_train: Training features
        y_train: Training labels
        X_test: Test features
        y_test: Test labels
        
    Returns:
        model: Trained RandomForestClassifier
    """
    print(f"\n🤖 Training RandomForestClassifier...")
    print(f"   - Estimators: {N_ESTIMATORS}")
    print(f"   - Training samples: {len(X_train)}")
    print(f"   - Test samples: {len(X_test)}")
    print(f"   - Feature dimension: {X_train.shape[1]}")
    
    # Initialize and train model
    model = RandomForestClassifier(
        n_estimators=N_ESTIMATORS,
        random_state=RANDOM_STATE,
        n_jobs=-1,  # Use all available cores
        verbose=1,
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2
    )
    
    print("\n⏳ This may take a few minutes...\n")
    model.fit(X_train, y_train)
    
    # Evaluate on training set
    train_accuracy = accuracy_score(y_train, model.predict(X_train))
    print(f"\n✓ Training Accuracy: {train_accuracy:.4f}")
    
    # Evaluate on test set
    y_pred = model.predict(X_test)
    test_accuracy = accuracy_score(y_test, y_pred)
    print(f"✓ Test Accuracy: {test_accuracy:.4f}")
    
    # Detailed classification report
    print(f"\n📊 Classification Report:")
    print(classification_report(y_test, y_pred))
    
    return model, train_accuracy, test_accuracy


def save_model(model, label_to_class):
    """
    Save trained model and class mapping to disk
    
    Args:
        model: Trained classifier
        label_to_class: Dictionary mapping label indices to class names
    """
    print(f"\n💾 Saving model...")
    
    # Save model
    joblib.dump(model, MODEL_SAVE_PATH)
    print(f"✓ Model saved: {MODEL_SAVE_PATH}")
    
    # Save class mapping
    joblib.dump(label_to_class, CLASSES_MAPPING_PATH)
    print(f"✓ Classes mapping saved: {CLASSES_MAPPING_PATH}")
    
    print(f"\n✅ Model training complete!")
    print(f"\nNext steps:")
    print(f"   1. Run: python backend/app.py")
    print(f"   2. Open: http://localhost:5000/")
    print(f"   3. Upload images to classify them")


def main():
    """Main training pipeline"""
    print("=" * 70)
    print("🔬 AI TraceFinder - Machine Learning Model Training")
    print("🎯 Labels: Scanner Model Names (e.g., Canon_DR_C225, Epson_V600)")
    print("=" * 70)
    
    # Load dataset
    images, labels, label_to_class = load_dataset(DATASET_PATH)
    
    # Split dataset
    print(f"\n📊 Splitting dataset...")
    
    # For small datasets, don't use stratification
    stratify_param = None if len(images) < 50 else labels
    test_size_param = min(0.2, max(2, len(images) // 10))  # Use smaller test size for small datasets
    
    X_train, X_test, y_train, y_test = train_test_split(
        images, labels, 
        test_size=test_size_param, 
        random_state=RANDOM_STATE,
        stratify=stratify_param
    )
    print(f"✓ Training set: {len(X_train)} images")
    print(f"✓ Test set: {len(X_test)} images")
    
    # Train model
    model, train_acc, test_acc = train_model(X_train, y_train, X_test, y_test)
    
    # Save model
    save_model(model, label_to_class)
    
    print("\n" + "=" * 70)
    print(f"Accuracy: Training={train_acc:.2%}, Test={test_acc:.2%}")
    print("=" * 70)


if __name__ == "__main__":
    main()
