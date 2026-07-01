# Backend FastAPI

Ce dossier contient le nouveau backend Python/FASTAPI pour le projet d'inspection scolaire.

## Installation

Depuis la racine du projet :

```powershell
python -m pip install -r backend/fastapi/requirements.txt
```

## Configuration

Les variables d'environnement suivantes sont utilisées par défaut :

- `DB_USER` (par défaut `root`)
- `DB_PASS` (par défaut `1234`)
- `DB_HOST` (par défaut `127.0.0.1`)
- `DB_PORT` (par défaut `3306`)
- `DB_NAME` (par défaut `inspection_scolaire`)

Si vous préférez utiliser SQLite pour un prototype local :

```powershell
setx USE_SQLITE 1
```

## Lancement

Lancer l'API FastAPI :

```powershell
cd backend/fastapi
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

L'API sera accessible sur `http://localhost:8000/api`.

## Endpoints disponibles

- `GET /api/health`
- `POST /api/auth/login`
- `GET /api/users`
- `GET /api/etablissements`
- `POST /api/etablissements`
- `PUT /api/etablissements/{id}`
- `DELETE /api/etablissements/{id}`
- `GET /api/inspections`
- `POST /api/inspections`
- `POST /api/inspections/{id}/images`
- `POST /api/images/{id}/analyze`
- `GET /api/rapports`
- `POST /api/rapports`
- `GET /api/rag/documents`
- `POST /api/rag/questions`
