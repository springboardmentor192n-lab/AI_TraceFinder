import requests
import json

API = 'http://127.0.0.1:5000'

print("=" * 60)
print("Creating User Account")
print("=" * 60)

# Register with provided credentials
print("\n1. Registering user...")
print("   Email: tejaswiputluri@gmail.com")
print("   Password: Tejareddy@2006")

session = requests.Session()
response = session.post(f'{API}/api/register', json={
    'username': 'tejaswiputluri',
    'email': 'tejaswiputluri@gmail.com',
    'password': 'Tejareddy@2006'
})

print(f"\n   Status: {response.status_code}")
if response.status_code in [200, 201]:
    print("   ✅ Registration successful!")
    result = response.json()
    print(f"   Response: {result}")
else:
    print(f"   ⚠️  Response: {response.json()}")

# Try logging in
print("\n2. Logging in with new credentials...")
login = session.post(f'{API}/api/login', json={
    'username': 'tejaswiputluri',
    'password': 'Tejareddy@2006'
})

print(f"   Status: {login.status_code}")
if login.status_code == 200:
    print("   ✅ Login successful!")
    print(f"   Response: {login.json()}")
else:
    print(f"   Response: {login.json()}")

print("\n" + "=" * 60)
print("✅ Account created! You can now login in the UI")
print("=" * 60)
print("\nBrowser URL: http://127.0.0.1:8000/tracefinder_auth.html")
print("Username: tejaswiputluri")
print("Email: tejaswiputluri@gmail.com")
print("Password: Tejareddy@2006")
