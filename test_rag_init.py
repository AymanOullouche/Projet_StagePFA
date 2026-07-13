import sys
import os

os.chdir(r'd:\ENSIASD\TP S4\Projet_StagePFA\backend\fastapi')
sys.path.insert(0, r'd:\ENSIASD\TP S4\Projet_StagePFA\backend\fastapi')

print("Step 1: importing constants")
try:
    from app.rag_service import CHROMADB_AVAILABLE, EMBEDDINGS_AVAILABLE, LANGCHAIN_AVAILABLE
    print(f"  CHROMADB_AVAILABLE={CHROMADB_AVAILABLE}, EMBEDDINGS_AVAILABLE={EMBEDDINGS_AVAILABLE}, LANGCHAIN_AVAILABLE={LANGCHAIN_AVAILABLE}")
except Exception as e:
    print("  ERROR importing constants:", e)
    raise

if not all([CHROMADB_AVAILABLE, EMBEDDINGS_AVAILABLE, LANGCHAIN_AVAILABLE]):
    print("Missing packages, aborting")
    sys.exit(1)

print("Step 2: importing embeddings")
try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
    print("  HuggingFaceEmbeddings imported")
except Exception as e:
    print("  ERROR:", e)
    raise

print("Step 3: creating embeddings instance")
try:
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
    )
    print("  Embeddings instance created")
except Exception as e:
    print("  ERROR:", e)
    raise

print("Step 4: importing Chroma")
try:
    from langchain_community.vectorstores import Chroma
    print("  Chroma imported")
except Exception as e:
    print("  ERROR:", e)
    raise

print("Step 5: creating vector store")
try:
    from app.config import PROJECT_ROOT
    chroma_dir = PROJECT_ROOT / "chroma_db"
    print(f"  chroma_dir={chroma_dir}")
    vector_store = Chroma(
        collection_name="inspection_docs",
        embedding_function=embeddings,
        persist_directory=str(chroma_dir),
    )
    print("  Vector store created")
except Exception as e:
    print("  ERROR:", e)
    raise

print("Step 6: importing ChatOllama")
try:
    from langchain_ollama import ChatOllama
    print("  ChatOllama imported")
except Exception as e:
    print("  ERROR:", e)
    raise

print("Step 7: creating ChatOllama instance")
try:
    llm = ChatOllama(
        model="llama3",
        base_url="http://localhost:11434",
        temperature=0.3,
    )
    print("  ChatOllama instance created")
except Exception as e:
    print("  ERROR:", e)
    raise

print("All steps OK")
