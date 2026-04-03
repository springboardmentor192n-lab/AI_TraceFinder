"""
SUPATLANTIQUE Dataset Exploration Guide
Practical code examples to understand the dataset structure
"""

import os
import cv2
import numpy as np
from pathlib import Path
import json

# ============================================================================
# 1. DATASET STRUCTURE EXPLORATION
# ============================================================================

class DatasetExplorer:
    """Explore SUPATLANTIQUE dataset structure"""
    
    def __init__(self, dataset_path):
        self.dataset_path = Path(dataset_path)
    
    def explore_structure(self):
        """Print dataset folder structure"""
        print("SUPATLANTIQUE Dataset Structure:")
        print("=" * 70)
        
        for folder in self.dataset_path.iterdir():
            if folder.is_dir():
                num_items = len(list(folder.rglob("*")))
                print(f"\n📁 {folder.name}/")
                print(f"   Items: {num_items}")
                
                # Show subfolders
                subfolders = [f for f in folder.iterdir() if f.is_dir()]
                if subfolders:
                    print(f"   Subfolders: {len(subfolders)}")
                    for sf in subfolders[:3]:  # Show first 3
                        print(f"      - {sf.name}")
                    if len(subfolders) > 3:
                        print(f"      ... and {len(subfolders)-3} more")
                
                # Show file types
                files = list(folder.rglob("*.*"))
                if files:
                    file_types = {}
                    for f in files:
                        ext = f.suffix.lower()
                        file_types[ext] = file_types.get(ext, 0) + 1
                    
                    print(f"   File types:")
                    for ext, count in sorted(file_types.items()):
                        print(f"      {ext}: {count} files")
    
    def get_scanner_list(self):
        """Extract list of scanners from folder names"""
        originals_path = self.dataset_path / "Originals"
        scanners = []
        
        if originals_path.exists():
            for folder in originals_path.iterdir():
                if folder.is_dir():
                    scanners.append(folder.name)
        
        print(f"\nScanner Models Found ({len(scanners)}):")
        for i, scanner in enumerate(scanners, 1):
            print(f"  {i}. {scanner}")
        
        return scanners
    
    def get_image_count_by_scanner(self):
        """Count images per scanner"""
        counts = {}
        originals_path = self.dataset_path / "Originals"
        
        if originals_path.exists():
            for scanner_folder in originals_path.iterdir():
                if scanner_folder.is_dir():
                    images = len(list(scanner_folder.glob("*.jpg"))) + \
                            len(list(scanner_folder.glob("*.png")))
                    counts[scanner_folder.name] = images
        
        print(f"\nImages per Scanner:")
        print("=" * 50)
        for scanner, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {scanner:30} : {count:4} images")
        
        return counts

# ============================================================================
# 2. IMAGE LOADING AND BASIC ANALYSIS
# ============================================================================

class ImageAnalyzer:
    """Load and analyze scanner images"""
    
    @staticmethod
    def load_image(path, as_gray=False):
        """Load image with error handling"""
        try:
            if as_gray:
                img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
            else:
                img = cv2.imread(str(path), cv2.IMREAD_COLOR)
            
            if img is None:
                raise ValueError(f"Failed to load: {path}")
            return img
        except Exception as e:
            print(f"Error loading {path}: {e}")
            return None
    
    @staticmethod
    def analyze_image(img, name="Image"):
        """Print basic image statistics"""
        if img is None:
            return
        
        print(f"\n{name} Analysis:")
        print(f"  Shape: {img.shape}")
        print(f"  Data type: {img.dtype}")
        print(f"  Min value: {img.min()}")
        print(f"  Max value: {img.max()}")
        print(f"  Mean: {img.mean():.2f}")
        print(f"  Std Dev: {img.std():.2f}")
        print(f"  Size: {img.nbytes / (1024*1024):.2f} MB")
    
    @staticmethod
    def compare_scanners(dataset_path, scanners_to_compare=None):
        """Compare images from different scanners"""
        originals_path = Path(dataset_path) / "Originals"
        
        if scanners_to_compare is None:
            # Get first 2 scanners
            available = [f for f in originals_path.iterdir() if f.is_dir()]
            scanners_to_compare = [s.name for s in available[:2]]
        
        print(f"\nComparing Scanners: {scanners_to_compare}")
        print("=" * 70)
        
        for scanner in scanners_to_compare:
            scanner_path = originals_path / scanner
            images = list(scanner_path.glob("*.jpg"))[:1]  # First image
            
            if images:
                print(f"\n{scanner}:")
                img = ImageAnalyzer.load_image(images[0], as_gray=True)
                ImageAnalyzer.analyze_image(img, scanner)

