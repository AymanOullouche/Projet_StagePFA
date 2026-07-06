"""
Script d'extraction de frames depuis des videos pour enrichir le dataset.
Extrait des images cles a intervalle regulier avec filtre de qualite.

Installation :
    pip install opencv-python

Utilisation :
    python extract_from_video.py video.mp4                    # Extrait toutes les 30 frames
    python extract_from_video.py video.mp4 --every 10         # Toutes les 10 frames
    python extract_from_video.py video.mp4 --output dossier/  # Dossier personnalise
    python extract_from_video.py dossier_videos/              # Traite tout un dossier
    python extract_from_video.py video.mp4 --to-dataset       # Deplacer vers dataset/
"""

import os
import argparse
import cv2
from pathlib import Path


def extract_frames(
    video_path: str,
    output_dir: str,
    every_n_frames: int = 30,
    img_size: tuple = (640, 640),
    min_quality: float = 0.5,
) -> int:
    """
    Extrait des frames d'une video a intervalle regulier.

    Args:
        video_path: Chemin vers la video
        output_dir: Dossier de sortie pour les images
        every_n_frames: Extraire 1 frame toutes les N frames
        img_size: Redimensionner les images (largeur, hauteur)
        min_quality: Score de qualite minimal base sur la nettetete

    Returns:
        Nombre de frames extraites
    """
    os.makedirs(output_dir, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"  [ERR] Impossible d'ouvrir la video : {video_path}")
        return 0

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0

    video_name = Path(video_path).stem
    frame_count = 0
    saved_count = 0

    print(f"  Video  : {video_name}")
    print(f"  FPS    : {fps:.1f}")
    print(f"  Duree  : {duration:.1f}s ({total_frames} frames)")
    print(f"  Output : {output_dir}")
    print(f"  Every  : {every_n_frames} frames")
    print("-" * 40)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % every_n_frames == 0:
            if img_size:
                frame = cv2.resize(frame, img_size)

            # Evaluation de la qualite (nettete via Laplacian)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            quality_score = min(laplacian_var / 100.0, 1.0)

            if quality_score >= min_quality:
                filename = f"{video_name}_frame{saved_count:04d}.jpg"
                cv2.imwrite(os.path.join(output_dir, filename), frame)
                saved_count += 1

                if saved_count % 10 == 0:
                    print(f"  -> {saved_count} frames extraites...")

        frame_count += 1

    cap.release()
    print(f"\n  [OK] {saved_count}/{frame_count} frames extraites")
    return saved_count


def process_video_folder(
    folder_path: str,
    output_base: str,
    every_n_frames: int = 30,
    img_size: tuple = (640, 640),
) -> int:
    """Traite toutes les videos d'un dossier."""
    folder = Path(folder_path)
    video_exts = {".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv", ".webm"}
    videos = [f for f in folder.iterdir() if f.suffix.lower() in video_exts]

    if not videos:
        print(f"Aucune video trouvee dans {folder_path}")
        return 0

    print(f"\nTraitement de {len(videos)} videos dans {folder_path}")
    print("=" * 60)

    total_saved = 0
    for video in videos:
        output_dir = os.path.join(output_base, video.stem)
        saved = extract_frames(
            video_path=str(video),
            output_dir=output_dir,
            every_n_frames=every_n_frames,
            img_size=img_size,
        )
        total_saved += saved
        print()

    print("=" * 60)
    print(f"[OK] Total : {total_saved} frames extraites de {len(videos)} videos")
    return total_saved


def move_to_dataset(output_base: str):
    """Deplace les frames extraites dans dataset/train/images/."""
    dataset_dir = Path(__file__).resolve().parent / "dataset" / "train" / "images"
    os.makedirs(dataset_dir, exist_ok=True)

    output_path = Path(output_base)
    moved = 0
    for img_file in output_path.rglob("*.jpg"):
        new_name = f"{img_file.parent.name}_{img_file.name}"
        dst = dataset_dir / new_name
        if not dst.exists():
            os.rename(img_file, dst)
            moved += 1

    print(f"\n[OK] {moved} images deplacees vers {dataset_dir}")
    print("     N'oubliez pas de les annoter avec LabelImg !")


def main():
    parser = argparse.ArgumentParser(
        description="Extraction de frames depuis des videos pour dataset YOLO"
    )
    parser.add_argument(
        "input",
        help="Chemin vers la video OU le dossier contenant les videos",
    )
    parser.add_argument(
        "--every", type=int, default=30,
        help="Extraire 1 frame toutes les N frames (defaut: 30)",
    )
    parser.add_argument(
        "--output", default=None,
        help="Dossier de sortie (defaut: yolo_training/extracted_frames/)",
    )
    parser.add_argument(
        "--size", type=int, nargs=2, default=(640, 640),
        help="Taille des images (defaut: 640 640)",
    )
    parser.add_argument(
        "--quality", type=float, default=0.3,
        help="Seuil de qualite minimale 0-1 (defaut: 0.3)",
    )
    parser.add_argument(
        "--to-dataset", action="store_true",
        help="Deplacer automatiquement vers dataset/train/images/",
    )
    args = parser.parse_args()

    input_path = args.input
    base_dir = Path(__file__).resolve().parent
    output_base = args.output or str(base_dir / "extracted_frames")

    if os.path.isdir(input_path):
        process_video_folder(
            folder_path=input_path,
            output_base=output_base,
            every_n_frames=args.every,
            img_size=tuple(args.size),
        )
    elif os.path.isfile(input_path):
        extract_frames(
            video_path=input_path,
            output_dir=output_base,
            every_n_frames=args.every,
            img_size=tuple(args.size),
            min_quality=args.quality,
        )
    else:
        print(f"[ERR] Chemin invalide : {input_path}")
        return

    if args.to_dataset:
        move_to_dataset(output_base)


if __name__ == "__main__":
    main()
