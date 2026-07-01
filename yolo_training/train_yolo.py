"""
Script de fine-tuning YOLO11 pour la detection d'equipements scolaires.

Utilisation :
    python train_yolo.py

Etapes :
1. Placez vos images annotees dans dataset/train/images/ et dataset/train/labels/
2. Ajustez les parametres ci-dessous (EPOCHS, BATCH_SIZE, IMG_SIZE)
3. Lancez le script
4. Le modele fine-tune sera dans runs/detect/train/weights/best.pt
"""

from ultralytics import YOLO
from pathlib import Path

# ── Parametres ──────────────────────────────────────────────
EPOCHS = 100           # Nombre d'epoques (augmenter pour plus de precision)
BATCH_SIZE = 16        # Taille du batch (reduire si GPU limite)
IMG_SIZE = 640         # Taille d'image d'entree (pixels)
PATIENCE = 20          # Early stopping si pas d'amelioration
LR = 0.001             # Learning rate initial
DEVICE = "cpu"         # "cuda" si GPU disponible, "cpu" sinon

# Modele de base pour le fine-tuning
# Options: yolo11n.pt (nano), yolo11s.pt (small), yolo11m.pt (medium)
BASE_MODEL = "yolo11n.pt"

# Chemin vers le dataset
DATA_YAML = str(Path(__file__).resolve().parent / "dataset" / "data.yaml")
# ────────────────────────────────────────────────────────────


def main():
    print("=" * 60)
    print(f"  Fine-Tuning YOLO - Inspection Scolaire")
    print(f"  Modele de base : {BASE_MODEL}")
    print(f"  Epoques        : {EPOCHS}")
    print(f"  Batch size     : {BATCH_SIZE}")
    print(f"  Device         : {DEVICE}")
    print(f"  Dataset        : {DATA_YAML}")
    print("=" * 60)

    # Charger le modele pre-entraine
    model = YOLO(BASE_MODEL)

    # Lancer l'entrainement
    results = model.train(
        data=DATA_YAML,
        epochs=EPOCHS,
        batch=BATCH_SIZE,
        imgsz=IMG_SIZE,
        patience=PATIENCE,
        lr0=LR,
        device=DEVICE,
        project="runs",
        name="detect",
        exist_ok=True,
        pretrained=True,
        verbose=True,
    )

    print(f"\n✅ Entrainement termine !")
    print(f"   Modele : runs/detect/weights/best.pt")
    print(f"\nPour utiliser le modele fine-tune :")
    print(f"   from ultralytics import YOLO")
    print(f"   model = YOLO('runs/detect/weights/best.pt')")
    print(f"   results = model('photo_salle.jpg')")


if __name__ == "__main__":
    main()
