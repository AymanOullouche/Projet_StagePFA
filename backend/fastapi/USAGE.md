# Démarrage du backend FastAPI

1. Ouvrir PowerShell dans le dossier `backend/fastapi`.
2. Exécuter :

```powershell
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

3. Si `uvicorn` n'est pas trouvé, utilisez la commande avec le module Python explicitement :

```powershell
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4. Pour lancer en une seule commande, utilisez le script PowerShell :

```powershell
.\start-fastapi.ps1
```

5. Si vous êtes déjà dans `backend/fastapi`, ne faites pas `cd backend/fastapi`.
