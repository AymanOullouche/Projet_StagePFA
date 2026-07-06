"""
Generation d'un dataset synthetique pour tester le pipeline YOLO.
Cree des images avec des formes geometriques simulant les 6 classes.

Utilisation :
    python generate_test_dataset.py                   # 20 images/classe
    python generate_test_dataset.py --count 50        # 50 images/classe
    python generate_test_dataset.py --show            # Affiche un apercu
"""

import os
import argparse
import cv2
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent / "dataset"

CLASSES = [
    ("Table",          0, (139, 90,  43)),   # Marron
    ("Chaise",         1, (100, 149, 237)),  # Bleu ciel
    ("Ordinateur",     2, (60,  179, 113)),  # Vert
    ("Imprimante",     3, (220, 20,  60)),   # Rouge
    ("Videoprojecteur",4, (255, 215, 0)),    # Or
    ("Extincteur",     5, (255, 69,  0)),    # Orange-rouge
]


def draw_synthetic_image(
    cls_id: int,
    cls_name: str,
    img_size: int = 640,
) -> tuple:
    """
    Cree une image synthetique avec un objet de la classe.

    Returns:
        (image, annotation_yolo)
    """
    img = np.ones((img_size, img_size, 3), dtype=np.uint8) * 255
    h, w = img_size, img_size

    # Position et taille aleatoires
    margin = 40
    bw = np.random.randint(60, min(250, w // 2))
    bh = np.random.randint(60, min(250, h // 2))
    cx = np.random.randint(margin + bw // 2, w - margin - bw // 2)
    cy = np.random.randint(margin + bh // 2, h - margin - bh // 2)
    x1, y1 = cx - bw // 2, cy - bh // 2
    x2, y2 = cx + bw // 2, cy + bh // 2

    color = CLASSES[cls_id][2]
    c_noise = tuple(min(255, max(0, c + np.random.randint(-30, 30))) for c in color)

    # Forme specifique selon la classe
    if cls_id == 0:  # Table
        cv2.rectangle(img, (x1, y1), (x2, y2), c_noise, -1)
        cv2.rectangle(img, (x1 + 5, y2 - 10), (x1 + 20, y2 + 30), (80, 50, 20), -1)
        cv2.rectangle(img, (x2 - 20, y2 - 10), (x2 - 5, y2 + 30), (80, 50, 20), -1)
    elif cls_id == 1:  # Chaise
        cv2.rectangle(img, (x1, y1), (x2, y2), c_noise, -1)
        cv2.rectangle(img, (x1 + 5, y1 - 20), (x2 - 5, y1 + 5), c_noise, -1)
        cv2.rectangle(img, (x1 + 5, y2 - 5), (x1 + 15, y2 + 25), (60, 60, 60), -1)
        cv2.rectangle(img, (x2 - 15, y2 - 5), (x2 - 5, y2 + 25), (60, 60, 60), -1)
    elif cls_id == 2:  # Ordinateur
        cv2.rectangle(img, (x1, y1), (x2, y2), c_noise, -1)
        cv2.rectangle(img, (x1 + 5, y1 + 5), (x2 - 5, y2 - 20), (200, 200, 255), -1)
        cv2.rectangle(img, (cx - 15, y2 - 5), (cx + 15, y2 + 15), (100, 100, 100), -1)
    elif cls_id == 3:  # Imprimante
        cv2.rectangle(img, (x1, y1), (x2, y2), c_noise, -1)
        cv2.rectangle(img, (x1 + 10, y1 + 5), (x2 - 10, y1 + 25), (255, 255, 255), -1)
        for i in range(3):
            cv2.circle(img, (x1 + 20 + i * 20, y2 - 15), 5, (50, 50, 200), -1)
    elif cls_id == 4:  # Videoprojecteur
        cv2.rectangle(img, (x1, y1), (x2, y2), c_noise, -1)
        cv2.circle(img, (cx, cy), bw // 6, (50, 50, 50), -1)
        cv2.circle(img, (cx, cy), bw // 8, (100, 150, 255), -1)
    elif cls_id == 5:  # Extincteur
        cv2.rectangle(img, (cx - bw // 4, y1), (cx + bw // 4, y2), c_noise, -1)
        cv2.ellipse(img, (cx, y1), (bw // 4, bh // 6), 0, 0, 180, c_noise, -1)
        cv2.ellipse(img, (cx, y2), (bw // 4, bh // 6), 0, 0, 180, c_noise, -1)
        cv2.rectangle(img, (cx - bw // 6, y1 + bh // 4),
                      (cx + bw // 6, y1 + bh // 2), (255, 255, 255), -1)
        cv2.putText(img, "FEU", (cx - 15, y1 + bh // 4 + 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 255), 1)

    # Bruit de fond leger
    noise = np.random.normal(0, 5, img.shape).astype(np.uint8)
    img = cv2.add(img, noise)

    # Annotation YOLO normalisee
    yolo_box = f"{cls_id} {cx/w:.6f} {cy/h:.6f} {bw/w:.6f} {bh/h:.6f}"

    return img, yolo_box


def generate_dataset(images_per_class: int = 20, show_sample: bool = False):
    """Genere le dataset synthetique dans train/val/test."""
    for split in ["train", "val", "test"]:
        for sub in ["images", "labels"]:
            os.makedirs(BASE_DIR / split / sub, exist_ok=True)

    total = 0
    for cls_name, cls_id, _ in CLASSES:
        n_train = int(images_per_class * 0.7)
        n_val = int(images_per_class * 0.2)
        n_test = images_per_class - n_train - n_val

        for i in range(images_per_class):
            img, yolo_box = draw_synthetic_image(cls_id, cls_name)

            if i < n_train:
                split = "train"
            elif i < n_train + n_val:
                split = "val"
            else:
                split = "test"

            fname = f"{cls_name.lower()}_{i:04d}"
            cv2.imwrite(str(BASE_DIR / split / "images" / f"{fname}.jpg"), img)
            with open(BASE_DIR / split / "labels" / f"{fname}.txt", "w") as f:
                f.write(yolo_box + "\n")
            total += 1

        print(f"  [OK] {cls_name:15s} : {images_per_class} images generees")

    print(f"\n  TOTAL : {total} images")
    print(f"  ├─ train/ : {total * 70 // 100} images")
    print(f"  ├─ val/   : {total * 20 // 100} images")
    print(f"  └─ test/  : {total * 10 // 100} images")

    if show_sample:
        for cls_name, cls_id, _ in CLASSES:
            fname = f"{cls_name.lower()}_0000"
            img_path = BASE_DIR / "train" / "images" / f"{fname}.jpg"
            if img_path.exists():
                img = cv2.imread(str(img_path))
                cv2.imshow(cls_name, img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser(description="Generation dataset synthetique YOLO")
    parser.add_argument("--count", type=int, default=20,
                        help="Nombre d'images par classe (defaut: 20)")
    parser.add_argument("--show", action="store_true",
                        help="Afficher un apercu des images")
    args = parser.parse_args()

    print("=" * 60)
    print("  Generation de dataset synthetique YOLO")
    print(f"  {args.count} images x {len(CLASSES)} classes = {args.count * len(CLASSES)} images")
    print("=" * 60)
    generate_dataset(images_per_class=args.count, show_sample=args.show)
    print("\n  Dataset pret ! Lancez : python train_yolo.py")
    print("=" * 60)


if __name__ == "__main__":
    main()