# ============================================================================
# 3. RESIDUAL EXTRACTION EXAMPLES
# ============================================================================

class ResidualExtractor:
    """Extract scanner fingerprints from images"""
    
    @staticmethod
    def extract_laplacian_residual(img):
        """
        Extract residual using Laplacian filter
        Residual = Image - Gaussian Blur
        """
        if len(img.shape) == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        img = img.astype(np.float32)
        
        # High-pass filter: Laplacian
        blurred = cv2.GaussianBlur(img, (5, 5), 1.5)
        residual = img - blurred
        
        return residual
    
    @staticmethod
    def extract_high_pass_residual(img):
        """
        Extract residual using high-pass filter kernel
        """
        if len(img.shape) == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        img = img.astype(np.float32)
        
        # High-pass kernel
        kernel = np.array([[-1, -1, -1],
                          [-1,  8, -1],
                          [-1, -1, -1]], dtype=np.float32)
        
        residual = cv2.filter2D(img, -1, kernel)
        
        return residual
    
    @staticmethod
    def analyze_residual(residual, name="Residual"):
        """Analyze residual properties"""
        print(f"\n{name} Analysis:")
        print(f"  Shape: {residual.shape}")
        print(f"  Min: {residual.min():.4f}")
        print(f"  Max: {residual.max():.4f}")
        print(f"  Mean: {residual.mean():.4f}")
        print(f"  Std Dev: {residual.std():.4f}")
        print(f"  Energy: {np.sum(residual**2):.2f}")

# ============================================================================
# 4. FREQUENCY DOMAIN ANALYSIS
# ============================================================================

class FrequencyAnalyzer:
    """Analyze frequency domain characteristics"""
    
    @staticmethod
    def compute_fft(img):
        """Compute 2D FFT"""
        if len(img.shape) == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        img = img.astype(np.float32)
        fft_result = np.fft.fft2(img)
        magnitude = np.abs(fft_result)
        phase = np.angle(fft_result)
        
        return magnitude, phase
    
    @staticmethod
    def analyze_spectrum(magnitude, name="Spectrum"):
        """Analyze FFT magnitude spectrum"""
        # Log scale for better visualization
        log_magnitude = np.log1p(magnitude)
        
        print(f"\n{name} Analysis:")
        print(f"  Min magnitude: {magnitude.min():.4f}")
        print(f"  Max magnitude: {magnitude.max():.4f}")
        print(f"  Mean magnitude: {magnitude.mean():.4f}")
        print(f"  DC component: {magnitude[0, 0]:.4f}")
        
        # Compute radial average (fingerprint in frequency)
        h, w = magnitude.shape
        cy, cx = h // 2, w // 2
        
        # Create radial distance map
        y = np.arange(h) - cy
        x = np.arange(w) - cx
        X, Y = np.meshgrid(x, y)
        R = np.sqrt(X**2 + Y**2)
        
        return log_magnitude, R

# ============================================================================
# 5. TAMPERED REGION EXPLORATION
# ============================================================================

