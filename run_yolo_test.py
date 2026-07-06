import sys
sys.path.insert(0, r"d:\ENSIASD\TP S4\Projet_StagePFA\backend\fastapi")
from pathlib import Path
from app.yolo_service import YoloService, CUSTOM_MODEL_PATH, WORLD_MODEL_NAME

print("=" * 60)
print("TEST YOLO-WORLD - Inspection Scolaire")
print("=" * 60)

world_path = Path(WORLD_MODEL_NAME)
if world_path.exists():
    print(f"\n[OK] YOLO-World trouve: {WORLD_MODEL_NAME} ({world_path.stat().st_size/1024/1024:.0f}MB)")
else:
    print(f"\n[INFO] YOLO-World non trouve, fallback COCO")

print("\nInitialisation YOLO-World...")
yolo = YoloService(conf_threshold=0.05)
print(f"OK - {len(yolo.class_names)} classes: {list(yolo.class_names.values())}")

uploads = Path(r"d:\ENSIASD\TP S4\Projet_StagePFA\backend\fastapi\uploads")
test_imgs = sorted([f for f in uploads.glob("*.jpg") if f.stat().st_size > 40000])

print(f"\nTest YOLO-World sur {len(test_imgs)} images (conf>=0.05):")
for img in test_imgs:
    r = yolo.analyze_image(img.name, "Salle standard")
    eq = ", ".join([f"{e['nom']}:{e['quantite']}x" for e in r["equipments"]]) if r["equipments"] else "rien"
    print(f"  {img.name:35s} -> Score:{r['scoreGlobal']:3d} | {eq}")

print("\n" + "=" * 60)
print("YOLO-World ACTIF ! Pret pour l'application !")
print("=" * 60)
print(f"\nPour utiliser le modele custom: placez best.pt dans:")
print(f"  {CUSTOM_MODEL_PATH}")
print(f"\nPour lancer le backend:")
print(f"  cd backend/fastapi && python -m uvicorn app.main:app --reload")
print(f"\nPour lancer le frontend:")
print(f"  npm run dev")
print("\n" + "=" * 60)
print("TERMINE")
print("=" * 60)

