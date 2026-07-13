import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'backend' / 'fastapi'))
from app.rag_service import rag_service

rag_dir = Path(__file__).resolve().parent / 'rag_documents'
print(f'RAG dir: {rag_dir}')
if rag_dir.exists():
    for f in rag_dir.glob('*'):
        print(f'  {f.name}')

file_path = None
for f in rag_dir.glob('6_*'):
    file_path = f
    break

print(f'\nFile to ingest: {file_path}')
if file_path:
    result = rag_service.ingest_pdf(file_path, 6, 'test_normes.pdf')
    print(f'Ingest result: {result}')
else:
    print('File not found!')
