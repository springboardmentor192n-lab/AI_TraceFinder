"""Simple diagnostic to check prediction quality and available scanners"""

import requests
import json

API = 'http://127.0.0.1:5000'

print("=" * 60)
print("TraceFinder Prediction Diagnostic")
print("=" * 60)

# 1. Register and login
print("\n1. Setting up test user...")
session = requests.Session()
session.post(f'{API}/api/register', json={
    'username': 'diagtest',
    'email': 'diag@test.com',
    'password': 'diag123'
})
login = session.post(f'{API}/api/login', json={
    'username': 'diagtest',
    'password': 'diag123'
})
if login.status_code == 200:
    print("   ✅ User created and logged in")
else:
    print(f"   ❌ Login failed: {login.status_code}")

# 2. Test analyze endpoint
print("\n2. Testing analysis with sample image...")
try:
    with open('fp_keys.npy', 'rb') as f:
        files = {'file': ('test.npy', f, 'application/octet-stream')}
        response = session.post(f'{API}/api/analyze', files=files)
        
    if response.status_code == 200:
        result = response.json()
        print("   ✅ Analysis successful!")
        print(f"\n   Predictions (Top 3):")
        if 'top3' in result:
            for i, (scanner, confidence) in enumerate(result['top3'], 1):
                print(f"     {i}. {scanner}: {confidence:.2f}%")
        
        print(f"\n   Tampering detected: {result.get('tampered', False)}")
        print(f"   Tamper score: {result.get('tamper', 0):.4f}")
        
        # Check for canon220
        top_scanner = result['top3'][0][0] if result['top3'] else None
        if top_scanner and 'canon' in top_scanner.lower():
            print(f"\n   ✅ Canon scanner detected: {top_scanner}")
        elif 'canon220' in str(result['top3']):
            print(f"\n   ✅ canon220 found in predictions")
        else:
            print(f"\n   ℹ️  No Canon scanner in top predictions")
    else:
        print(f"   ❌ Analysis failed: {response.status_code}")
        print(f"      {response.json()}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("Diagnostic complete")
print("=" * 60)
