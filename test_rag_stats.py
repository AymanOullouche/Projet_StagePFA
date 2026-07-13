import sys
import os
import traceback

os.chdir(r'd:\ENSIASD\TP S4\Projet_StagePFA\backend\fastapi')
sys.path.insert(0, r'd:\ENSIASD\TP S4\Projet_StagePFA\backend\fastapi')

from app.rag_service import rag_service
print("vector_store is None:", rag_service.vector_store is None)
print("llm is None:", rag_service.llm is None)
print("qa_chain is None:", rag_service.qa_chain is None)

try:
    stats = rag_service.get_stats()
    print("get_stats() returned:", stats)
except Exception as e:
    print("get_stats() raised:", e)
    traceback.print_exc()

try:
    docs = rag_service.ask("test")
    print("ask() returned:", docs)
except Exception as e:
    print("ask() raised:", e)
    traceback.print_exc()
