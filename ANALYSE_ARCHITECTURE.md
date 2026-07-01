# Analyse Architecture / Code vs Cahier des Charges

## 1. Résumé de l'Architecture Globale

L'application suit une architecture **3-tiers modulaire** :
- **Frontend** : React.js + Vite + Tailwind CSS (SPA) — `src/`
- **Backend** : FastAPI (Python) avec SQLAlchemy ORM — `backend/fastapi/app/`
- **Base de données** : MySQL (script SQL) / PostgreSQL via SQLAlchemy

---

## 2. Analyse des Diagrammes extraits du Cahier des Charges

### Images extraites (dans `extracted_architecture_images/`)

| Fichier | Type de Diagramme | Contenu estimé |
|---|---|---|
| `page1_image1_Image9.png` | **Cas d'utilisation (Use Case)** | Acteurs (Inspecteur, Admin) + fonctionnalités principales |
| `page1_image2_Image11.png` | **Séquence** | Flux d'authentification et d'inspection |
| `page2_image1_Image15.jpg` | **Classes** | Structure des entités (User, Etablissement, Inspection, Rapport) |
| `page3_image1_Image19.png` | **Composants / Déploiement** | Architecture système (Frontend, Backend, DB, services IA) |
| `page4_image1_Image23.png` | **Activités** | Workflow d'inspection de A à Z |

---

## 3. Analyse Fonctionnelle : Cahier des Charges vs Code Implémenté

### EF1 : Authentification
| Exigence | Implémenté ? | Détails et écarts |
|---|---|---|
| Connexion sécurisée | ✅ Partiellement | JWT simulé via token session en base. Pas de hash de mot de passe. Authentification par email + rôle uniquement. |
| Déconnexion | ✅ | Endpoint `/auth/logout` + suppression du token côté backend et localStorage côté frontend |
| Gestion des rôles (Admin/Inspecteur) | ✅ | Rôles `ADMIN` et `INSPECTEUR` gérés côté backend (décoration `require_admin`) et frontend (filtrage navigation) |

**Correspondance avec les diagrammes** : Le diagramme de séquence (page1_image2) montre un flux login → token → sessions protégées, qui est implémenté.

### EF2 : Gestion des Établissements
| Exigence | Implémenté ? | Détails |
|---|---|---|
| Ajouter un établissement | ✅ | `POST /api/etablissements` + formulaire frontend |
| Modifier un établissement | ✅ | `PUT /api/etablissements/{id}` |
| Consulter la liste | ✅ | `GET /api/etablissements` + tableau avec recherche |
| Supprimer un établissement | ✅ | `DELETE /api/etablissements/{id}` (réservé admin) |

**Correspondance avec les diagrammes** : Les cas d'utilisation incluent la gestion des établissements. L'interface `EstablishmentsView` est complète avec CRUD.

### EF3 : Gestion des Inspections
| Exigence | Implémenté ? | Détails |
|---|---|---|
| Créer une inspection | ✅ | `POST /api/inspections` |
| Associer à un établissement | ✅ | Foreign Key `etablissement_id` dans le modèle `Inspection` |
| Ajouter des images | ✅ | `POST /api/inspections/{id}/images` avec upload fichier + modèle `InspectionImage` |

**Correspondance avec les diagrammes** : Le diagramme d'activités montre le workflow création-inspection → upload → analyse, qui est partiellement suivi.

### EF4 : Analyse par Vision Artificielle
| Exigence | Implémenté ? | Détails |
|---|---|---|
| Charger une image d'une salle | ✅ | Upload multiple avec prévisualisation |
| Détection automatique des équipements (Tables, Chaises, Ordinateurs, Imprimantes, Vidéoprojecteurs, Extincteurs) | ⚠️ **Simulé** | Aucun modèle YOLO réel. Résultats mockés dans `mockData.js` (5 équipements uniquement). |
| Afficher les résultats avec annotations visuelles | ⚠️ **Simulé** | Affichage en liste, pas d'annotations visuelles sur l'image |

**Écart** : L'EF4 exige la détection de 6 types d'équipements : Tables, Chaises, Ordinateurs, **Imprimantes**, Vidéoprojecteurs, Extincteurs. Le mock ne couvre que 5 types (sans Imprimantes).

