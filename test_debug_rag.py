import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'backend' / 'fastapi'))
import app.rag_service as rs
print('CHROMADB_AVAILABLE:', rs.CHROMADB_AVAILABLE)
print('EMBEDDINGS_AVAILABLE:', rs.EMBEDDINGS_AVAILABLE)
print('LANGCHAIN_AVAILABLE:', rs.LANGCHAIN_AVAILABLE)
print('vector_store is None:', rs.rag_service.vector_store is None)
print('vector_store type:', type(rs.rag_service.vector_store))
print('get_stats:', rs.rag_service.get_stats())
