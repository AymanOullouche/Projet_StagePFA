# Guide du Systeme RAG - Assistant IA pour Inspections Scolaires

## 📋 Vue d'ensemble

Systeme RAG (Retrieval-Augmented Generation) pour poser des questions en langage naturel sur les documents réglementaires.

**Architecture** :
- **ChromaDB** : Base de données vectorielle
- **Sentence-Transformers** : Embeddings multilingues
- **Ollama + Llama 3** : LLM local pour générer des réponses
- **LangChain** : Orchestration du pipeline

## 🚀 Installation complete

### Prérequis
- Python 3.9+
- Ollama (https://ollama.ai/download)
- 8GB RAM minimum (16GB recommandé)

### Étape 1 : Installer les dépendances Python

```powershell
cd backend/fastapi
python -m pip install chromadb langchain langchain-community langchain-chroma ollama pypdf sentence-transformers
```

### Étape 2 : Configurer Ollama

```powershell
# Démarrer Ollama
ollama serve

# Dans un autre terminal, télécharger Llama 3
ollama pull llama3
```

### Étape 3 : Lancer l'application

```powershell
# Terminal 1 - Backend
cd backend/fastapi
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd d:\ENSIASD\TP S4\Projet_StagePFA
npm run dev
```

## 📖 Utilisation

### 1. Importer des documents PDF

- Allez dans l'onglet **"Assistant RAG"**
- Cliquez sur **"Importer un PDF"**
- Sélectionnez un document réglementaire
- Cliquez sur **"Indexer"** pour l'analyser

### 2. Poser des questions

Exemples :
- "Quelles sont les normes pour une salle informatique ?"
- "Combien d'ordinateurs sont requis ?"
- "Quels sont les équipements de sécurité obligatoires ?"

### 3. Interpréter les résultats

Le système retourne :
- **Réponse** : Générée par Llama 3
- **Sources** : Documents et extraits utilisés
- **Confiance** : Score de 0 à 1
- **Mode** : RAG complet ou retrieval-only

## 🔧 Configuration

### Modèle d'embeddings
- Modèle : `sentence-transformers/all-MiniLM-L6-v2`
- Taille : 80MB
- Multilingue (français inclus)
- Device : CPU

### LLM (Ollama)
- Modèle : `llama3`
- Temperature : 0.3 (réponses contrôlées)
- Max tokens : 512

### ChromaDB
- Collection : `inspection_docs`
- Chunk size : 300 caractères
- Overlap : 50 caractères
- Persistence : `chroma_db/`

## 📊 Endpoints API

### `GET /api/rag/documents`
Liste les documents indexés + statistiques RAG.

### `POST /api/rag/questions`
Pose une question au système RAG.

**Request** :
```json
{
  "question": "Quelle est la norme pour une salle informatique ?"
}
```

**Réponse** :
```json
{
  "data": {
    "question": "...",
    "answer": "Réponse générée...",
    "sources": [...],
    "confidence": 0.85,
    "mode": "RAG (Ollama + ChromaDB)"
  }
}
```

### `POST /api/rag/documents/{id}/index`
Indexe un document PDF.

### `DELETE /api/rag/documents/{id}`
Supprime un document indexé.

## 🧪 Tests rapides

### Vérifier Ollama
```powershell
ollama list
# Doit afficher: llama3
```

### Vérifier le RAG
```powershell
python -c "from app.rag_service import rag_service; print(rag_service.get_stats())"
```

### Tester une question
```powershell
curl -X POST http://localhost:8000/api/rag/questions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer VOTRE_TOKEN" \
  -d "{\"question\": \"Normes salle informatique ?\"}"
```

## 🐛 Dépannage

### "Ollama non disponible"
```powershell
# Démarrer Ollama
ollama serve
```

### "RAG non initialisé"
```powershell
pip install chromadb langchain sentence-transformers pypdf
```

### "Aucun document pertinent"
- Vérifiez que des documents sont indexés
- Uploadez et indexez des PDF
- Vérifiez les logs du serveur

## 📈 Améliorations futures

1. Support multi-format (DOCX, TXT, MD)
2. Indexation automatique (watcher)
3. Historique des questions en base
4. Feedback utilisateur (thumbs up/down)
5. Support de plusieurs LLMs (Mistral, Falcon)
6. Cache des réponses
7. Streaming des réponses

## 📝 Notes importantes

- Ollama doit être démarré avant le backend
- Les documents sont persistés dans `chroma_db/`
- Le modèle Llama 3 est téléchargé une seule fois (~4.7GB)
- Mode retrieval-only si Ollama n'est pas disponible