### EF5 : Détection des Anomalies
| Exigence | Implémenté ? | Détails |
|---|---|---|
| Comparer équipements détectés vs normes | ⚠️ **Simulé** | Les normes (`expectedNorms`) sont définies dans `mockData.js` mais la comparaison n'est pas dynamique — les anomalies sont pré-définies |
| Signaler les équipements manquants | ✅ | Anomalie "Extincteur absent" affichée comme critique |
| Lister les anomalies | ✅ | Avec sévérité (CRITIQUE, ÉLEVÉE, MOYENNE) et composant `SeverityBadge` |

**Écart** : Pas de vraie logique de comparaison entre `detectedEquipments` et `expectedNorms` pour générer les anomalies automatiquement.

### EF6 : Assistant IA basé sur le RAG
| Exigence | Implémenté ? | Détails |
|---|---|---|
| Importer des documents PDF réglementaires | ⚠️ **Simulé** | Upload accepté mais stocké uniquement en base, pas d'indexation vectorielle |
| Indexer automatiquement les documents | ❌ **Non implémenté** | Pas de ChromaDB, ni LangChain, ni embeddings |
| Poser des questions en langage naturel | ⚠️ **Simulé** | Réponses basées sur des mots-clés (ex: "informatique" → réponse sur normes) |
| Obtenir des réponses contextualisées | ❌ **Non implémenté** | Pas de Retrieval-Augmented Generation réel |
| Interroger sur le traitement des anomalies | ⚠️ **Simulé** | Réponse pré-définie si "anomal" dans la question |

**Écart majeur** : L'assistant RAG est entièrement simulé côté frontend. Le backend a une fonction `answer_rag_question()` qui renvoie une réponse statique avec les 2 premiers documents comme sources.

### EF7 : Génération Automatique de Rapports
| Exigence | Implémenté ? | Détails |
|---|---|---|
| Générer un rapport structuré | ✅ | Création d'un rapport en base avec titre, établissement, anomalies |
| Intégrer les anomalies détectées | ✅ | Le champ `anomalies` est rempli |
| Intégrer les recommandations de l'IA | ⚠️ **Simulé** | Les recommandations sont mockées (3 recommandations fixes) |
| Exporter au format PDF | ❌ **Non implémenté** | Le bouton PDF est présent mais non fonctionnel (pas de génération PDF réelle) |

**Écart** : L'export PDF est un mock visuel. Aucune librairie PDF (jsPDF, react-pdf) n'est installée.

### EF8 : Tableau de Bord
| Exigence | Implémenté ? | Détails |
|---|---|---|
| Nombre total d'inspections réalisées | ✅ | `MetricCard` avec `inspections.length` |
| Nombre d'anomalies détectées | ✅ | `sum(item.anomalies)` |
| Lister les établissements inspectés | ✅ | Tableau des inspections récentes |
| Statistiques globales | ✅ | Score moyen, inspections en cours, rapports prêts |

**Correspondance avec les diagrammes** : Le tableau de bord est complet et fonctionnel.

---

## 4. Analyse Technique : Architecture vs Code

### Base de données
| Élément | Script SQL (`database/inspection_scolaire.sql`) | Modèles SQLAlchemy (`models.py`) | Correspondance |
|---|---|---|---|
| `users` | ✅ Présent | ✅ `User` (manque `password` dans les deux) | ✅ Correspondance exacte |
| `session_tokens` | ✅ Présent | ✅ `SessionToken` | ✅ |
| `etablissements` | ✅ Présent | ✅ `Etablissement` | ✅ |
| `inspections` | ✅ Présent | ✅ `Inspection` | ✅ |
| `rapports` | ✅ Présent | ✅ `Rapport` | ✅ |
| `anomalies` | ✅ Table présente dans SQL | ❌ **Absent du modèle** | ⚠️ Écart : La table `anomalies` existe dans le script SQL mais n'a PAS de modèle SQLAlchemy correspondant. Le backend ne peut donc pas créer/lire des anomalies en base. |
| `inspection_images` | ❌ Absent du script SQL | ✅ Présent dans `models.py` | ⚠️ Écart : Le modèle `InspectionImage` existe mais n'a pas de table correspondante dans le script MySQL. |
| `documents` | ❌ Absent du script SQL | ✅ Présent dans `models.py` | ⚠️ Écart : Le modèle `Document` n'a pas de table dans le script MySQL. |

