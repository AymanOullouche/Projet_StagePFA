"""Test init + login"""
import requests

BASE = "http://localhost:8000/api"

# Init DB
r = requests.post(f"{BASE}/init")
print(f"Init: {r.status_code} {r.text[:300]}")

# Login
r = requests.post(f"{BASE}/auth/login",
    json={"email": "admin@inspection.ma", "password": "admin123"})
print(f"Login: {r.status_code}")
if r.status_code == 200:
    data = r.json()["data"]
    print(f"Token: {data['access_token'][:50]}...")
    print(f"User: {data['user']}")
else:
    print(f"Error: {r.text[:500]}")
