"""
Data augmentation pour enrichir le dataset d'entrainement.
Utilise des transformations pour multiplier les images existantes.

Usage :
    python data_augmentation.py
    # Cree des copies augmentees dans dataset/augmented/
"""

import cv2
import numpy as np
import os
import random
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent / "dataset"
IMG_DIR = BASE_DIR / "train" / "images"
LAB_DIR = BASE_DIR / "train" / "labels"
OUT_IMG = BASE_DIR / "augmented" / "images"
OUT_LAB = BASE_DIR / "augmented" / "labels"

# Nombre de variations par image originale
AUGMENTATIONS_PER_IMAGE = 3


def read_yolo_label(txt_path: Path):
    """Lit un fichier d'annotation YOLO."""
    if not txt_path.exists():
        return []
    boxes = []
    with open(txt_path, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 5:
                cls, cx, cy, w, h = map(float, parts)
                boxes.append([int(cls), cx, cy, w, h])
    return boxes


def write_yolo_label(txt_path: Path, boxes):
    """Ecrit un fichier d'annotation YOLO."""
    with open(txt_path, "w") as f:
        for box in boxes:
            cls, cx, cy, w, h = box
            f.write(f"{cls} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}\n")


def apply_brightness(img):
    """Variation de luminosite."""
    value = random.randint(-40, 40)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    v = np.clip(v.astype(int) + value, 0, 255).astype(np.uint8)
    hsv = cv2.merge([h, s, v])
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)


def apply_noise(img):
    """Ajout de bruit gaussien."""
    noise = np.random.normal(0, 15, img.shape).astype(np.uint8)
    return cv2.add(img, noise)


def apply_blur(img):
    """Flou gaussien leger."""
    k = random.choice([3, 5])
    return cv2.GaussianBlur(img, (k, k), 0)


def apply_flip(img, boxes):
    """Retournement horizontal (miroir)."""
    h, w = img.shape[:2]
    img = cv2.flip(img, 1)
    flipped = []
    for box in boxes:
        cls, cx, cy, bw, bh = box
        flipped.append([cls, 1.0 - cx, cy, bw, bh])
    return img, flipped


def main():
    os.makedirs(OUT_IMG, exist_ok=True)
    os.makedirs(OUT_LAB, exist_ok=True)

    image_exts = {".jpg", ".jpeg", ".png"}
    images = [f for f in os.listdir(IMG_DIR) if f.lower().endswith(tuple(image_exts))]

    if not images:
        print("Aucune image trouvee dans dataset/train/images/")
        return

    print(f"Generation d'augmentations pour {len(images)} images...")
    count = 0

    for img_name in images:
        stem = Path(img_name).stem
        img_path = IMG_DIR / img_name
        lab_path = LAB_DIR / f"{stem}.txt"

        img = cv2.imread(str(img_path))
        if img is None:
            continue

        boxes = read_yolo_label(lab_path)
        if not boxes:
            continue

        h, w = img.shape[:2]
        if h == 0 or w == 0:
            continue

        transforms = [
            ("brightness", apply_brightness),
            ("noise", apply_noise),
            ("blur", apply_blur),
        ]

        for aug_idx in range(AUGMENTATIONS_PER_IMAGE):
            aug_img = img.copy()
            aug_boxes = [list(b) for b in boxes]

            # Appliquer 1-2 transformations aleatoires
            selected = random.sample(transforms, random.randint(1, 2))
            for name, func in selected:
                if name == "flip":
                    aug_img, aug_boxes = func(aug_img, aug_boxes)
                else:
                    aug_img = func(aug_img)

            out_name = f"{stem}_aug{aug_idx}.jpg"
            cv2.imwrite(str(OUT_IMG / out_name), aug_img)
            write_yolo_label(OUT_LAB / f"{stem}_aug{aug_idx}.txt", aug_boxes)
            count += 1

    print(f"✅ {count} images augmentees creees dans dataset/augmented/")
    print(f"   Copiez-les dans dataset/train/ :")
    print(f"   copy dataset\\augmented\\images\\* dataset\\train\\images\\")
    print(f"   copy dataset\\augmented\\labels\\* dataset\\train\\labels\\")


if __name__ == "__main__":
    main()
