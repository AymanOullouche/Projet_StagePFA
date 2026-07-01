# Fine-Tuning YOLO pour l'Inspection Scolaire

## Objectif

Entraîner un modèle YOLO personnalisé pour détecter **6 types d'équipements** dans les salles de classe marocaines :

| ID | Classe | Exemple |
|----|--------|---------|
| 0 | Table | Bureaux, tables d'élèves |
| 1 | Chaise | Chaises d'élèves, fauteuils |
| 2 | Ordinateur | PC fixes, laptops |
| 3 | Imprimante | Imprimantes, photocopieurs |
| 4 | Vidéoprojecteur | Projecteurs, écrans interactifs |
| 5 | Extincteur | Extincteurs muraux |

---

## 🗂️ Structure du Dataset

```
yolo_training/
├── dataset/
│   ├── train/
│   │   ├── images/          # Photos des salles (JPG/PNG)
│   │   └── labels/          # Annotations (fichiers .txt)
│   ├── val/
│   │   ├── images/          # Photos de validation
│   │   └── labels/          # Annotations de validation
│   ├── test/
│   │   ├── images/          # Photos de test (optionnel)
│   │   └── labels/          # Annotations de test
│   └── data.yaml            # Configuration du dataset
├── train_yolo.py            # Script d'entraînement
└── README_FINETUNING.md     # Ce fichier
```

---

## 📸 Collecte d'images

### Sources recommandées :
1. **Photos terrain** - Prenez des photos avec votre téléphone dans les écoles
2. **Google Images / Bing** - Recherchez "salle de classe Maroc", "laboratoire scolaire"
3. **Vidéos** - Extrayez des frames de vidéos de visites scolaires
4. **Kaggle** - Datasets publiques comme "School Classroom Objects"

### Règles :
- ✅ Minimum **100 images par classe** (idéal : 500+)
- ✅ Varier les angles, l'éclairage, l'orientation
- ✅ Images en **640x640** ou plus
- ✅ Éviter les images floues ou trop sombres
- ✅ Répartir : 70% train, 20% val, 10% test

---

## 🏷️ Annotation des images

### Outils recommandés :

| Outil | Plateforme | Prix |
|-------|-----------|------|
| **[LabelImg](https://github.com/HumanSignal/labelImg)** | Windows/Linux | Gratuit |
| **[CVAT](https://www.cvat.ai/)** | Web | Gratuit |
| **[Roboflow](https://roboflow.com/)** | Web | Gratuit (limité) |
| **[Label Studio](https://labelstud.io/)** | Web/Desktop | Gratuit |

### Format YOLO :
Chaque image `photo123.jpg` → un fichier `photo123.txt` contenant :

```
class_id x_center y_center width height
```

- Toutes les valeurs sont **normalisées** entre 0 et 1
- Format : `0 0.5 0.5 0.8 0.6` (Table au centre)

### Exemple avec LabelImg :
```bash
pip install labelImg
labelImg
# 1. Open Dir -> dataset/train/images
# 2. Change Save Dir -> dataset/train/labels
# 3. Select YOLO format
# 4. Draw bounding boxes et assigner les classes
```

---

## 🚀 Entraînement

```bash
cd yolo_training
python train_yolo.py
```

### Paramètres clés (éditez `train_yolo.py`) :
- `EPOCHS` : 100 par défaut (300 pour meilleure précision)
- `BATCH_SIZE` : 16 (réduire à 8 si mémoire insuffisante)
- `IMG_SIZE` : 640 (taille standard YOLO)
- `DEVICE` : "cuda" si GPU NVIDIA, "cpu" sinon
- `BASE_MODEL` : "yolo11n.pt" (nano), "yolo11s.pt" (small)

### Résultats :
```
runs/detect/weights/
    ├── best.pt    ← Meilleur modèle (à utiliser)
    └── last.pt    ← Dernière époque
```

---

## 🔧 Intégration dans l'application

Après fine-tuning, remplacez le modèle dans `yolo_service.py` :

```python
class YoloService:
    def __init__(self) -> None:
        # Ancien : modele COCO generique
        # self.model = YOLO("yolo11n-seg.pt")
        
        # Nouveau : modele fine-tune
        self.model = YOLO("yolo_training/runs/detect/weights/best.pt")
    
    def detect_raw(self, stored_filename: str) -> List[Dict[str, Any]]:
        # Plus besoin de mapping COCO -> School
        # Les classes sont directement les bonnes !
        ...
```

Le mapping des classes sera directement :

```python
# Le modele fine-tune a deja les bonnes classes
CLASS_NAMES = {
    0: "Table",
    1: "Chaise",
    2: "Ordinateur",
    3: "Imprimante",
    4: "Videoprojecteur",
    5: "Extincteur",
}
```

---

## 📊 Évaluation

Le script `train_yolo.py` affiche automatiquement :
- **mAP@50** : Précision moyenne à 50% IoU (cible : >0.85)
- **mAP@50:95** : Précision moyenne sur différents seuils (cible : >0.60)
- **Precision** : Taux de vrais positifs (cible : >0.90)
- **Recall** : Taux de détection (cible : >0.85)
- **F1-score** : Balance précision/rappel (cible : >0.87)

---

## 📝 Notes

- Le fine-tuning peut prendre **2-8 heures** selon le GPU et le nombre d'images
- Sans GPU, utilisez Google Colab (GPU gratuit) :
  ```python
  # Dans Colab : Runtime -> Change runtime type -> T4 GPU
  !pip install ultralytics
  !python train_yolo.py
  ```
- Pour un modèle plus précis, préférez `yolo11m.pt` (medium) ou `yolo11l.pt` (large)
