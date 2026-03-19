"""
AI TraceFinder - System Information & Debug Tools
For troubleshooting and system verification
"""

import os
import sys
import platform


def print_system_info():
    """Print system information"""
    print("\n" + "="*60)
    print("AI TraceFinder - System Information")
    print("="*60)
    
    print(f"\nPython Version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Processor: {platform.processor()}")
    print(f"Machine: {platform.machine()}")
    print(f"Python Executable: {sys.executable}")
    print(f"Working Directory: {os.getcwd()}")
    
    print("\n" + "-"*60)
    print("Installed Packages:")
    print("-"*60)
    
    try:
        import flask
        print(f"✓ Flask: {flask.__version__}")
    except ImportError:
        print("✗ Flask: Not installed")
    
    try:
        import cv2
        print(f"✓ OpenCV: {cv2.__version__}")
    except ImportError:
        print("✗ OpenCV: Not installed")
    
    try:
        import numpy
        print(f"✓ NumPy: {numpy.__version__}")
    except ImportError:
        print("✗ NumPy: Not installed")
    
    try:
        import scipy
        print(f"✓ SciPy: {scipy.__version__}")
    except ImportError:
        print("✗ SciPy: Not installed")
    
    try:
        import skimage
        print(f"✓ scikit-image: {skimage.__version__}")
    except ImportError:
        print("✗ scikit-image: Not installed")
    
    try:
        import flask_cors
        print(f"✓ Flask-CORS: {flask_cors.__version__}")
    except ImportError:
        print("✗ Flask-CORS: Not installed")


def check_file_structure():
    """Check if all required files exist"""
    print("\n" + "-"*60)
    print("File Structure Check:")
    print("-"*60)
    
    required_files = [
        'backend/app.py',
        'backend/image_forensics.py',
        'backend/config.py',
        'frontend/templates/index.html',
        'frontend/static/styles.css',
        'frontend/static/script.js',
        'requirements.txt',
        'README.md',
    ]
    
    for filepath in required_files:
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"✓ {filepath} ({size} bytes)")
        else:
            print(f"✗ {filepath} - MISSING")


def verify_installation():
    """Verify complete installation"""
    print("\n" + "="*60)
    print("AI TraceFinder - Installation Verification")
    print("="*60)
    
    print_system_info()
    check_file_structure()
    
    print("\n" + "="*60)
    print("Status:")
    print("="*60)
    
    try:
        import flask
        import cv2
        import numpy
        from image_forensics import ImageForensics
        print("✓ All core dependencies installed")
        print("✓ Image forensics module accessible")
        print("\n✓ System is ready to run!")
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("\nRun: pip install -r requirements.txt")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--verbose':
        verify_installation()
    else:
        print("\nAI TraceFinder Verification Utility")
        print("Usage: python check_system.py --verbose")
        verify_installation()
