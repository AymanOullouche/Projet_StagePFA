@echo off
cd /d "%~dp0"
d:\ENSIASD\TP S4\Projet_StagePFA\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
