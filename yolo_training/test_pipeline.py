from pathlib import Path
from ultralytics import YOLO

EPOCHS = 3
BATCH_SIZE = 8
IMG_SIZE = 320
PATIENCE = 5
DEVICE = "cpu"
BASE_MODEL = str(Path(__file__).resolve().parent / "yolo11n.pt")
DATA_YAML = str(Path(__file__).resolve().parent / "dataset" / "data.yaml")

print("=" * 60)
print("Quick Training - YOLO Inspection Scolaire")
print(f"Model: {BASE_MODEL}")
print(f"Epochs: {EPOCHS}")
print(f"Batch: {BATCH_SIZE}")
print(f"Image size: {IMG_SIZE}")
print(f"Device: {DEVICE}")
print(f"Data: {DATA_YAML}")
print("=" * 60)

model = YOLO(BASE_MODEL)

results = model.train(
    data=DATA_YAML,
    epochs=EPOCHS,
    batch=BATCH_SIZE,
    imgsz=IMG_SIZE,
    patience=PATIENCE,
    lr0=0.001,
    device=DEVICE,
    project="runs",
    name="detect",
    exist_ok=True,
    pretrained=True,
    verbose=True,
)

print("\nTraining complete!")
weights = Path(__file__).resolve().parent / "runs" / "detect" / "weights"
if weights.exists():
    print(f"Model weights: {weights}")
    for f in weights.iterdir():
        print(f"  - {f.name}")


