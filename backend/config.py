"""
Configuration Settings for AI TraceFinder Backend
Centralized configuration management for production and testing environments
"""

import os
from datetime import timedelta


class Config:
    """Base configuration"""
    
    # Flask settings
    DEBUG = True
    TESTING = False
    
    # File upload settings
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'tif', 'tiff', 'bmp', 'gif', 'webp'}
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    FILE_CLEANUP_HOURS = 24  # Auto-cleanup files after 24 hours
    
    # Analysis settings
    IMAGE_RESIZE_SIZE = (256, 256)  # Standard image size for analysis
    FEATURE_EXTRACTION_TIMEOUT = 30  # Seconds
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'ai_tracefinder.log'
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5
    
    # CORS settings
    CORS_RESOURCES = {
        r"/api/*": {
            "origins": ["*"],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    }
    
    # Cache settings
    CACHE_TIMEOUT = 3600  # 1 hour
    
    # API rate limiting
    RATE_LIMIT_ENABLED = False
    RATE_LIMIT_PER_MINUTE = 100
    
    # Scanner database
    SCANNER_DATABASE = {
        'Canon_EOS': {
            'type': 'DSLR',
            'fingerprint_strength': 'Medium-High',
            'noise_characteristics': 'Sensor-specific PRNU pattern'
        },
        'Nikon_D850': {
            'type': 'DSLR',
            'fingerprint_strength': 'Medium',
            'noise_characteristics': 'Balanced sensor noise'
        },
        'Epson_Scanner': {
            'type': 'Scanner',
            'fingerprint_strength': 'Very Low',
            'noise_characteristics': 'Minimal, uniform, predictable'
        },
        'iPhone_12': {
            'type': 'SmartPhone',
            'fingerprint_strength': 'Medium',
            'noise_characteristics': 'Mobile processor artifacts'
        },
        'Samsung_Galaxy': {
            'type': 'SmartPhone',
            'fingerprint_strength': 'Medium-High',
            'noise_characteristics': 'Variable processing pipeline'
        }
    }


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB for testing


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    LOG_LEVEL = 'WARNING'


def get_config(env=None):
    """Get configuration based on environment"""
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    
    config_map = {
        'development': DevelopmentConfig,
        'testing': TestingConfig,
        'production': ProductionConfig
    }
    
    return config_map.get(env, DevelopmentConfig)


# Feature extraction configuration
FEATURE_EXTRACTION_CONFIG = {
    'PRNU': {
        'enabled': True,
        'patch_size': 32,
        'stride': 16,
        'bins': 5,
        'weight': 1.0
    },
    'FFT': {
        'enabled': True,
        'num_bands': 6,
        'weight': 1.0
    },
    'Texture': {
        'enabled': True,
        'num_bins': 8,
        'sobel_kernel': 3,
        'weight': 0.9
    },
    'Statistical': {
        'enabled': True,
        'bins': 256,
        'weight': 0.8
    },
    'Residual': {
        'enabled': True,
        'wiener_size': 5,
        'weight': 1.2  # Higher weight for scanner identification
    }
}

# Classification thresholds
CLASSIFICATION_THRESHOLDS = {
    'Epson_Scanner': {
        'residual_max': 0.08,
        'texture_max': 0.20,
        'confidence_boost': 1.0
    },
    'Canon_EOS': {
        'residual_min': 0.14,
        'residual_max': 0.28,
        'confidence_boost': 1.0
    },
    'Nikon_D850': {
        'residual_min': 0.12,
        'residual_max': 0.22,
        'confidence_boost': 1.0
    },
    'iPhone_12': {
        'residual_min': 0.08,
        'residual_max': 0.16,
        'confidence_boost': 0.95
    },
    'Samsung_Galaxy': {
        'residual_min': 0.10,
        'residual_max': 0.20,
        'confidence_boost': 0.95
    },
    'confidence_threshold': 0.35  # Minimum score to avoid 'Unknown'
}