class TamperedImageExplorer:
    """Explore tampered images and masks"""
    
    @staticmethod
    def explore_tampered_categories(dataset_path):
        """List tampering categories and counts"""
        tampered_path = Path(dataset_path) / "Tampered_images"
        
        if not tampered_path.exists():
            print("Tampered_images folder not found")
            return
        
        print("\nTampering Categories:")
        print("=" * 70)
        
        for category in tampered_path.iterdir():
            if category.is_dir():
                images = list(category.glob("*.jpg")) + list(category.glob("*.png"))
                masks = list(category.glob("*mask*"))
                
                print(f"\n{category.name}:")
                print(f"  Images: {len(images)}")
                print(f"  Masks: {len(masks)}")
    
    @staticmethod
    def load_tampered_pair(image_path, mask_path=None):
        """Load tampered image and its mask"""
        image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
        
        mask = None
        if mask_path and os.path.exists(mask_path):
            mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
        
        return image, mask
    
    @staticmethod
    def analyze_tampering_pattern(image, mask=None):
        """Analyze tampering pattern in image"""
        print(f"\nTampering Analysis:")
        print(f"  Image shape: {image.shape}")
        
        if mask is not None:
            print(f"  Mask shape: {mask.shape}")
            
            # Calculate tampered percentage
            tampered_pixels = np.sum(mask > 128)
            total_pixels = mask.size
            percentage = (tampered_pixels / total_pixels) * 100
            
            print(f"  Tampered pixels: {tampered_pixels}")
            print(f"  Tampered percentage: {percentage:.2f}%")

# ============================================================================
# 6. FEATURE EXTRACTION BASICS
# ============================================================================

class FeatureExtractor:
    """Extract features from residuals for classification"""
    
    @staticmethod
    def extract_statistical_features(residual):
        """Extract statistical features from residual"""
        features = {
            'mean': np.mean(residual),
            'std': np.std(residual),
            'variance': np.var(residual),
            'skewness': float(3 * (np.mean(residual) - np.median(residual)) / np.std(residual)),
            'min': np.min(residual),
            'max': np.max(residual),
            'range': np.max(residual) - np.min(residual),
        }
        
        return features
    
    @staticmethod
    def extract_histogram_features(residual, bins=256):
        """Extract histogram-based features"""
        hist, _ = np.histogram(residual, bins=bins)
        hist = hist / hist.sum()  # Normalize
        
        features = {
            'entropy': -np.sum(hist[hist > 0] * np.log2(hist[hist > 0])),
            'hist_mean': np.mean(hist),
            'hist_std': np.std(hist),
        }
        
        return features
    
    @staticmethod
    def extract_all_features(image):
        """Extract all feature types"""
        # Extract residual
        residual = ResidualExtractor.extract_laplacian_residual(image)
        
        # Statistical features
        stat_features = FeatureExtractor.extract_statistical_features(residual)
        
        # Histogram features
        hist_features = FeatureExtractor.extract_histogram_features(residual)
        
        # Combine
        all_features = {**stat_features, **hist_features}
        
        return all_features

# ============================================================================
# USAGE EXAMPLES
# ============================================================================

if __name__ == "__main__":
    # Example path (modify to your dataset location)
    dataset_path = r"C:\Users\tejap\Downloads\Trace_finder-20260402T041728Z-1-001\Trace_finder"
    
    # 1. Explore dataset structure
    print("\n" + "="*70)
    print("DATASET EXPLORATION")
    print("="*70)
    
    explorer = DatasetExplorer(dataset_path)
    explorer.explore_structure()
    explorer.get_scanner_list()
    explorer.get_image_count_by_scanner()
    
    # 2. Compare scanners statistically
    print("\n" + "="*70)
    print("IMAGE ANALYSIS")
    print("="*70)
    
    analyzer = ImageAnalyzer()
    analyzer.compare_scanners(dataset_path)
    
    # 3. Explore tampered images
    print("\n" + "="*70)
    print("TAMPERING ANALYSIS")
    print("="*70)
    
    tamper_explorer = TamperedImageExplorer()
    tamper_explorer.explore_tampered_categories(dataset_path)
    
    print("\n" + "="*70)
    print("Dataset exploration complete!")
    print("="*70)
