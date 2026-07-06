import os
import zipfile
from pathlib import Path

DATASET_DIR = Path(r"d:\ENSIASD\TP S4\Projet_StagePFA\yolo_training\dataset")
OUTPUT_ZIP = Path(r"d:\ENSIASD\TP S4\Projet_StagePFA\yolo_training\dataset.zip")

def zip_dataset():
    print("=" * 60)
    print("Packaging dataset for Google Colab training")
    print("=" * 60)
    
    with zipfile.ZipFile(OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(DATASET_DIR):
            for file in files:
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, DATASET_DIR.parent)
                zf.write(full_path, arcname)
    
    size_mb = os.path.getsize(OUTPUT_ZIP) / (1024 * 1024)
    print(f"\nDataset zipped: {OUTPUT_ZIP}")
    print(f"Size: {size_mb:.1f} MB")
    print(f"Ready to upload to Google Colab!")
    
    # Count items
    train_imgs = len(os.listdir(DATASET_DIR / "train" / "images"))
    val_imgs = len(os.listdir(DATASET_DIR / "val" / "images"))
    print(f"\nDataset summary:")
    print(f"  Train: {train_imgs} images")
    print(f"  Val:   {val_imgs} images")
    print(f"  Classes: 6 (Table, Chaise, Ordinateur, Imprimante, Videoprojecteur, Extincteur)")

if __name__ == "__main__":
    zip_dataset()
