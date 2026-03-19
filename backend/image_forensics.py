"""
Core Image Forensics Module
Provides image analysis, feature extraction, and scanner identification

Advanced forensic techniques:
- PRNU (Photo Response Non-Uniformity) analysis
- FFT (Frequency domain) analysis
- Texture analysis using gradients and LBP patterns
- Statistical feature extraction
- Wiener filter-based residual computation
- Smart classification with improved accuracy
"""

import cv2
import numpy as np
import os
from scipy.signal import wiener
from scipy import ndimage
from scipy.fft import fft2, fftshift
from scipy.ndimage import uniform_filter
from scipy.stats import skew, kurtosis
import warnings
warnings.filterwarnings('ignore')


class ImageForensics:
    """
    Advanced Image Forensics Engine for Scanner Source Identification
    Supports multiple feature extraction methods and classification
    """
    
    def __init__(self):
        """Initialize the forensics engine with optimized settings"""
        self.scanner_db = self._load_scanner_database()
        self.img_size = (256, 256)
        self.statistics = {
            'total_analyzed': 0,
            'successful_analysis': 0,
            'failed_analysis': 0
        }
    
    def _load_scanner_database(self):
        """
        Load or create scanner database with characteristic fingerprints
        Each scanner has unique noise patterns and feature signatures
        """
        return {
            'Canon_EOS': {
                'fingerprint_id': 'canon_1',
                'type': 'DSLR',
                'residual_range': (0.15, 0.25),
                'texture_range': (0.25, 0.4),
                'characteristics': 'High color depth, Strong PRNU pattern, Medium noise'
            },
            'Nikon_D850': {
                'fingerprint_id': 'nikon_1',
                'type': 'DSLR',
                'residual_range': (0.12, 0.20),
                'texture_range': (0.20, 0.35),
                'characteristics': 'Medium residual, Balanced texture, Clean signal'
            },
            'Epson_Scanner': {
                'fingerprint_id': 'epson_1',
                'type': 'Scanner',
                'residual_range': (0.02, 0.08),  # VERY LOW - Scanner specific
                'texture_range': (0.05, 0.15),   # LOW - Scanned images are clean
                'characteristics': 'Very low noise, Uniform patterns, Minimal residual, Regular texture'
            },
            'iPhone_12': {
                'fingerprint_id': 'iphone_1',
                'type': 'SmartPhone',
                'residual_range': (0.08, 0.15),
                'texture_range': (0.18, 0.35),
                'characteristics': 'Medium noise, Mobile processing artifacts, Computational PRNU'
            },
            'Samsung_Galaxy': {
                'fingerprint_id': 'samsung_1',
                'type': 'SmartPhone',
                'residual_range': (0.10, 0.18),
                'texture_range': (0.22, 0.40),
                'characteristics': 'Variable noise, Strong texture, Processing artifacts'
            },
            'Unknown': {
                'fingerprint_id': 'unknown',
                'type': 'Unknown',
                'residual_range': (0.0, 1.0),
                'texture_range': (0.0, 1.0),
                'characteristics': 'Unidentified source'
            }
        }
    
    def analyze_image(self, filepath):
        """
        Main analysis function - Performs complete forensic analysis on image
        
        Pipeline:
        1. Load and validate image
        2. Preprocess (resize, normalize)
        3. Extract comprehensive features
        4. Compute residual (noise pattern)
        5. Classify scanner source
        6. Generate metrics and recommendations
        """
        try:
            # Load and validate image
            image = cv2.imread(filepath)
            if image is None:
                return {
                    'success': False,
                    'error': 'Failed to load image file'
                }
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            
            # Preprocess image
            preprocessed = self._preprocess_image(gray)
            
            # Extract all features - used for classification
            features = self._extract_all_features(preprocessed, gray)
            
            # Compute noise pattern (residual) - key for PRNU analysis
            residual = self._compute_residual(gray)
            
            # Perform scanner identification
            scanner_id, confidence = self._identify_scanner(features, residual)
            
            # Get additional forensic metrics
            fft_analysis = self._analyze_fft(preprocessed)
            texture_metrics = self._compute_texture_metrics(preprocessed)
            forensic_indicators = self._get_forensic_indicators(preprocessed, residual)
            recommendations = self._generate_recommendations(confidence, forensic_indicators, scanner_id)
            
            # Update statistics
            self.statistics['total_analyzed'] += 1
            self.statistics['successful_analysis'] += 1
            
            return {
                'success': True,
                'scanner_id': scanner_id,
                'confidence': confidence,
                'feature_vector': features['feature_vector'],
                'noise_pattern_strength': float(np.std(residual)),
                'fft_analysis': fft_analysis,
                'texture_metrics': texture_metrics,
                'forensic_indicators': forensic_indicators,
                'recommendations': recommendations,
                'image_info': {
                    'shape': gray.shape,
                    'dtype': str(gray.dtype),
                    'min_val': float(gray.min()),
                    'max_val': float(gray.max()),
                    'mean_val': float(gray.mean()),
                    'std_val': float(gray.std())
                }
            }
        
        except Exception as e:
            self.statistics['failed_analysis'] += 1
            return {
                'success': False,
                'error': f'Analysis failed: {str(e)}'
            }
    
    def _preprocess_image(self, image):
        """
        Preprocess image for analysis
        - Resize to standard size for consistent feature extraction
        - Normalize pixel values to [0, 1] range
        """
        # Resize to standard size
        resized = cv2.resize(image, self.img_size, interpolation=cv2.INTER_AREA)
        
        # Normalize to [0, 1]
        normalized = resized.astype(np.float32) / 255.0
        
        return normalized
    
    def _compute_residual(self, image):
        """
        Compute residual using Wiener filter denoising
        
        Residual = Original Image - Denoised Image
        
        The residual captures device-specific noise patterns (PRNU),
        which is unique to each camera/scanner sensor.
        Scanners have VERY low residuals (clean, uniform patterns)
        while cameras have higher residuals (sensor noise)
        """
        # Normalize
        norm_img = image.astype(np.float32) / 255.0
        norm_img = cv2.resize(norm_img, self.img_size, interpolation=cv2.INTER_AREA)
        
        # Apply Wiener filter denoising - removes noise while preserving edges
        denoised = wiener(norm_img, mysize=(5, 5))
        
        # Compute residual
        residual = norm_img - denoised
        
        return residual.astype(np.float32)
    
    def _extract_all_features(self, image, original_image):
        """
        Extract comprehensive feature set combining multiple methods
        
        Features extracted:
        1. PRNU (Camera noise pattern)
        2. FFT (Frequency domain analysis)
        3. Texture (Gradient and LBP-like patterns)
        4. Statistical (Moments, entropy, percentiles)
        5. Residual (Noise characteristics)
        """
        features_dict = {}
        
        # PRNU-like features (fingerprint correlation)
        prnu_features = self._extract_prnu_features(image)
        features_dict['prnu'] = prnu_features
        
        # FFT features (frequency analysis)
        fft_features = self._extract_fft_features(image)
        features_dict['fft'] = fft_features
        
        # Texture features (gradients and patterns)
        texture_features = self._extract_texture_features(image)
        features_dict['texture'] = texture_features
        
        # Statistical features
        stat_features = self._extract_statistical_features(image)
        features_dict['statistical'] = stat_features
        
        # Residual-based features
        residual_features = self._extract_residual_features(original_image)
        features_dict['residual'] = residual_features
        
        # Combine all features into single vector
        combined_vector = np.concatenate([
            prnu_features,
            fft_features,
            texture_features,
            stat_features,
            residual_features
        ]).astype(np.float32)
        
        features_dict['feature_vector'] = combined_vector
        
        return features_dict
    
    def _extract_prnu_features(self, image, num_bins=5):
        """
        Extract PRNU (Photo Response Non-Uniformity) inspired features
        
        PRNU is the unique noise pattern created by variations in
        the CCD/CMOS sensor. Scanners have minimal PRNU (no sensor noise).
        """
        features = []
        patch_size = 32
        stride = 16  # Optimized stride for efficiency
        
        # Extract variance from patches
        for i in range(0, image.shape[0] - patch_size, stride):
            for j in range(0, image.shape[1] - patch_size, stride):
                patch = image[i:i+patch_size, j:j+patch_size]
                features.append(np.var(patch))
        
        # Create histogram of variances
        if features:
            features = np.array(features)
            hist, _ = np.histogram(features, bins=num_bins, range=(0, np.max(features)+0.01))
            return (hist.astype(np.float32) / len(features))
        else:
            return np.zeros(num_bins, dtype=np.float32)
    
    def _extract_fft_features(self, image, num_bands=6):
        """
        Extract FFT (Frequency Domain) features
        
        Analyzes frequency components to identify:
        - Compression artifacts (JPEG blocking patterns)
        - Processing pipelines (scanner vs camera)
        - Sensor characteristics
        """
        # Compute 2D FFT
        fft_img = np.abs(fft2(image))
        fft_img = fftshift(fft_img)
        
        # Extract radial frequency bands
        h, w = fft_img.shape
        cy, cx = h // 2, w // 2
        
        yy, xx = np.ogrid[:h, :w]
        radii = np.sqrt((yy - cy)**2 + (xx - cx)**2)
        rmax = radii.max() + 1e-6
        
        bands = np.linspace(0, rmax, num_bands + 1)
        features = []
        
        for k in range(num_bands):
            mask = (radii >= bands[k]) & (radii < bands[k + 1])
            energy = fft_img[mask].mean() if mask.any() else 0.0
            features.append(energy)
        
        return np.array(features, dtype=np.float32)
    
    def _extract_texture_features(self, image, num_bins=8):
        """
        Extract texture features using gradient analysis
        
        Includes:
        - Gradient magnitude histogram
        - Gradient direction histogram
        - Local binary pattern-like features
        """
        # Compute gradients using Sobel operator
        grad_x = ndimage.sobel(image, axis=1)
        grad_y = ndimage.sobel(image, axis=0)
        grad_mag = np.sqrt(grad_x**2 + grad_y**2)
        grad_dir = np.arctan2(grad_y, grad_x)
        
        # Gradient magnitude histogram
        mag_hist, _ = np.histogram(grad_mag.flatten(), bins=num_bins, 
                                   range=(0, grad_mag.max()+0.01))
        mag_hist = mag_hist.astype(np.float32) / (mag_hist.sum() + 1e-8)
        
        # Gradient direction histogram
        dir_hist, _ = np.histogram(grad_dir.flatten(), bins=num_bins, 
                                   range=(-np.pi, np.pi))
        dir_hist = dir_hist.astype(np.float32) / (dir_hist.sum() + 1e-8)
        
        return np.concatenate([mag_hist, dir_hist]).astype(np.float32)
    
    def _extract_statistical_features(self, image):
        """
        Extract statistical features from image
        
        Captures distribution characteristics:
        - Central tendency (mean, median, mode)
        - Spread (std dev, IQR)
        - Shape (skewness, kurtosis)
        - Entropy (information content)
        """
        features = [
            np.mean(image),              # Mean
            np.std(image),               # Standard deviation
            np.median(image),            # Median
            np.percentile(image, 25),    # Q1
            np.percentile(image, 75),    # Q3
            np.min(image),               # Min
            np.max(image),               # Max
            np.ptp(image),               # Peak to peak (range)
            skew(image.flatten()),       # Skewness
            kurtosis(image.flatten()),   # Kurtosis
        ]
        
        # Entropy-like feature (information content)
        hist, _ = np.histogram(image, bins=256, range=(0, 1))
        hist = hist.astype(np.float32) / (hist.sum() + 1e-8)
        entropy = -np.sum(hist[hist > 0] * np.log2(hist[hist > 0] + 1e-10))
        features.append(entropy)
        
        return np.array(features, dtype=np.float32)
    
    def _extract_residual_features(self, image):
        """
        Extract features from residual (noise pattern)
        
        Critical for distinguishing:
        - Scanner (minimal residual) vs Camera (high residual)
        """
        residual = self._compute_residual(image)
        
        features = [
            np.std(residual),            # Residual noise strength
            np.mean(np.abs(residual)),   # Mean absolute residual
            np.max(np.abs(residual)),    # Peak residual
            np.percentile(np.abs(residual), 75),  # Q3 of residual
        ]
        
        return np.array(features, dtype=np.float32)
    
    def _identify_scanner(self, features, residual):
        """
        Identify scanner using BALANCED multi-feature scoring system.
        
        Key improvements:
        1. Normalized scoring (100 points max per scanner)
        2. Feature-based confidence scoring
        3. Penalty system to reduce bias
        4. Statistical distance metrics
        
        Scanner Profiles:
        - Epson Scanner: Very low residual (<0.05), uniform low texture, minimal PRNU
        - Canon EOS: Med-high residual (0.15-0.28), strong texture (0.25-0.45), high PRNU
        - Nikon D850: Med residual (0.12-0.22), balanced texture (0.20-0.38), med PRNU
        - iPhone 12: Low-med residual (0.08-0.16), variable texture, mobile artifacts
        - Samsung Galaxy: Med residual (0.10-0.20), high texture (0.22-0.45), variable PRNU
        """
        # ============ FEATURE EXTRACTION ============
        residual_strength = float(np.std(residual))
        feature_energy = float(np.sum(features['fft']))
        texture_complexity = float(np.std(features['texture']))
        stat_entropy = float(features['statistical'][-1])  # Entropy
        prnu_strength = float(np.sum(features['prnu']))
        residual_mean = float(np.mean(np.abs(residual)))
        
        scanner_scores = {}
        
        # ============ UTILITY: Distance-based scoring ============
        def distance_score(value, ideal_range, weight=20):
            """
            Calculate score based on distance from ideal range.
            Closer to ideal = higher score (0-20 points typically)
            """
            low, high = ideal_range
            if low <= value <= high:
                # Perfect match: full points
                return weight
            elif value < low:
                # Below range: penalize based on distance
                distance = (low - value) / (low + 1e-8)
                return max(0, weight * (1 - min(distance, 1.0)))
            else:
                # Above range: penalize based on distance
                distance = (value - high) / (high + 1e-8)
                return max(0, weight * (1 - min(distance, 1.0)))
        
        # ==================== EPSON SCANNER ====================
        epson_score = 0.0
        
        # Residual strength (CRITICAL - must be very low)
        # Epson: < 0.05 (ideal), 0.05-0.08 (acceptable)
        residual_score = 0
        if residual_strength < 0.05:
            residual_score = 25  # Perfect match
        elif residual_strength < 0.08:
            residual_score = 18  # Good match
        elif residual_strength < 0.12:
            residual_score = 8   # Acceptable but weak
        else:
            residual_score = 0   # No match - Scanner must have low noise
        
        epson_score += residual_score
        
        # Texture complexity (should be VERY LOW)
        texture_score = 0
        if texture_complexity < 0.15:
            texture_score = 20  # Excellent uniformity
        elif texture_complexity < 0.22:
            texture_score = 15  # Good uniformity
        elif texture_complexity < 0.35:
            texture_score = 5   # Some degradation
        else:
            texture_score = 0   # Too much texture
        
        epson_score += texture_score
        
        # PRNU strength (should be MINIMAL for scanners)
        prnu_score = 0
        if prnu_strength < 0.3:
            prnu_score = 20    # No camera sensor
        elif prnu_strength < 0.6:
            prnu_score = 10    # Weak signal OK
        else:
            prnu_score = 0     # Too strong - unlikely scanner
        
        epson_score += prnu_score
        
        # Residual mean (should be very low)
        residual_mean_score = distance_score(residual_mean, (0.001, 0.015), weight=15)
        epson_score += residual_mean_score
        
        # Entropy (lower for scanned docs)
        entropy_score = 0
        if stat_entropy < 5.5:
            entropy_score = 20  # Low information = scanned
        elif stat_entropy < 6.5:
            entropy_score = 10  # Acceptable
        else:
            entropy_score = 0   # Too high
        
        epson_score += entropy_score
        
        # Feature energy constraint
        energy_score = 0
        if feature_energy < 0.30:
            energy_score = 10   # Low energy
        elif feature_energy < 0.40:
            energy_score = 5    # Acceptable
        else:
            energy_score = 0    # High energy
        
        epson_score += energy_score
        
        scanner_scores['Epson_Scanner'] = max(0, min(100, epson_score))
        
        # ==================== CANON EOS ====================
        canon_score = 0.0
        
        # Residual strength (medium-high)
        canon_residual = distance_score(residual_strength, (0.15, 0.28), weight=20)
        canon_score += canon_residual
        
        # Texture complexity (high, varies)
        canon_texture = distance_score(texture_complexity, (0.25, 0.45), weight=20)
        canon_score += canon_texture
        
        # PRNU (must be strong - camera sensor)
        canon_prnu = 0
        if prnu_strength > 1.2:
            canon_prnu = 20     # Strong sensor fingerprint
        elif prnu_strength > 0.9:
            canon_prnu = 15     # Decent camera signal
        elif prnu_strength > 0.6:
            canon_prnu = 8      # Weak camera signal
        else:
            canon_prnu = 0      # No camera signature
        
        canon_score += canon_prnu
        
        # Entropy (higher for natural scenes)
        canon_entropy = distance_score(stat_entropy, (6.4, 7.8), weight=15)
        canon_score += canon_entropy
        
        # Feature energy
        canon_energy = distance_score(feature_energy, (0.4, 0.80), weight=15)
        canon_score += canon_energy
        
        # Residual mean (should be medium)
        canon_residual_mean = distance_score(residual_mean, (0.02, 0.06), weight=10)
        canon_score += canon_residual_mean
        
        scanner_scores['Canon_EOS'] = max(0, min(100, canon_score))
        
        # ==================== NIKON D850 ====================
        nikon_score = 0.0
        
        # Residual (medium)
        nikon_residual = distance_score(residual_strength, (0.12, 0.22), weight=20)
        nikon_score += nikon_residual
        
        # Texture (balanced)
        nikon_texture = distance_score(texture_complexity, (0.20, 0.38), weight=20)
        nikon_score += nikon_texture
        
        # PRNU (medium-strong)
        nikon_prnu = 0
        if prnu_strength > 1.0:
            nikon_prnu = 20
        elif prnu_strength > 0.7:
            nikon_prnu = 12
        elif prnu_strength > 0.4:
            nikon_prnu = 5
        else:
            nikon_prnu = 0
        
        nikon_score += nikon_prnu
        
        # Entropy
        nikon_entropy = distance_score(stat_entropy, (6.1, 7.4), weight=15)
        nikon_score += nikon_entropy
        
        # Feature energy
        nikon_energy = distance_score(feature_energy, (0.35, 0.68), weight=15)
        nikon_score += nikon_energy
        
        # Residual mean
        nikon_residual_mean = distance_score(residual_mean, (0.015, 0.05), weight=10)
        nikon_score += nikon_residual_mean
        
        scanner_scores['Nikon_D850'] = max(0, min(100, nikon_score))
        
        # ==================== IPHONE 12 ====================
        iphone_score = 0.0
        
        # Residual (low-medium)
        iphone_residual = distance_score(residual_strength, (0.08, 0.16), weight=20)
        iphone_score += iphone_residual
        
        # Texture (medium, processing artifacts)
        iphone_texture = distance_score(texture_complexity, (0.15, 0.35), weight=18)
        iphone_score += iphone_texture
        
        # PRNU (mobile-specific)
        iphone_prnu = 0
        if 0.7 <= prnu_strength <= 1.8:
            iphone_prnu = 20    # Mobile phone range
        elif 0.5 <= prnu_strength < 0.7:
            iphone_prnu = 12
        elif 1.8 < prnu_strength <= 2.2:
            iphone_prnu = 10
        else:
            iphone_prnu = 0
        
        iphone_score += iphone_prnu
        
        # Entropy (mobile processing shows high entropy)
        iphone_entropy = distance_score(stat_entropy, (6.6, 7.7), weight=15)
        iphone_score += iphone_entropy
        
        # Feature energy
        iphone_energy = distance_score(feature_energy, (0.25, 0.58), weight=15)
        iphone_score += iphone_energy
        
        # Residual mean
        iphone_residual_mean = distance_score(residual_mean, (0.008, 0.035), weight=12)
        iphone_score += iphone_residual_mean
        
        scanner_scores['iPhone_12'] = max(0, min(100, iphone_score))
        
        # ==================== SAMSUNG GALAXY ====================
        samsung_score = 0.0
        
        # Residual (medium)
        samsung_residual = distance_score(residual_strength, (0.10, 0.20), weight=20)
        samsung_score += samsung_residual
        
        # Texture (high, distinctive)
        samsung_texture = distance_score(texture_complexity, (0.22, 0.45), weight=20)
        samsung_score += samsung_texture
        
        # PRNU (variable mobile range)
        samsung_prnu = 0
        if 0.85 <= prnu_strength <= 2.2:
            samsung_prnu = 20   # Strong mobile PRNU
        elif 0.5 <= prnu_strength < 0.85:
            samsung_prnu = 12
        elif prnu_strength > 2.2:
            samsung_prnu = 8
        else:
            samsung_prnu = 0
        
        samsung_score += samsung_prnu
        
        # Entropy (high for smartphone images)
        samsung_entropy = distance_score(stat_entropy, (6.7, 7.9), weight=15)
        samsung_score += samsung_entropy
        
        # Feature energy
        samsung_energy = distance_score(feature_energy, (0.38, 0.75), weight=15)
        samsung_score += samsung_energy
        
        # Residual mean
        samsung_residual_mean = distance_score(residual_mean, (0.012, 0.04), weight=10)
        samsung_score += samsung_residual_mean
        
        scanner_scores['Samsung_Galaxy'] = max(0, min(100, samsung_score))
        
        # ============ DECISION LOGIC ============
        # Find best match
        best_scanner = max(scanner_scores, key=scanner_scores.get)
        best_score = scanner_scores[best_scanner]
        
        # Get second best for comparison
        sorted_scores = sorted(scanner_scores.items(), key=lambda x: x[1], reverse=True)
        second_score = sorted_scores[1][1] if len(sorted_scores) > 1 else 0
        
        # Calculate confidence with better normalization
        # Only claim high confidence if clearly better than second choice
        score_margin = best_score - second_score
        
        if best_score < 30:
            # No clear match
            confidence = 0.50
            best_scanner = 'Unknown'
        elif score_margin < 10:
            # Too close to call
            confidence = min(0.65, best_score / 100.0)
        elif score_margin < 20:
            # Reasonable match
            confidence = min(0.80, best_score / 100.0)
        else:
            # Clear winner
            confidence = min(0.95, best_score / 100.0)
        
        return best_scanner, float(confidence)
    
    def _analyze_fft(self, image):
        """Analyze FFT patterns for forensic indicators"""
        fft_img = np.abs(fft2(image))
        fft_img = fftshift(fft_img)
        
        # Compute energy concentration
        total_energy = np.sum(fft_img)
        top_10_percent = np.sum(fft_img[fft_img > np.percentile(fft_img, 90)])
        energy_concentration = top_10_percent / (total_energy + 1e-8)
        
        return {
            'mean_magnitude': float(np.mean(fft_img)),
            'max_magnitude': float(np.max(fft_img)),
            'peak_frequency_ratio': float(np.max(fft_img) / (np.mean(fft_img) + 1e-8)),
            'energy_concentration': float(energy_concentration)
        }
    
    def _compute_texture_metrics(self, image):
        """
        Compute texture-related metrics using efficient algorithms
        Optimized for faster computation (avoiding nested loops)
        """
        # Compute local variance using efficient method
        mean_filter = uniform_filter(image, size=8, mode='constant')
        sqr_filter = uniform_filter(image**2, size=8, mode='constant')
        local_var = np.maximum(sqr_filter - mean_filter**2, 0.0)
        
        return {
            'mean_texture': float(np.mean(local_var)),
            'texture_std': float(np.std(local_var)),
            'texture_entropy': float(self._compute_entropy(local_var)),
            'edge_strength': float(np.mean(np.abs(ndimage.sobel(image))))
        }
    
    def _compute_entropy(self, image):
        """Compute entropy of image patches"""
        hist, _ = np.histogram(image, bins=16)
        hist = hist.astype(np.float32) / (hist.sum() + 1e-8)
        entropy = -np.sum(hist[hist > 0] * np.log2(hist[hist > 0] + 1e-10))
        return entropy
    
    def _get_forensic_indicators(self, image, residual):
        """Get forensic indicators for security assessment"""
        return {
            'noise_level': float(np.std(residual)),
            'compression_artifacts': bool(self._detect_compression_artifacts(image)),
            'color_channel_mismatch': bool(False),  # Would check in color images
            'unusual_patterns': bool(self._detect_unusual_patterns(image)),
            'potential_tampering': bool(float(np.std(residual)) > 0.3)  # High unusual noise
        }
    
    def _detect_compression_artifacts(self, image):
        """Detect JPEG-like compression artifacts"""
        # Look for blocking patterns (8x8 blocks typical in JPEG)
        block_size = 8
        block_variance = []
        
        for i in range(0, image.shape[0] - block_size, block_size):
            for j in range(0, image.shape[1] - block_size, block_size):
                block = image[i:i+block_size, j:j+block_size]
                block_variance.append(np.std(block))
        
        if block_variance:
            return bool(np.std(block_variance) > 0.1)
        return bool(False)
    
    def _detect_unusual_patterns(self, image):
        """Detect unusual patterns that might indicate manipulation"""
        fft_img = np.abs(fft2(image))
        fft_img = fftshift(fft_img)
        
        # Look for multiple strong frequency peaks
        threshold = np.percentile(fft_img, 95)
        peak_count = np.sum(fft_img > threshold)
        
        return bool(peak_count > 50)  # More than 50 peaks might indicate manipulation
    
    def _generate_recommendations(self, confidence, indicators, scanner_id):
        """Generate recommendations based on analysis results"""
        recommendations = []
        
        if confidence < 0.65:
            recommendations.append("⚠ Low confidence - Consider manual review")
        
        if indicators.get('compression_artifacts'):
            recommendations.append("📊 JPEG compression artifacts detected")
        
        if indicators.get('unusual_patterns'):
            recommendations.append("⚠ Unusual frequency patterns detected")
        
        if indicators.get('potential_tampering'):
            recommendations.append("⚠ High noise level - Possible manipulation")
        
        if scanner_id == 'Epson_Scanner':
            recommendations.append("✓ Scanner-originated document identified")
        elif scanner_id in ['Canon_EOS', 'Nikon_D850', 'iPhone_12', 'Samsung_Galaxy']:
            recommendations.append(f"✓ {scanner_id} identified as likely source")
        
        if not recommendations:
            recommendations.append("✓ Analysis complete - No anomalies detected")
        
        return recommendations
    
    def get_statistics(self):
        """Get system statistics"""
        return {
            'total_analyzed': self.statistics['total_analyzed'],
            'successful_analysis': self.statistics['successful_analysis'],
            'failed_analysis': self.statistics['failed_analysis'],
            'scanner_database_size': len(self.scanner_db),
            'available_scanners': list(self.scanner_db.keys()),
            'supported_formats': ['JPG', 'PNG', 'TIFF', 'BMP']
        }
