import requests, json
BASE='http://localhost:8000/api'

# Login
r = requests.post(f'{BASE}/auth/login', json={'email':'admin@inspection.ma','password':'admin123'}, timeout=10)
token = r.json()['access_token']
headers={'Authorization':f'Bearer {token}'}
print('Login OK')

# Upload PDF
print('\n1. UPLOAD PDF')
with open('d:\\ENSIASD\\TP S4\\Projet_StagePFA\\test_normes_informatique.pdf', 'rb') as f:
    files = {'file': ('test_normes.pdf', f, 'application/pdf')}
    r2 = requests.post(f'{BASE}/rag/documents/upload', files=files, headers=headers, timeout=15)
    print(f'   Status: {r2.status_code}')
    if r2.status_code != 200:
        print('   ERROR:', r2.text)
        exit()
    upload_data = r2.json()['data']
    print(f'   Document: {upload_data["titre"]} (ID: {upload_data["id"]})')
    doc_id = upload_data['id']

# Indexation
print(f'\n2. INDEXATION Document {doc_id}')
r3 = requests.post(f'{BASE}/rag/documents/{doc_id}/index', headers=headers, timeout=60)
print(f'   Status: {r3.status_code}')
index_data = r3.json()
print(f'   Resultat: {index_data.get("data", {}).get("status")}')

# Question
print('\n3. QUESTION RAG')
question = 'Quelles sont les normes pour une salle informatique ?'
print(f'   Q: {question}')
r4 = requests.post(f'{BASE}/rag/questions', json={'question': question}, headers=headers, timeout=60)
print(f'   Status: {r4.status_code}')
answer = r4.json()['data']
print(f'   Mode: {answer.get("mode")}')
print(f'   Confiance: {answer.get("confidence")}')
print(f'   Reponse: {answer.get("answer", "")[:300]}...')
print(f'   Sources: {len(answer.get("sources", []))} document(s)')
