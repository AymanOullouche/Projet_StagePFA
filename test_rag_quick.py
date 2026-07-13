import sys
import os

os.chdir(r'd:\ENSIASD\TP S4\Projet_StagePFA\backend\fastapi')
sys.path.insert(0, r'd:\ENSIASD\TP S4\Projet_StagePFA\backend\fastapi')

print("Quick check: imports only")
try:
    import chromadb
    print("chromadb imported")
except Exception as e:
    print("chromadb ERROR:", e)

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    print("RecursiveCharacterTextSplitter imported")
except Exception as e:
    print("RecursiveCharacterTextSplitter ERROR:", e)

try:
    from langchain_community.vectorstores import Chroma
    print("Chroma imported")
except Exception as e:
    print("Chroma ERROR:", e)

try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
    print("HuggingFaceEmbeddings imported")
except Exception as e:
    print("HuggingFaceEmbeddings ERROR:", e)

try:
    from langchain_ollama import ChatOllama
    print("ChatOllama imported")
except Exception as e:
    print("ChatOllama ERROR:", e)

try:
    from langchain_core.prompts import PromptTemplate
    print("PromptTemplate imported")
except Exception as e:
    print("PromptTemplate ERROR:", e)

try:
    from langchain_core.runnables import RunnablePassthrough
    print("RunnablePassthrough imported")
except Exception as e:
    print("RunnablePassthrough ERROR:", e)

try:
    from langchain_core.output_parsers import StrOutputParser
    print("StrOutputParser imported")
except Exception as e:
    print("StrOutputParser ERROR:", e)

print("Quick check done")
