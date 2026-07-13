import requests, json

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkBpbnNwZWN0aW9uLm1hIiwicm9sZSI6IkFETUlOIiwidXNlcl9pZCI6MSwiZXhwIjoxNzg0MDE4MzE3fQ.I57jkn1GuSsuvxyEMQP2TYUV8P5gDBrwnNM1-7OmN-0"
print("Question streaming...", flush=True)
r = requests.post(
    "http://localhost:8000/api/rag/questions/stream",
    json={"question": "Quelles sont les normes pour une salle informatique ?"},
    headers={"Authorization": f"Bearer {token}", "Accept": "application/x-ndjson"},
    stream=True,
    timeout=120,
)
print(f"Status: {r.status_code}", flush=True)
for line in r.iter_lines():
    if line:
        try:
            chunk = json.loads(line)
            if chunk.get("type") == "meta":
                print(f"[META] mode={chunk.get('mode')} conf={chunk.get('confidence')}", flush=True)
            elif chunk.get("type") == "token":
                print(chunk.get("text"), end="", flush=True)
            elif chunk.get("type") == "done":
                print("\n[DONE]", flush=True)
        except Exception as e:
            print(f"parse err: {e}", flush=True)
print("Completed", flush=True)