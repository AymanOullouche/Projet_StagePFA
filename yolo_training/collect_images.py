"""
Script de collecte automatique d'images depuis le web pour le fine-tuning YOLO.
Utilise icrawler (Bing) pour telecharger des images pour chaque classe.

Installation :
    pip install icrawler

Utilisation :
    python collect_images.py                     # Telecharge pour toutes les classes
    python collect_images.py --class Table        # Telecharge pour une classe specifique
    python collect_images.py --count 200          # 200 images par classe
    python collect_images.py --split 70:20:10     # Repartition train/val/test
"""

import os
import argparse
import random
import shutil
from pathlib import Path
from icrawler.builtin import BingImageCrawler, GoogleImageCrawler

# ── Configuration ──────────────────────────────────────────────
CLASSES = {
    "Table": [
        "table salle de classe école maroc",
        "table bureau salle de classe",
        "table école salle informatique",
    ],
    "Chaise": [
        "chaise salle de classe école",
        "chaise bureau école maroc",
        "chaise salle informatique scolaire",
    ],
    "Ordinateur": [
        "ordinateur salle informatique école",
        "pc bureau salle de classe",
        "ordinateur scolaire laboratoire",
    ],
    "Imprimante": [
        "imprimante bureau école",
        "photocopieur salle de classe",
        "imprimante salle informatique",
    ],
    "Videoprojecteur": [
        "vidéoprojecteur salle de classe",
        "projecteur interactif école",
        "écran interactif salle classe",
    ],
    "Extincteur": [
        "extincteur mural école",
        "extincteur salle de classe",
        "extincteur sécurité école",
    ],
}

BLACKLIST_TERMS = [
    "icon", "icone", "clipart", "cartoon", "vector", "illustration",
    "logo", "drawing", "3d", "render", "wallpaper", "landscape",
]

BASE_DIR = Path(__file__).resolve().parent / "dataset"
TEMP_DIR = BASE_DIR / "_temp_downloads"



# ── Fonctions ──────────────────────────────────────────────────


def prune_irrelevant_images(cls_dir: Path) -> int:
    """Supprime les fichiers douteux ou trop génériques après téléchargement."""
    removed = 0
    image_exts = {".jpg", ".jpeg", ".png", ".webp"}
    for root, _, files in os.walk(cls_dir):
        for f in files:
            path = Path(root) / f
            if path.suffix.lower() not in image_exts:
                continue
            name = path.name.lower()
            if any(term in name for term in BLACKLIST_TERMS):
                path.unlink(missing_ok=True)
                removed += 1
    return removed


