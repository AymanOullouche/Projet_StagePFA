import sys
import os

os.chdir(r'd:\ENSIASD\TP S4\Projet_StagePFA\backend\fastapi')
sys.path.insert(0, r'd:\ENSIASD\TP S4\Projet_StagePFA\backend\fastapi')

from app.rag_service import rag_service
print('vector_store type:', type(rag_service.vector_store))
print('vector_store is None:', rag_service.vector_store is None)
print('bool(vector_store):', bool(rag_service.vector_store))
try:
    print('len(vector_store):', len(rag_service.vector_store))
except Exception as e:
    print('len error:', e)
