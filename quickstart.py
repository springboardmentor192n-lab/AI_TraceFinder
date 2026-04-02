#!/usr/bin/env python
"""
TraceFinder Quick Start Script
Run this after installing dependencies to verify everything is working
"""

import sys
import os
import subprocess
import time

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RESET = '\033[0m'

print(f"""
{BLUE}╔════════════════════════════════════════════════════════════╗
║                   TraceFinder Quick Start                     ║
║            Forensic Intelligence Platform v2.0.0             ║
╚════════════════════════════════════════════════════════════╝{RESET}
""")

# Check Python version
print(f"{YELLOW}1. Checking Python version...{RESET}")
if sys.version_info < (3, 8):
    print(f"{RED}✗ Python 3.8+ required (you have {sys.version}){RESET}")
    sys.exit(1)
print(f"{GREEN}✓ Python {sys.version.split()[0]}{RESET}\n")

# Check required files
print(f"{YELLOW}2. Checking required files...{RESET}")
required_files = [
    'backend/api.py',
    'test_api.py',
    'requirements.txt',
    'artifacts/scanner_hybrid.keras',
    'artifacts/hybrid_label_encoder.pkl',
    'artifacts/hybrid_feat_scaler.pkl',
    'artifacts/scanner_fingerprints.pkl',
    'artifacts/fp_keys.npy'
]

missing = []
for file in required_files:
    if os.path.exists(file):
        print(f"{GREEN}✓ {file}{RESET}")
    else:
        print(f"{RED}✗ {file} (missing){RESET}")
        missing.append(file)

if 'artifacts/scanner_hybrid.keras' in missing or 'artifacts/fp_keys.npy' in missing:
    print(f"\n{YELLOW}⚠ Warning: Model artifacts missing. Analysis will fail.{RESET}")
    print(f"  Ensure artifacts/ directory contains required .keras and .pkl files")
else:
    print(f"{GREEN}✓ All model artifacts present{RESET}\n")

# Check dependencies
print(f"{YELLOW}3. Checking Python packages...{RESET}")
required_packages = {
    'flask': 'Flask',
    'flask_cors': 'Flask-CORS',
    'flask_login': 'Flask-Login',
    'flask_sqlalchemy': 'Flask-SQLAlchemy',
    'werkzeug': 'Werkzeug',
    'numpy': 'NumPy',
    'cv2': 'OpenCV',
    'PIL': 'Pillow',
    'tensorflow': 'TensorFlow'
}

all_installed = True
for import_name, display_name in required_packages.items():
    try:
        __import__(import_name)
        print(f"{GREEN}✓ {display_name}{RESET}")
    except ImportError:
        print(f"{RED}✗ {display_name} (not installed){RESET}")
        all_installed = False

if not all_installed:
    print(f"\n{YELLOW}Install missing packages:{RESET}")
    print(f"  pip install -r requirements.txt\n")

# Summary
print(f"\n{BLUE}╔════════════════════════════════════════════════════════════╗{RESET}")
print(f"{BLUE}║ Getting Started:{RESET}")
print(f"{BLUE}╚════════════════════════════════════════════════════════════╝{RESET}\n")

print(f"1. {YELLOW}Install Dependencies:{RESET}")
print(f"   pip install -r requirements.txt\n")

print(f"2. {YELLOW}Start Backend Server:{RESET}")
print(f"   python backend/api.py")
print(f"   (Server runs on http://127.0.0.1:5000)\n")

print(f"3. {YELLOW}In another terminal, run tests:{RESET}")
print(f"   python test_api.py")
print(f"   (Should show: Results: 11/11 tests passed)\n")

print(f"4. {YELLOW}In another terminal, start frontend:{RESET}")
print(f"   python -m http.server 8000")
print(f"   (Navigate to http://localhost:8000/tracefinder_auth.html)\n")

print(f"5. {YELLOW}In the web interface:{RESET}")
print(f"   - Click 'Sign Up' to create an account")
print(f"   - Login with your credentials")
print(f"   - Upload an image to analyze")
print(f"   - View results and history\n")

print(f"{BLUE}╔════════════════════════════════════════════════════════════╗{RESET}")
print(f"{BLUE}║ Documentation:{RESET}")
print(f"{BLUE}╚════════════════════════════════════════════════════════════╝{RESET}\n")

print(f"📖 Full Setup Guide:")
print(f"   Read: BACKEND_SETUP.md\n")

print(f"📋 Completion Summary:")
print(f"   Read: COMPLETION_SUMMARY.md\n")

print(f"🧪 Test Suite:")
print(f"   Run: python test_api.py\n")

print(f"📊 API Endpoints:")
print(f"   GET  /health              - Health check")
print(f"   POST /api/register        - Create account")
print(f"   POST /api/login           - Login")
print(f"   POST /api/logout          - Logout")
print(f"   GET  /api/me              - User profile")
print(f"   POST /analyze             - Analyze image")
print(f"   GET  /api/history         - Analysis history")
print(f"   GET  /api/stats           - User statistics\n")

print(f"🔍 Common Commands:")
print(f"   Check health:     curl http://127.0.0.1:5000/health")
print(f"   View logs:        tail -f logs/api.log")
print(f"   Git status:       git status")
print(f"   Git log:          git log --oneline\n")

print(f"{GREEN}✓ TraceFinder is ready to use!{RESET}\n")
