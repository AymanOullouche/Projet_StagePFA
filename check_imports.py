import sys

try:
    import langchain_ollama
    print("langchain_ollama OK:", langchain_ollama.__version__)
except Exception as e:
    print("ERROR langchain_ollama:", e)

try:
    import sentence_transformers
    print("sentence_transformers OK:", sentence_transformers.__version__)
except Exception as e:
    print("ERROR sentence_transformers:", e)

try:
    import chromadb
    print("chromadb OK:", chromadb.__version__)
except Exception as e:
    print("ERROR chromadb:", e)

try:
    from langchain_ollama import ChatOllama
    print("ChatOllama import OK")
except Exception as e:
    print("ERROR ChatOllama:", e)

try:
    from langchain_community.vectorstores import Chroma
    print("Chroma import OK")
except Exception as e:
    print("ERROR Chroma:", e)

try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
    print("HuggingFaceEmbeddings import OK")
except Exception as e:
    print("ERROR HuggingFaceEmbeddings:", e)
