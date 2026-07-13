import requests, json
BASE='http://localhost:8000/api'

r = requests.post(f'{BASE}/auth/login', json={'email':'admin@inspection.ma','password':'admin123'}, timeout=10)
token = r.json()['access_token']
headers={'Authorization':f'Bearer {token}'}

# Upload
print('UPLOAD:')
with open('d:\\ENSIASD\\TP S4\\Projet_StagePFA\\test_normes_informatique.pdf', 'rb') as f:
    files = {'file': ('normes.pdf', f, 'application/pdf')}
    r2 = requests.post(f'{BASE}/rag/documents/upload', files=files, headers=headers, timeout=15)
    print(f'  status={r2.status_code}')
    print(f'  body={r2.text}')
    
# Question directe (sans indexation pour voir le mode)
print('\nQUESTION (sans indexation):')
r3 = requests.post(f'{BASE}/rag/questions', json={'question':'Quelles sont les normes ?'}, headers=headers, timeout=60)
print(f'  status={r3.status_code}')
print(f'  body={r3.text[:500]}')
