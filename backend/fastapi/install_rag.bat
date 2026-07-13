@echo off
REM Installation des dependances RAG
echo Installation de LangChain, ChromaDB, Ollama, PyPDF...
python -m pip install langchain langchain-community langchain-chroma ollama pypdf sentence-transformers --quiet
echo.
echo Installation terminee!
pause
