"""Test YOLO sur les images reelles telechargees."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from app.yolo_service import YoloService, ROOM_NORMS

UPLOADS = Path(__file__).resolve().parent / "uploads"
yolo = YoloService()

print("=" * 60)
print("  TEST YOLO SUR IMAGES REELLES")
print("=" * 60)

for img_path in sorted(UPLOADS.glob("*.jpg")):
    if img_path.stat().st_size < 40000:
        continue
    print(f"\n{'=' * 60}")
    print(f"  Image: {img_path.name}")
    for rt in ["Salle informatique", "Salle standard"]:
        r = yolo.analyze_image(img_path.name, rt)
        print(f"\n  --- {rt} ---")
        print(f"  Score: {r['scoreGlobal']}/100 | Anomalies: {r['nbAnomalies']}")
        if r['equipments']:
            for e in r['equipments']:
                print(f"    {e['nom']}: {e['quantite']}x conf={e['confiance']:.1%}")
        else:
            print("    (rien detecte)")
        for f in r.get('findings', []):
            print(f"    -> {f}")
