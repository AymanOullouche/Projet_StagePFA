"""
Service de detection d'equipements scolaires.
Support 3 modeles (par ordre de priorite) :
  1. YOLO-World (open-vocabulary)
  2. Modele custom fine-tune (best.pt)
  3. YOLO11 COCO (fallback)
"""

from pathlib import Path
from typing import Any, Dict, List
from ultralytics import YOLO
from .config import UPLOADS_DIR

# BUGFIX #1: Chemins absolus (les .pt sont a la racine du projet)
PROJECT_ROOT = Path(__file__).resolve().parents[3]
CUSTOM_MODEL_PATH = PROJECT_ROOT / "yolo_training" / "runs" / "detect" / "weights" / "best.pt"

# YOLO-World (57MB a la racine, pas dans backend/fastapi/)
WORLD_MODEL_PATH = PROJECT_ROOT / "yolov8m-worldv2.pt"

# BUGFIX #3: Noms optimises (phrases descriptives > mots isoles)
WORLD_CLASSES_EN = [
    "table", "desk", "chair", "computer monitor", "desktop computer",
    "printer", "projector", "fire extinguisher", "mouse", "keyboard",
]
EN_TO_FR = {
    "table": "Table", "desk": "Table",
    "chair": "Chaise",
    "computer monitor": "Ordinateur", "desktop computer": "Ordinateur",
    "printer": "Imprimante",
    "projector": "Videoprojecteur",
    "fire extinguisher": "Extincteur",
    "mouse": "Souris",
    "keyboard": "Clavier",
}
MAJOR_EQUIPMENTS = {"Table","Chaise","Ordinateur","Videoprojecteur","Extincteur","Imprimante"}

# Fallback COCO
COCO_FALLBACK = PROJECT_ROOT / "yolo11n-seg.pt"
COCO_LOCAL = Path(__file__).resolve().parent.parent / "yolo11n-seg.pt"
COCO_TO_SCHOOL = {56:"Chaise",60:"Table",62:"Videoprojecteur",63:"Ordinateur",64:"Souris",66:"Clavier"}
CUSTOM_CLASS_NAMES = {0:"Table",1:"Chaise",2:"Ordinateur",3:"Imprimante",4:"Videoprojecteur",5:"Extincteur"}

# BUGFIX #5: Ajout Extincteur dans Salle informatique (match frontend)
ROOM_NORMS = {
    "Salle informatique": {"Table":12,"Chaise":12,"Ordinateur":12,"Videoprojecteur":1,"Extincteur":1},
    "Laboratoire": {"Table":10,"Chaise":20,"Extincteur":2},
    "Salle standard": {"Table":15,"Chaise":30,"Videoprojecteur":1},
}

class YoloService:
    """Service de detection d'equipements scolaires."""

    def __init__(self, conf_threshold: float = 0.10) -> None:
        """BUGFIX #2: conf=0.10 (seuil equilibre precision/rappel)"""
        self.conf_threshold = conf_threshold
        self.model = None
        self.class_names = {}

        if WORLD_MODEL_PATH.exists():
            sz = WORLD_MODEL_PATH.stat().st_size // (1024*1024)
            print(f"[YOLO] World: {WORLD_MODEL_PATH.name} ({sz}MB)")
            self.model = YOLO(str(WORLD_MODEL_PATH))
            self.model.set_classes(WORLD_CLASSES_EN)
            self.class_names = {i: EN_TO_FR[n] for i,n in enumerate(WORLD_CLASSES_EN)}
            print(f"[YOLO] Classes: {list(EN_TO_FR.values())}")

        elif CUSTOM_MODEL_PATH.exists():
            print(f"[YOLO] Custom: {CUSTOM_MODEL_PATH}")
            self.model = YOLO(str(CUSTOM_MODEL_PATH))
            self.class_names = CUSTOM_CLASS_NAMES

        else:
            coco = COCO_LOCAL if COCO_LOCAL.exists() else COCO_FALLBACK
            if not coco.exists():
                print("[YOLO] AUCUN MODELE!")
                return
            print(f"[YOLO] Fallback COCO: {coco.name}")
            self.model = YOLO(str(coco))
            self.class_names = COCO_TO_SCHOOL

        print(f"[YOLO] OK - {len(self.class_names)} classes (seuil={self.conf_threshold})")

    def detect_raw(self, fn: str) -> list:
        ip = UPLOADS_DIR / fn
        if not ip.exists():
            return []
        results = self.model(str(ip), conf=self.conf_threshold, verbose=False)
        dets = []
        for r in results:
            if r.boxes is None:
                continue
            for b in r.boxes:
                cid = int(b.cls[0])
                if cid not in self.class_names:
                    continue
                dets.append({"nom": self.class_names[cid], "quantite": 1, "confiance": round(float(b.conf[0]), 3)})
        agg = {}
        for d in dets:
            n = d["nom"]
            if n not in agg:
                agg[n] = dict(d)
            else:
                agg[n]["quantite"] += 1
                if d["confiance"] > agg[n]["confiance"]:
                    agg[n]["confiance"] = d["confiance"]
        return list(agg.values())

    def analyze_image(self, fn: str, rt: str = "Salle standard") -> dict:
        eqs = self.detect_raw(fn)
        norms = ROOM_NORMS.get(rt, ROOM_NORMS["Salle standard"])
        anom, finds = [], []
        dm = {e["nom"]: e["quantite"] for e in eqs}
        for equip, req in norms.items():
            dq = dm.get(equip, 0)
            if dq < req:
                mq = req - dq
                anom.append({"type": f"INSUFF_{equip.upper()}", "equipement": equip, "requis": req, "detecte": dq, "manquants": mq, "gravite": "ELEVEE" if mq >= 5 else "MOYENNE"})
                finds.append(f"{equip}: {dq}/{req} ({mq} manquant(s))")
        total_r = sum(norms.values())
        total_d = sum(dm.get(e, 0) for e in norms)
        score = min(100, round((total_d / max(total_r, 1)) * 100))
        nd = [{"equipement": e, "requis": r, "detecte": dm.get(e, 0), "manquants": max(0, r - dm.get(e, 0)), "conforme": dm.get(e, 0) >= r} for e, r in norms.items()]
        return {"equipments": eqs, "norms": norms, "norm_details": nd, "anomalies": anom, "nbAnomalies": len(anom), "scoreGlobal": score, "status": "TERMINEE", "findings": finds or ["Aucune anomalie detectee"]}

yolo_service = YoloService()
