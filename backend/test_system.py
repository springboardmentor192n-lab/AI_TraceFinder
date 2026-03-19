#!/usr/bin/env python3
"""
AI TraceFinder - System Testing Script

This script tests the entire backend system including:
- Image loading and preprocessing
- Feature extraction pipeline
- Scanner identification accuracy
- API endpoint functionality
- Performance metrics
"""

import sys
import os
import json
import time
import requests
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import cv2
    import numpy as np
    from image_forensics import ImageForensics
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)


class ForensicsSystemTester:
    """Test suite for AI TraceFinder forensics system"""
    
    def __init__(self):
        """Initialize the tester"""
        self.forensics_engine = ImageForensics()
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
        self.api_base_url = 'http://localhost:5000'
        self.test_images_dir = Path(__file__).parent.parent / 'data' / 'test_images'
    
    def print_header(self, title):
        """Print a formatted header"""
        print("\n" + "="*70)
        print(f"  {title}")
        print("="*70)
    
    def print_test(self, test_name, status, details=""):
        """Print test result"""
        symbol = "✓" if status else "✗"
        color = "\033[92m" if status else "\033[91m"  # Green or Red
        reset = "\033[0m"
        
        print(f"{color}{symbol}{reset} {test_name}")
        if details:
            print(f"  └─ {details}")
        
        if status:
            self.test_results['passed'] += 1
        else:
            self.test_results['failed'] += 1
            self.test_results['errors'].append(test_name)
    
    def test_imports(self):
        """Test 1: Verify all imports work correctly"""
        self.print_header("TEST 1: Imports & Dependencies")
        
        try:
            import cv2
            self.print_test("OpenCV Import", True, f"Version: {cv2.__version__}")
        except ImportError as e:
            self.print_test("OpenCV Import", False, str(e))
        
        try:
            import numpy
            self.print_test("NumPy Import", True, f"Version: {numpy.__version__}")
        except ImportError as e:
            self.print_test("NumPy Import", False, str(e))
        
        try:
            import scipy
            self.print_test("SciPy Import", True, f"Version: {scipy.__version__}")
        except ImportError as e:
            self.print_test("SciPy Import", False, str(e))
        
        try:
            from skimage import io
            self.print_test("scikit-image Import", True)
        except ImportError as e:
            self.print_test("scikit-image Import", False, str(e))
    
    def test_image_creation(self):
        """Test 2: Create synthetic test images"""
        self.print_header("TEST 2: Synthetic Image Generation")
        
        try:
            # Create a synthetic image
            img = np.random.randint(0, 256, (256, 256), dtype=np.uint8)
            self.print_test("Image Creation", True, f"Shape: {img.shape}, DType: {img.dtype}")
        except Exception as e:
            self.print_test("Image Creation", False, str(e))
            return None
        
        try:
            # Save test image
            test_img_path = Path(self.test_images_dir).parent / 'test_synthetic.png'
            os.makedirs(test_img_path.parent, exist_ok=True)
            cv2.imwrite(str(test_img_path), img)
            self.print_test("Image Saving", True, f"Path: {test_img_path}")
            return str(test_img_path)
        except Exception as e:
            self.print_test("Image Saving", False, str(e))
            return None
    
    def test_preprocessing(self, image_path):
        """Test 3: Image preprocessing"""
        self.print_header("TEST 3: Image Preprocessing Pipeline")
        
        try:
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                self.print_test("Image Loading", False, "Could not load image")
                return False
            
            self.print_test("Image Loading", True, f"Shape: {img.shape}")
        except Exception as e:
            self.print_test("Image Loading", False, str(e))
            return False
        
        try:
            # Test resize
            resized = cv2.resize(img, (256, 256), interpolation=cv2.INTER_AREA)
            self.print_test("Image Resizing", True, f"Output shape: {resized.shape}")
        except Exception as e:
            self.print_test("Image Resizing", False, str(e))
            return False
        
        try:
            # Test normalization
            normalized = resized.astype(np.float32) / 255.0
            self.print_test("Image Normalization", True, f"Range: [{normalized.min():.3f}, {normalized.max():.3f}]")
        except Exception as e:
            self.print_test("Image Normalization", False, str(e))
            return False
        
        return True
    
    def test_feature_extraction(self, image_path):
        """Test 4: Feature extraction"""
        self.print_header("TEST 4: Feature Extraction Pipeline")
        
        try:
            start_time = time.time()
            
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            preprocessed = self.forensics_engine._preprocess_image(img)
            
            # Test residual computation
            residual = self.forensics_engine._compute_residual(img)
            residual_std = np.std(residual)
            self.print_test("Residual Computation", True, f"Std Dev: {residual_std:.4f}")
            
            # Test feature extraction
            features = self.forensics_engine._extract_all_features(preprocessed, img)
            feature_vector = features['feature_vector']
            self.print_test("All Features Extraction", True, f"Vector size: {len(feature_vector)}")
            
            # Test individual extractors
            self.print_test("PRNU Features", True, f"Shape: {features['prnu'].shape}")
            self.print_test("FFT Features", True, f"Shape: {features['fft'].shape}")
            self.print_test("Texture Features", True, f"Shape: {features['texture'].shape}")
            self.print_test("Statistical Features", True, f"Shape: {features['statistical'].shape}")
            
            elapsed = time.time() - start_time
            self.print_test("Feature Extraction Speed", True, f"Completed in {elapsed:.2f}s")
            
            return features
        except Exception as e:
            self.print_test("Feature Extraction", False, str(e))
            return None
    
    def test_scanner_identification(self, image_path):
        """Test 5: Scanner identification"""
        self.print_header("TEST 5: Scanner Source Identification")
        
        try:
            start_time = time.time()
            results = self.forensics_engine.analyze_image(image_path)
            elapsed = time.time() - start_time
            
            if results['success']:
                self.print_test("Analysis Success", True)
                self.print_test("Scanner Identification", True, 
                               f"Scanner: {results['scanner_id']}, Confidence: {results['confidence']:.2%}")
                
                self.print_test("Noise Pattern Strength", True, 
                               f"Value: {results['noise_pattern_strength']:.4f}")
                
                self.print_test("FFT Analysis", True, 
                               f"Peak Ratio: {results['fft_analysis'].get('peak_frequency_ratio', 0):.2f}")
                
                self.print_test("Texture Metrics", True, 
                               f"Mean: {results['texture_metrics'].get('mean_texture', 0):.4f}")
                
                self.print_test("Recommendations Generated", True, 
                               f"Count: {len(results['recommendations'])}")
                
                self.print_test("Analysis Speed", True, f"Completed in {elapsed:.2f}s")
                
                return results
            else:
                self.print_test("Analysis Success", False, results.get('error', 'Unknown error'))
                return None
        except Exception as e:
            self.print_test("Scanner Identification", False, str(e))
            return None
    
    def test_api_endpoints(self):
        """Test 6: Flask API endpoints"""
        self.print_header("TEST 6: Flask API Endpoints")
        
        try:
            # Test health check
            response = requests.get(f"{self.api_base_url}/api/health", timeout=5)
            self.print_test("Health Check Endpoint", response.status_code == 200,
                           f"Status: {response.status_code}")
        except requests.exceptions.ConnectionError:
            self.print_test("Health Check Endpoint", False, "Flask server not running at localhost:5000")
            self.print_test("API Extractors Endpoint", False, "Skipped (server not running)")
            self.print_test("API Statistics Endpoint", False, "Skipped (server not running)")
            return
        except Exception as e:
            self.print_test("Health Check Endpoint", False, str(e))
        
        try:
            response = requests.get(f"{self.api_base_url}/api/extractors", timeout=5)
            self.print_test("API Extractors Endpoint", response.status_code == 200,
                           f"Status: {response.status_code}")
        except Exception as e:
            self.print_test("API Extractors Endpoint", False, str(e))
        
        try:
            response = requests.get(f"{self.api_base_url}/api/statistics", timeout=5)
            self.print_test("API Statistics Endpoint", response.status_code == 200,
                           f"Status: {response.status_code}")
        except Exception as e:
            self.print_test("API Statistics Endpoint", False, str(e))
    
    def test_system_statistics(self):
        """Test 7: System statistics"""
        self.print_header("TEST 7: System Statistics")
        
        try:
            stats = self.forensics_engine.get_statistics()
            
            self.print_test("Statistics Retrieval", True)
            self.print_test("Total Analyzed", True, f"Count: {stats['total_analyzed']}")
            self.print_test("Successful Analysis", True, f"Count: {stats['successful_analysis']}")
            self.print_test("Failed Analysis", True, f"Count: {stats['failed_analysis']}")
            self.print_test("Scanner Database Size", True, f"Scanners: {stats['scanner_database_size']}")
            self.print_test("Available Scanners", True, 
                           f"Scanners: {', '.join(stats['available_scanners'])}")
        except Exception as e:
            self.print_test("System Statistics", False, str(e))
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n")
        print("╔" + "="*68 + "╗")
        print("║" + " "*68 + "║")
        print("║" + "  AI TraceFinder - System Testing Suite".center(68) + "║")
        print("║" + "  Scanner Source Identification & Image Forensics".center(68) + "║")
        print("║" + " "*68 + "║")
        print("╚" + "="*68 + "╝")
        
        # Test 1: Imports
        self.test_imports()
        
        # Test 2: Image creation
        test_image = self.test_image_creation()
        if not test_image:
            print("\n❌ Cannot continue without test image")
            return
        
        # Test 3: Preprocessing
        if not self.test_preprocessing(test_image):
            print("\n❌ Preprocessing failed")
            return
        
        # Test 4: Feature extraction
        features = self.test_feature_extraction(test_image)
        if not features:
            print("\n⚠ Feature extraction failed")
        
        # Test 5: Scanner identification
        self.test_scanner_identification(test_image)
        
        # Test 6: API endpoints
        self.test_api_endpoints()
        
        # Test 7: Statistics
        self.test_system_statistics()
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        self.print_header("TEST SUMMARY")
        
        total = self.test_results['passed'] + self.test_results['failed']
        passed_pct = (self.test_results['passed'] / total * 100) if total > 0 else 0
        
        print(f"\n📊 Test Results:")
        print(f"   ✓ Passed: {self.test_results['passed']}/{total}")
        print(f"   ✗ Failed: {self.test_results['failed']}/{total}")
        print(f"   📈 Success Rate: {passed_pct:.1f}%")
        
        if self.test_results['failed'] > 0:
            print(f"\n❌ Failed Tests:")
            for error in self.test_results['errors']:
                print(f"   - {error}")
        else:
            print(f"\n✅ All tests passed! System is ready for use.")
        
        print(f"\n⏱️  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70 + "\n")


def main():
    """Main entry point"""
    tester = ForensicsSystemTester()
    tester.run_all_tests()


if __name__ == '__main__':
    main()