def download_class_images(cls_name: str, queries: list, count: int = 150) -> int:
    """
    Telecharge des images pour une classe depuis Bing.
    Utilise plusieurs requetes pour varier les resultats.
    """
    cls_dir = TEMP_DIR / cls_name
    if cls_dir.exists():
        shutil.rmtree(cls_dir)
    os.makedirs(cls_dir, exist_ok=True)

    total_downloaded = 0
    per_query = max(count // len(queries), 10)

    for i, query in enumerate(queries):
        try:
            crawler = BingImageCrawler(
                storage={"root_dir": str(cls_dir / f"source_{i}")},
                feeder_threads=2,
                parser_threads=2,
                downloader_threads=4,
            )
            crawler.crawl(
                keyword=query,
                max_num=per_query,
                file_idx_offset=total_downloaded,
                min_size=(600, 600),
                max_size=(2048, 2048),
            )
            total_downloaded += per_query
            print(f"  [Bing] '{query}' -> {per_query} images")
        except Exception as e:
            print(f"  [Bing] Erreur pour '{query}' : {e}")

    removed = prune_irrelevant_images(cls_dir)
    if removed:
        print(f"  [Filter] {removed} fichiers supprimes comme trop génériques")

    return total_downloaded


def split_dataset(
    split_ratio: tuple = (70, 20, 10),
    min_images: int = 10,
):
    """
    Repartit les images telechargees en train/val/test.
    Cree les dossiers d'annotations vides (a remplir avec LabelImg).
    """
    train_r, val_r, test_r = split_ratio
    assert train_r + val_r + test_r == 100, "Les ratios doivent totaliser 100"

    splits = {
        "train": BASE_DIR / "train" / "images",
        "val": BASE_DIR / "val" / "images",
        "test": BASE_DIR / "test" / "images",
    }
    label_dirs = {
        "train": BASE_DIR / "train" / "labels",
        "val": BASE_DIR / "val" / "labels",
        "test": BASE_DIR / "test" / "labels",
    }

    for d in list(splits.values()) + list(label_dirs.values()):
        os.makedirs(d, exist_ok=True)

    image_exts = {".jpg", ".jpeg", ".png", ".webp"}

    for cls_name in CLASSES:
        cls_dir = TEMP_DIR / cls_name
        if not cls_dir.exists():
            print(f"  [ ] Aucune image trouvee pour '{cls_name}', ignoree.")
            continue

        # Rassembler toutes les images
        images = []
        for root, _, files in os.walk(cls_dir):
            for f in files:
                if Path(f).suffix.lower() in image_exts:
                    images.append(Path(root) / f)

        if len(images) < min_images:
            print(f"  [ ] '{cls_name}' : {len(images)} images (< {min_images}), ignoree.")
            continue

        # Melanger
        random.shuffle(images)

        # Calculer les indices de split
        n = len(images)
        n_train = int(n * train_r / 100)
        n_val = int(n * val_r / 100)

        # Copier dans les dossiers
        for idx, img_path in enumerate(images):
            if idx < n_train:
                split = "train"
            elif idx < n_train + n_val:
                split = "val"
            else:
                split = "test"

            new_name = f"{cls_name.lower()}_{idx:04d}{img_path.suffix.lower()}"
            dst = splits[split] / new_name
            shutil.copy2(img_path, dst)

            # Annotation vide (a remplir manuellement)
            label_file = label_dirs[split] / f"{Path(new_name).stem}.txt"
            label_file.touch()

        print(f"  [OK] '{cls_name}' : {n} images reparties "
              f"(train={n_train}, val={n_val}, test={n - n_train - n_val})")


def show_stats():
    """Affiche les statistiques du dataset apres collecte."""
    print("\n" + "=" * 60)
    print("  Statistiques du dataset")
    print("=" * 60)

    total_images = 0
    for split in ["train", "val", "test"]:
        img_dir = BASE_DIR / split / "images"
        label_dir = BASE_DIR / split / "labels"
        if img_dir.exists():
            images = list(img_dir.glob("*"))
            labels = list(label_dir.glob("*.txt"))
            annotated = sum(1 for l in labels if l.stat().st_size > 0)
            total_images += len(images)
            print(f"  {split.upper()} : {len(images)} images, "
                  f"{len(labels)} annotations ({annotated} avec objets)")
        else:
            print(f"  {split.upper()} : dossier absent")

    print(f"  ------------------------------")
    print(f"  TOTAL : {total_images} images")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Collecte automatique d'images pour fine-tuning YOLO"
    )
    parser.add_argument(
        "--class", dest="cls_name",
        help="Classe specifique a telecharger (defaut: toutes)",
    )
    parser.add_argument(
        "--count", type=int, default=150,
        help="Nombre d'images par classe (defaut: 150)",
    )
    parser.add_argument(
        "--no-download", action="store_true",
        help="Ne pas telecharger, seulement reorganiser les fichiers existants",
    )
    parser.add_argument(
        "--split", default="70:20:10",
        help="Ratio train:val:test (defaut: 70:20:10)",
    )
    parser.add_argument(
        "--stats", action="store_true",
        help="Afficher seulement les statistiques du dataset",
    )
    args = parser.parse_args()

    if args.stats:
        show_stats()
        return

    split_ratio = tuple(map(int, args.split.split(":")))
    assert len(split_ratio) == 3, "Format du split invalide. Utilisez 70:20:10"
    assert sum(split_ratio) == 100, "Les ratios doivent totaliser 100"

    print("=" * 60)
    print("  Collecte automatique d'images pour YOLO")
    print("=" * 60)

    classes_to_process = (
        [args.cls_name] if args.cls_name
        else list(CLASSES.keys())
    )

    # Phase 1 : Telechargement
    if not args.no_download:
        print(f"\nPhase 1 : Telechargement ({args.count} images/classe)")
        print("-" * 40)
        for cls_name in classes_to_process:
            if cls_name not in CLASSES:
                print(f"  Classe inconnue : '{cls_name}'")
                continue
            queries = CLASSES[cls_name]
            print(f"\n  [{cls_name}] Recherche : {queries}")
            n = download_class_images(cls_name, queries, count=args.count)
            print(f"  -> {n} images telechargees")
    else:
        print("\n[ ] Phase de telechargement ignoree (--no-download)")

    # Phase 2 : Organisation en train/val/test
    print(f"\nPhase 2 : Organisation du dataset (split {args.split})")
    print("-" * 40)
    split_dataset(split_ratio=split_ratio)

    # Phase 3 : Statistiques finales
    show_stats()

    print("\nProchaine etape : Annoter les images avec LabelImg")
    print("   pip install labelImg")
    print("   labelImg")
    print("\n   Puis lancer l'entrainement :")
    print("   python train_yolo.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
