@echo off
echo ========================================
echo  INSTALLATION DU SYSTEME RAG COMPLET
echo ========================================
echo.

echo [1/5] Installation des dependances Python...
cd /d "%~dp0backend\fastapi"
python -m pip install chromadb langchain langchain-community langchain-chroma ollama pypdf sentence-transformers --quiet
echo.

echo [2/5] Verification Ollama...
where ollama >nul 2>&1
if %errorlevel% neq 0 (
    echo ERREUR: Ollama n'est pas installe!
    echo Telechargez-le sur: https://ollama.ai/download
    pause
    exit /b 1
)
echo Ollama detecte!
echo.

echo [3/5] Demarrage d'Ollama...
start "Ollama" /B ollama serve
timeout /t 3 >nul
echo.

echo [4/5] Telechargement de Llama 3...
ollama pull llama3
echo.

echo [5/5] Verification du systeme...
python -c "from rag_service import rag_service; print('RAG service pret!'); print('Stats:', rag_service.get_stats())"
echo.

echo ========================================
echo  INSTALLATION TERMINEE!
echo ========================================
echo.
echo Pour utiliser le RAG:
echo 1. Le serveur FastAPI doit tourner: python -m uvicorn app.main:app --reload
echo 2. Ouvrez l'application et allez dans "Assistant RAG"
echo 3. Uploadez un PDF et cliquez sur "Indexer"
echo 4. Posez vos questions!
echo.
pause
