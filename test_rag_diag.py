import sys
import os
import traceback

os.chdir(r'd:\ENSIASD\TP S4\Projet_StagePFA\backend\fastapi')
sys.path.insert(0, r'd:\ENSIASD\TP S4\Projet_StagePFA\backend\fastapi')

from app.rag_service import CHROMADB_AVAILABLE, EMBEDDINGS_AVAILABLE, LANGCHAIN_AVAILABLE, PROJECT_ROOT, CHROMA_PERSIST_DIR
print(f"Flags: chromadb={CHROMADB_AVAILABLE}, embeddings={EMBEDDINGS_AVAILABLE}, langchain={LANGCHAIN_AVAILABLE}")
print(f"Project root: {PROJECT_ROOT}")
print(f"Chroma dir: {CHROMA_PERSIST_DIR}")
print(f"Chroma dir exists: {CHROMA_PERSIST_DIR.exists()}")

from langchain_community.embeddings import HuggingFaceEmbeddings
print("Creating embeddings...")
try:
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
    )
    print("Embeddings created")
except Exception as e:
    print("Embeddings FAILED:", e)
    traceback.print_exc()
    sys.exit(1)

from langchain_community.vectorstores import Chroma
print("Creating vector store...")
try:
    vector_store = Chroma(
        collection_name="inspection_docs",
        embedding_function=embeddings,
        persist_directory=str(CHROMA_PERSIST_DIR),
    )
    print("Vector store created")
except Exception as e:
    print("Vector store FAILED:", e)
    traceback.print_exc()
    sys.exit(1)

from langchain_ollama import ChatOllama
print("Creating ChatOllama...")
try:
    llm = ChatOllama(
        model="llama3",
        base_url="http://localhost:11434",
        temperature=0.3,
    )
    print("ChatOllama created")
except Exception as e:
    print("ChatOllama FAILED:", e)
    traceback.print_exc()
    sys.exit(1)

print("All good")
