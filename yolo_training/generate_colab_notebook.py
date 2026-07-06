#!/usr/bin/env python
"""Generate the Google Colab notebook for YOLO fine-tuning."""
import json, os

nb = {
 "cells": [],
 "metadata": {
  "accelerator": "GPU",
  "colab": {"provenance": [], "gpuType": "T4"},
  "kernelspec": {"display_name": "Python 3", "name": "python3"},
  "language_info": {"name": "python"}
 },
 "nbformat": 4,
 "nbformat_minor": 0
}

def md(src):
    nb["cells"].append({"cell_type": "markdown", "metadata": {}, "source": [src]})

def code(src):
    nb["cells"].append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "source": [src],
        "outputs": []
    })

# Title
md("# Fine-Tuning YOLO11 pour l'Inspection Scolaire\n\n"
   "Detecte 6 equipements : Tables, Chaises, Ordinateurs, Imprimantes, "
   "Videoprojecteurs, Extincteurs.\n\n"
   "---\n## Avant de commencer\n"
   "1. **Runtime -> Change runtime type -> T4 GPU**\n"
   "2. Executez les cellules dans l'ordre\n"
   "3. Modele final sauvegarde dans Google Drive")

code("# Installation des dependances\n"
     "!pip install -q ultralytics\n"
     "from ultralytics import YOLO\n"
     "from pathlib import Path\n"
     "import os, sys, yaml, shutil\n"
     "print('OK')")

code("# Monter Google Drive\n"
     "from google.colab import drive\n"
     "drive.mount('/content/drive')\n"
     "DRIVE_PATH = '/content/drive/MyDrive/inspection_scolaire_yolo'\n"
     "os.makedirs(DRIVE_PATH, exist_ok=True)")

md("---\n## Etape 1 : Upload du dataset")

code("# Upload dataset.zip\n"
     "from google.colab import files\n"
     "print('Uploader dataset.zip (data.yaml + train/ + val/ + test/)')\n"
     "uploaded = files.upload()\n"
     "for fn in uploaded.keys():\n"
     "    !unzip -o {fn} -d /content/dataset/\n"
     "\n"
     "yaml_path = list(Path('/content/dataset').rglob('data.yaml'))\n"
     "if yaml_path:\n"
     "    yaml_path = yaml_path[0]\n"
     "else:\n"
     "    yaml_path = list(Path('/content').rglob('data.yaml'))[0]\n"
     "    !cp -r {yaml_path.parent} /content/dataset/\n"
     "    yaml_path = Path('/content/dataset/data.yaml')\n"
     "print(f'data.yaml: {yaml_path}')")

code("# Exploration du dataset\n"
     "with open(yaml_path) as f:\n"
     "    data_cfg = yaml.safe_load(f)\n"
     "print(f'Classes: {data_cfg[\"nc\"]} - {data_cfg[\"names\"]}')\n"
     "for s in ['train','val','test']:\n"
     "    d = yaml_path.parent / data_cfg.get(s, f'{s}/images')\n"
     "    if d.exists(): print(f'{s}: {len(list(d.glob(\"*\")))} images')")

md("---\n## Etape 2 : Entrainement")

code("# Parametres\n"
     "EPOCHS, BATCH_SIZE, IMG_SIZE = 150, 32, 640\n"
     "BASE_MODEL, PATIENCE, LR = 'yolo11n.pt', 30, 0.001\n"
     "print('GPU:', !nvidia-smi --query-gpu=name --format=csv,noheader)")

code("# Lancer l'entrainement\n"
     "print('Entrainement YOLO...')\n"
     "model = YOLO(BASE_MODEL)\n"
     "model.train(data=str(yaml_path), epochs=EPOCHS, batch=BATCH_SIZE,\n"
     "            imgsz=IMG_SIZE, patience=PATIENCE, lr0=LR,\n"
     "            device='cuda', project='/content/runs',\n"
     "            name='inspection_scolaire', exist_ok=True,\n"
     "            pretrained=True, augment=True, verbose=True)\n"
     "print('Entrainement termine !')")

md("---\n## Etape 3 : Evaluation")

code("# Courbes d'entrainement\n"
     "from IPython.display import Image as IPImage\n"
     "rp = Path('/content/runs/inspection_scolaire')\n"
     "for img in ['results.png','confusion_matrix.png','F1_curve.png','PR_curve.png']:\n"
     "    f = rp / img\n"
     "    if f.exists(): display(IPImage(filename=str(f), width=800))")

code("# Test sur une image\n"
     "from google.colab.patches import cv2_imshow\n"
     "model = YOLO('/content/runs/inspection_scolaire/weights/best.pt')\n"
     "test_imgs = list(Path('/content/dataset/test/images').glob('*'))\n"
     "if test_imgs:\n"
     "    results = model(str(test_imgs[0]))\n"
     "    cv2_imshow(results[0].plot())\n"
     "    for box in results[0].boxes:\n"
     "        print(f'{results[0].names[int(box.cls[0])]}: {float(box.conf[0]):.2%}')")

md("---\n## Etape 4 : Sauvegarde")

code("# Sauvegarder dans Google Drive\n"
     "shutil.copytree('/content/runs/inspection_scolaire',\n"
     "                f'{DRIVE_PATH}/runs_inspection_scolaire',\n"
     "                dirs_exist_ok=True)\n"
     "shutil.copy2('/content/runs/inspection_scolaire/weights/best.pt',\n"
     "             f'{DRIVE_PATH}/best.pt')\n"
     "print(f'Modele: {DRIVE_PATH}/best.pt')")

code("# Telecharger best.pt\n"
     "from google.colab import files\n"
     "files.download('/content/runs/inspection_scolaire/weights/best.pt')")

md("---\n## Integration\n\n"
   "Dans `yolo_service.py` :\n"
   "```python\n"
   "class YoloService:\n"
   "    def __init__(self):\n"
   "        self.model = YOLO('best.pt')\n"
   "    def detect(self, image_path):\n"
   "        results = self.model(image_path)\n"
   "        return [{\n"
   "            'class_id': int(b.cls[0]),\n"
   "            'class_name': results[0].names[int(b.cls[0])],\n"
   "            'confidence': float(b.conf[0]),\n"
   "            'bbox': b.xyxy[0].tolist(),\n"
   "        } for b in results[0].boxes]\n"
   "```\n\n"
   "---\n## Resume\n"
   "1. Upload dataset -> OK\n"
   "2. Entrainement YOLO -> OK\n"
   "3. Evaluation -> OK\n"
   "4. Sauvegarde Drive -> OK")

# Write the notebook
out = r"d:\ENSIASD\TP S4\Projet_StagePFA\yolo_training\yolo_colab_training.ipynb"
with open(out, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

sz = os.path.getsize(out) / 1024
print(f"Notebook genere: {out} ({sz:.1f} Ko)")
print(f"Cellules: {len(nb['cells'])}")
