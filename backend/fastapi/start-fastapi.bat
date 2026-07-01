@echo off
REM Installer les dépendances et lancer le backend FastAPI
REM Usage : start-fastapi.bat
pushd %~dp0
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
popd