### API Backend (FastAPI)
| Endpoint | Implémenté ? | Sécurisé ? |
|---|---|---|
| `GET /api/health` | ✅ | Non |
| `POST /api/auth/login` | ✅ | Non |
| `POST /api/auth/logout` | ✅ | Bearer token |
| `GET /api/auth/me` | ✅ | Bearer token |
| `GET /api/users` | ✅ | Admin requis |
| `POST /api/users` | ✅ | Admin requis |
| `GET /api/etablissements` | ✅ | Bearer token |
| `POST /api/etablissements` | ✅ | Admin requis |
| `PUT /api/etablissements/{id}` | ✅ | Admin requis |
| `DELETE /api/etablissements/{id}` | ✅ | Admin requis |
| `GET /api/inspections` | ✅ | Bearer token |
| `POST /api/inspections` | ✅ | Bearer token |
| `POST /api/inspections/{id}/images` | ✅ | Bearer token |
| `POST /api/images/{id}/analyze` | ✅ Simulation | Bearer token |
| `GET /api/rapports` | ✅ | Bearer token |
| `POST /api/rapports` | ✅ | Bearer token |
| `GET /api/rag/documents` | ✅ | Bearer token |
| `POST /api/rag/questions` | ✅ Simulation | Bearer token |

### Frontend
| Composant | Rôle | Correspondance CDC |
|---|---|---|
| `LoginScreen` | Connexion avec email + rôle | ✅ EF1 |
| `DashboardView` | Tableau de bord statistiques | ✅ EF8 |
| `EstablishmentsView` | CRUD établissements | ✅ EF2 |
| `InspectionsView` | Création inspection + upload + analyse | ✅ EF3, EF4, EF5 |
| `AssistantView` | Chat RAG + documents | ⚠️ EF6 simulé |
| `ReportsView` | Liste des rapports | ✅ EF7 |
| `AdminView` | Gestion utilisateurs | ✅ EF1 |

---

## 5. Correspondance avec les Diagrammes d'Architecture

### Diagramme de Cas d'Utilisation (page1_image1)
Les acteurs **Inspecteur** et **Administrateur** sont implémentés avec leurs droits respectifs. Les cas d'utilisation identifiés dans le CDC sont tous couverts au niveau de l'interface.

### Diagramme de Séquence (page1_image2)
Le flux login → session → inspection → analyse → rapport est respecté dans le code. La séquence d'appels API dans `InspectionsView.runAnalysis()` suit ce chemin : upload → analyse → création inspection → création rapport.

### Diagramme de Classes (page2_image1)
Les entités `User`, `Etablissement`, `Inspection`, `Rapport` sont toutes mappées en modèles SQLAlchemy et en tables SQL. **Manquant** : `Anomalie` (pas de modèle), `Document` (pas dans le SQL), `InspectionImage` (pas dans le SQL).

### Diagramme de Composants (page3_image1)
L'architecture à 3 couches est respectée : React Frontend ↔ FastAPI Backend ↔ Base de données. Les services IA (YOLO, ChromaDB, LangChain) sont prévus dans l'architecture mais pas encore intégrés (phase prototype).

### Diagramme d'Activités (page4_image1)
Le workflow complet est suivi dans l'interface `InspectionsView` : sélection établissement → upload images → analyse → affichage résultats → génération rapport.

---

## 6. Écarts et Recommandations

### Écarts critiques
1. ❌ **YOLO/IA Vision non intégré** — La détection d'équipements est entièrement simulée avec des données mockées
2. ❌ **RAG non fonctionnel** — Pas de ChromaDB, LangChain, Llama 3, ni embeddings
3. ❌ **Export PDF non fonctionnel** — Bouton PDF présent mais aucune génération réelle
4. ❌ **Table `anomalies` non mappée** — Existe dans le SQL mais pas de modèle SQLAlchemy ni d'API
5. ❌ **Tables `inspection_images` et `documents` absentes du SQL** — Présentes dans SQLAlchemy mais pas dans le script MySQL
6. ❌ **Annotations visibles sur les images** — EF4 exige des annotations visuelles sur les images détectées, non implémenté

