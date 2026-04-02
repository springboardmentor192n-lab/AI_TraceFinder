"""
Test script for TraceFinder API
Tests all endpoints: registration, login, analysis, history, stats
Includes sample image generation for analysis testing
"""

import requests
import json
import numpy as np
from PIL import Image
import io
import logging
from datetime import datetime

# ================== CONFIGURATION ==================
BASE_URL = "http://127.0.0.1:5000"
SAMPLE_IMAGE_DIR = "sample_images"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ================== SESSION MANAGEMENT ==================
session = requests.Session()

# ================== HELPER FUNCTIONS ==================
def log_response(description, response):
    """Log API response details"""
    logger.info(f"\n{'='*60}")
    logger.info(f"{description}")
    logger.info(f"Status: {response.status_code}")
    try:
        logger.info(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        logger.info(f"Response: {response.text}")
    logger.info(f"{'='*60}\n")


def generate_sample_image(filename="sample_image.png", width=256, height=256):
    """Generate a random sample image for testing"""
    try:
        import os
        os.makedirs(SAMPLE_IMAGE_DIR, exist_ok=True)
        
        # Create random but realistic-looking image
        img_array = np.random.randint(50, 200, (height, width, 3), dtype=np.uint8)
        
        # Add some patterns to make it more realistic
        for i in range(0, height, 32):
            img_array[i:i+16, :] = np.random.randint(100, 180, (16, width, 3), dtype=np.uint8)
        
        img = Image.fromarray(img_array, 'RGB')
        filepath = os.path.join(SAMPLE_IMAGE_DIR, filename)
        img.save(filepath)
        logger.info(f"Generated sample image: {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Error generating sample image: {e}")
        raise


def create_test_image_bytes():
    """Create an in-memory test image for upload"""
    img_array = np.random.randint(50, 200, (256, 256, 3), dtype=np.uint8)
    img = Image.fromarray(img_array, 'RGB')
    img_io = io.BytesIO()
    img.save(img_io, format='PNG')
    img_io.seek(0)
    return img_io


# ================== TEST FUNCTIONS ==================
def test_health_check():
    """Test /health endpoint - no auth required"""
    logger.info("Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        log_response("Health Check Response", response)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert response.json()['status'] == 'ok', "Status not 'ok'"
        logger.info("✓ Health check passed")
        return True
    except Exception as e:
        logger.error(f"✗ Health check failed: {e}")
        return False


def test_register(username="testuser", email="test@example.com", password="password123"):
    """Test user registration"""
    logger.info(f"Testing user registration with username: {username}...")
    try:
        data = {
            'username': username,
            'email': email,
            'password': password
        }
        response = session.post(f"{BASE_URL}/api/register", json=data)
        log_response("Registration Response", response)
        
        if response.status_code == 201:
            logger.info(f"✓ Registration successful for {username}")
            return True
        elif response.status_code == 400 and 'already exists' in response.text:
            logger.info(f"⚠ User {username} already exists (continuing)")
            return True
        else:
            logger.error(f"✗ Registration failed with status {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"✗ Registration error: {e}")
        return False


def test_login(username="testuser", password="password123"):
    """Test user login"""
    logger.info(f"Testing login with username: {username}...")
    try:
        data = {
            'username': username,
            'password': password
        }
        response = session.post(f"{BASE_URL}/api/login", json=data)
        log_response("Login Response", response)
        
        if response.status_code == 200:
            logger.info(f"✓ Login successful for {username}")
            return True
        else:
            logger.error(f"✗ Login failed with status {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"✗ Login error: {e}")
        return False


def test_get_me():
    """Test /api/me endpoint - requires auth"""
    logger.info("Testing get current user endpoint...")
    try:
        response = session.get(f"{BASE_URL}/api/me")
        log_response("Get Me Response", response)
        
        if response.status_code == 200:
            logger.info("✓ Get me successful")
            return response.json()
        else:
            logger.error(f"✗ Get me failed with status {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"✗ Get me error: {e}")
        return None


def test_analyze():
    """Test image analysis endpoint - requires auth"""
    logger.info("Testing image analysis endpoint...")
    try:
        img_file = ('test_image.png', create_test_image_bytes(), 'image/png')
        files = {'file': img_file}
        
        response = session.post(f"{BASE_URL}/analyze", files=files)
        log_response("Analysis Response", response)
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"✓ Analysis successful")
            logger.info(f"  - Tampered: {result.get('tampered')}")
            logger.info(f"  - Tamper Score: {result.get('tamper'):.4f}")
            logger.info(f"  - Top Scanner: {result.get('top3', [['N/A', 0]])[0][0]}")
            logger.info(f"  - Confidence: {result.get('top3', [['N/A', 0]])[0][1]:.2f}%")
            return result
        else:
            logger.error(f"✗ Analysis failed with status {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"✗ Analysis error: {e}")
        return False


def test_get_history():
    """Test history endpoint - requires auth"""
    logger.info("Testing get analysis history endpoint...")
    try:
        response = session.get(f"{BASE_URL}/api/history?limit=10")
        log_response("History Response", response)
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"✓ History retrieved: {result.get('count')} analyses")
            return result
        else:
            logger.error(f"✗ History failed with status {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"✗ History error: {e}")
        return None


def test_get_stats():
    """Test statistics endpoint - requires auth"""
    logger.info("Testing get statistics endpoint...")
    try:
        response = session.get(f"{BASE_URL}/api/stats")
        log_response("Stats Response", response)
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"✓ Stats retrieved:")
            logger.info(f"  - Total Analyses: {result.get('total_analyses')}")
            logger.info(f"  - Tampered Count: {result.get('tampered_count')}")
            logger.info(f"  - Authentic Count: {result.get('authentic_count')}")
            logger.info(f"  - Avg Tamper Score: {result.get('avg_tamper_score'):.4f}")
            return result
        else:
            logger.error(f"✗ Stats failed with status {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"✗ Stats error: {e}")
        return None


def test_logout():
    """Test logout endpoint"""
    logger.info("Testing logout endpoint...")
    try:
        response = session.post(f"{BASE_URL}/api/logout")
        log_response("Logout Response", response)
        
        if response.status_code == 200:
            logger.info("✓ Logout successful")
            return True
        else:
            logger.error(f"✗ Logout failed with status {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"✗ Logout error: {e}")
        return False


def test_unauthorized_access():
    """Test that endpoints reject unauthorized requests"""
    logger.info("Testing unauthorized access protection...")
    
    # Create new session without login
    unauth_session = requests.Session()
    
    try:
        response = unauth_session.get(f"{BASE_URL}/api/me")
        if response.status_code in [401, 302]:  # Unauthorized or redirect to login
            logger.info("✓ Unauthorized access properly blocked")
            return True
        else:
            logger.warning(f"⚠ Expected 401, got {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"✗ Auth test error: {e}")
        return False


# ================== MAIN TEST SUITE ==================
def run_all_tests():
    """Run complete test suite"""
    logger.info("\n" + "="*70)
    logger.info("TRACEFINDER API TEST SUITE")
    logger.info(f"Server: {BASE_URL}")
    logger.info(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*70 + "\n")
    
    results = {}
    
    # Test 1: Health check (no auth)
    results['health_check'] = test_health_check()
    
    # Test 2: Unauthorized access
    results['unauthorized_protection'] = test_unauthorized_access()
    
    # Test 3: Register
    results['register'] = test_register()
    
    # Test 4: Login
    results['login'] = test_login()
    
    # Test 5: Get current user
    results['get_me'] = test_get_me() is not None
    
    # Test 6: Multiple analyses
    logger.info("\n--- Running multiple analyses ---\n")
    results['analyze_1'] = test_analyze() is not None
    results['analyze_2'] = test_analyze() is not None
    results['analyze_3'] = test_analyze() is not None
    
    # Test 7: Get history
    results['history'] = test_get_history() is not None
    
    # Test 8: Get stats
    results['stats'] = test_get_stats() is not None
    
    # Test 9: Logout
    results['logout'] = test_logout()
    
    # Print summary
    logger.info("\n" + "="*70)
    logger.info("TEST SUMMARY")
    logger.info("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info("="*70)
    logger.info(f"Results: {passed}/{total} tests passed")
    logger.info("="*70 + "\n")
    
    return results


if __name__ == '__main__':
    import sys
    
    # Check if server is running
    try:
        requests.get(f"{BASE_URL}/health", timeout=2)
    except requests.exceptions.ConnectionError:
        logger.error(f"\n✗ Cannot connect to API server at {BASE_URL}")
        logger.error("Please ensure Flask server is running: python backend/api.py\n")
        sys.exit(1)
    
    # Run tests
    results = run_all_tests()
    
    # Exit with appropriate code
    passed = sum(1 for v in results.values() if v)
    sys.exit(0 if passed == len(results) else 1)
