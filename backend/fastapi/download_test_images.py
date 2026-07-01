"""Telecharge des images test reelles pour tester YOLO (chaises, tables, ordinateurs)."""
import requests, io, os, sys
from pathlib import Path
from PIL import Image

OUT_DIR = Path(__file__).resolve().parent / "uploads"
OUT_DIR.mkdir(exist_ok=True)

# Images test issues de sources libres (Unsplash/Pexels) contenant des objets COCO
TEST_IMAGES = [
    ("salle_classe.jpg", "https://images.pexels.com/photos/256395/pexels-photo-256395.jpeg?auto=compress&w=800"),
    ("bureau_ordinateur.jpg", "https://images.pexels.com/photos/38568/apple-imac-ipad-workplace-38568.jpeg?auto=compress&w=800"),
    ("salle_reunion.jpg", "https://images.pexels.com/photos/1181359/pexels-photo-1181359.jpeg?auto=compress&w=800"),
    ("chaises_table.jpg", "https://images.pexels.com/photos/207691/pexels-photo-207691.jpeg?auto=compress&w=800"),
]

print("Telechargement d'images test pour YOLO...")
for name, url in TEST_IMAGES:
    path = OUT_DIR / name
    if path.exists():
        print(f"  Deja present: {name}")
        continue
    try:
        r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200:
            img = Image.open(io.BytesIO(r.content))
            img.save(path)
            print(f"  OK: {name} ({img.size})")
        else:
            print(f"  ERR: {name} HTTP {r.status_code}")
    except Exception as e:
        print(f"  ERR: {name} {e}")

print(f"\nImages disponibles dans {OUT_DIR}:")
for f in sorted(OUT_DIR.glob("*.*")):
    size_kb = f.stat().st_size // 1024
    print(f"  {f.name} ({size_kb} Ko)")
