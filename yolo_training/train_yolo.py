from pathlib import Path

from ultralytics import YOLO

try:
    import torch
except Exception:  # pragma: no cover - fallback for environments without torch
    torch = None

EPOCHS = 100
BATCH_SIZE = 16
IMG_SIZE = 640
PATIENCE = 20
LR = 0.001
DEVICE = "cuda" if torch is not None and torch.cuda.is_available() else "cpu"
BASE_MODEL = "yolo11n.pt"
DATA_YAML = str(Path(__file__).resolve().parent / "dataset" / "data.yaml")


def main():
    print("=" * 60)
    print(f"  Fine-Tuning YOLO - Inspection Scolaire")
    print(f"  Modele de base : {BASE_MODEL}")
    print(f"  Epoques        : {EPOCHS}")
    print(f"  Batch size     : {BATCH_SIZE}")
    print(f"  Device         : {DEVICE}")
    print(f"  Dataset        : {DATA_YAML}")
    print("=" * 60)

    model = YOLO(BASE_MODEL)

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

    print(f"\nEntrainement termine !")
    print(f"   Modele : runs/detect/weights/best.pt")


if __name__ == "__main__":
    main()

