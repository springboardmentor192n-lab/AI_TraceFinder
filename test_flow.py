import requests
import json

# Create session to maintain cookies
session = requests.Session()
API = 'http://127.0.0.1:5000'

print("=" * 50)
print("TraceFinder API Test")
print("=" * 50)

# 1. Check health
print("\n1. Checking API health...")
try:
    health = session.get(f'{API}/api/health')
    print(f"   Status: {health.status_code}")
    print(f"   Response: {health.json()}")
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    print("   → Is backend running? (python backend/api.py)")
    exit(1)

# 2. Test analysis WITHOUT auth
print("\n2. Testing analysis (no auth required)...")
try:
    with open('fp_keys.npy', 'rb') as f:
        files = {'file': ('test.npy', f, 'application/octet-stream')}
        analyze = session.post(f'{API}/api/test/analyze', files=files)
        print(f"   Status: {analyze.status_code}")
        if analyze.status_code == 200:
            result = analyze.json()
            print(f"   ✅ SUCCESS! Analysis worked")
            print(f"   Result keys: {list(result.keys())}")
            if 'top3' in result:
                print(f"   Top scanner: {result['top3'][0] if result['top3'] else 'unknown'}")
        else:
            print(f"   ❌ FAILED: {analyze.json()}")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

# 3. Register new user
print("\n3. Registering user...")
try:
    reg = session.post(f'{API}/api/register', json={
        'username': 'quicktest',
        'email': 'quick@test.com',
        'password': 'quick123'
    })
    print(f"   Status: {reg.status_code}")
    if reg.status_code in [200, 201]:
        print(f"   ✅ Registration successful")
    else:
        print(f"   Response: {reg.json()}")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

# 4. Login
print("\n4. Logging in...")
try:
    login = session.post(f'{API}/api/login', json={
        'username': 'quicktest',
        'password': 'quick123'
    })
    print(f"   Status: {login.status_code}")
    if login.status_code == 200:
        print(f"   ✅ Login successful")
    else:
        print(f"   Response: {login.json()}")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

# 5. Analyze WITH auth
print("\n5. Testing analysis (WITH authentication)...")
try:
    with open('fp_keys.npy', 'rb') as f:
        files = {'file': ('test_auth.npy', f, 'application/octet-stream')}
        analyze = session.post(f'{API}/api/analyze', files=files)
        print(f"   Status: {analyze.status_code}")
        if analyze.status_code == 200:
            result = analyze.json()
            print(f"   ✅ Authenticated analysis worked!")
            print(f"   Analysis saved with ID: {result.get('analysis_id', 'unknown')}")
        else:
            print(f"   Response: {analyze.json()}")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

print("\n" + "=" * 50)
print("Test complete!")
print("=" * 50)

