# Plateforme intelligente d'inspection scolaire

Frontend pour la phase 1 pour le projet d'inspection et d'analyse des infrastructures scolaires.

## Objectif de cette phase

Mettre en place une interface React connectable au backend FastAPI:

- authentification mockee avec roles `ADMIN` et `INSPECTEUR`;
- tableau de bord des inspections et anomalies;
- gestion visuelle des etablissements;
- creation d'une inspection avec upload d'images et resultat d'analyse simule;
- assistant RAG avec documents reglementaires mockes;
- liste des rapports generes;
- client Axios pret pour les endpoints FastAPI.

## Lancement

```bash
npm install
npm run dev
```

Par defaut, le frontend attendra l'API sur `http://localhost:8000/api`.
Pour changer l'URL:

```bash
VITE_API_URL=http://localhost:8000/api npm run dev
```
