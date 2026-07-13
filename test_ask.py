import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'backend' / 'fastapi'))
from pathlib import Path
from app.rag_service import rag_service
print('vector_store:', rag_service.vector_store is None)
print('llm:', rag_service.llm)
print('qa_chain:', rag_service.qa_chain is None)
result = rag_service.ask("Quelles sont les normes pour une salle informatique ?", top_k=4)
print('ask result:', result)