### Écarts mineurs
7. ⚠️ **Mot de passe absent** — Pas de champ `password` dans `users` (acceptable pour prototype)
8. ⚠️ **Imprimantes manquantes** — Les imprimantes ne sont pas dans les équipements détectés mockés
9. ⚠️ **Pas de scoring automatique** — Le score global est saisi manuellement ou mocké

### Recommandations pour Phase 2
1. Intégrer YOLOv8/YOLO11 avec OpenCV pour la détection réelle d'équipements
2. Mettre en place ChromaDB + LangChain + Ollama pour un RAG fonctionnel
3. Ajouter une librairie de génération PDF (pdfkit, ReportLab)
4. Synchroniser le script SQL avec les modèles SQLAlchemy (ajouter `inspection_images`, `documents` supprimer `anomalies` ou la mapper)
5. Implémenter la logique de comparaison équipements/normes pour générer les anomalies dynamiquement
6. Ajouter les fonctionnalités "perspectives" : scoring automatique, carte géographique, comparaison avant/après

---

## 7. Technologies Utilisées vs Technologies Prévisionnelles (CDC)

| Technologie | CDC Prévue | Réellement utilisée | Statut |
|---|---|---|---|
| React.js | ✅ | ✅ React 18 | ✅ |
| Tailwind CSS | ✅ | ✅ Tailwind 3 | ✅ |
| FastAPI | ✅ | ✅ FastAPI | ✅ |
| OpenCV | ✅ | ❌ Non installé | ⚠️ À faire |
| YOLOv8/YOLO11 | ✅ | ❌ Non installé | ⚠️ À faire |
| LangChain | ✅ | ❌ Non installé | ⚠️ À faire |
| Ollama, Llama 3 | ✅ | ❌ Non installé | ⚠️ À faire |
| MySQL | ✅ | ✅ Script SQL fourni | ✅ (mais SQLAlchemy utilise PostgreSQL/SQLite) |
| phpMyAdmin | ✅ | ❌ Non configuré | ⚠️ |
| ChromaDB | ✅ | ❌ Non installé | ⚠️ À faire |
| Docker | ✅ | ❌ Non configuré | ⚠️ À faire |
| Axios | ✅ | ✅ Axios | ✅ |
| Lucide React | Non spécifié | ✅ Icônes | Bonus |

---

## 8. Structure des Fichiers Projet

```
Projet_StagePFA/
├── cahier_des_charges_Stage.pdf          # Cahier des charges
├── extracted_architecture_images/        # Diagrammes extraits
│   ├── page1_image1_Image9.png          # Use Case Diagram
│   ├── page1_image2_Image11.png         # Sequence Diagram
│   ├── page2_image1_Image15.jpg         # Class Diagram
│   ├── page3_image1_Image19.png         # Component/Deployment Diagram
│   └── page4_image1_Image23.png         # Activity Diagram
│
├── src/                                  # Frontend React
│   ├── App.jsx                          # Composant principal (1255 lignes)
│   ├── main.jsx                         # Entry point
│   ├── index.css                        # Styles Tailwind
│   ├── services/
│   │   └── api.js                       # Client Axios + endpoints
│   └── data/
│       └── mockData.js                  # Données simulées (inspections, équipements, anomalies, normes)
│
├── backend/fastapi/app/                  # Backend FastAPI
│   ├── main.py                          # Routes API (18 endpoints)
│   ├── crud.py                          # Opérations CRUD + logique métier
│   ├── models.py                        # Modèles SQLAlchemy (7 entités)
│   ├── schemas.py                       # Schémas Pydantic (validation)
│   ├── database.py                      # Connexion SQLAlchemy (PostgreSQL/SQLite)
│   └── config.py                        # Configuration
│
├── database/
│   └── inspection_scolaire.sql          # Script MySQL (6 tables + données initiales)
│
├── package.json                          # Dépendances Node.js
├── vite.config.js                        # Configuration Vite
├── tailwind.config.js                    # Configuration Tailwind
├── postcss.config.js                     # Configuration PostCSS
└── index.html                            # Page HTML principale