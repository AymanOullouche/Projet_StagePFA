import json
import urllib.request

base = 'http://127.0.0.1:8000/api'

login_data = json.dumps({'email': 'inspecteur@inspection.ma', 'role': 'INSPECTEUR'}).encode()
req = urllib.request.Request(base + '/auth/login', data=login_data, headers={'Content-Type': 'application/json'})
response = urllib.request.urlopen(req).read().decode()
print('/auth/login', response)

try:
    token = json.loads(response)['token']
except Exception as e:
    raise SystemExit(f"Login failed: {e}")

headers = {'Authorization': f'Bearer {token}'}
paths = ['/health', '/auth/me', '/users', '/etablissements', '/inspections', '/rapports', '/rag/documents']
for path in paths:
    try:
        req = urllib.request.Request(base + path, headers=headers)
        data = urllib.request.urlopen(req).read().decode()
        print(path, data[:200])
    except Exception as e:
        print(path, 'ERROR', e)

logout_req = urllib.request.Request(base + '/auth/logout', method='POST', headers=headers)
try:
    data = urllib.request.urlopen(logout_req).read().decode()
    print('/auth/logout', data)
except Exception as e:
    print('/auth/logout ERROR', e)
