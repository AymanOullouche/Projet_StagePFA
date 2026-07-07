"""Service avance : double-passage, seuils par classe, fusion, reco dynamiques."""
from pathlib import Path
from typing import Any, Dict, List
from ultralytics import YOLO
from .config import UPLOADS_DIR

PROJECT_ROOT = Path(__file__).resolve().parents[3]
CUSTOM_MODEL_PATH = PROJECT_ROOT / "yolo_training" / "runs" / "detect" / "weights" / "best.pt"
WORLD_MODEL_PATH = PROJECT_ROOT / "yolov8m-worldv2.pt"

# Amelioration #1+#4: 15 prompts -> 8 classes (synonymes)
WORLD_CLASSES_EN = [
    "table","desk","dining table","chair","office chair",
    "computer monitor","desktop computer","laptop","screen",
    "printer","projector","fire extinguisher",
    "mouse","computer mouse","keyboard","computer keyboard",
]
EN_TO_FR = {
    "table":"Table","desk":"Table","dining table":"Table",
    "chair":"Chaise","office chair":"Chaise",
    "computer monitor":"Ordinateur","desktop computer":"Ordinateur",
    "laptop":"Ordinateur","screen":"Ordinateur",
    "printer":"Imprimante","projector":"Videoprojecteur",
    "fire extinguisher":"Extincteur",
    "mouse":"Souris","computer mouse":"Souris",
    "keyboard":"Clavier","computer keyboard":"Clavier",
}
MAJOR_EQUIPMENTS = {"Table","Chaise","Ordinateur","Videoprojecteur","Extincteur","Imprimante"}

# Amelioration #3: Seuils de confiance par classe
PER_CLASS_THRESHOLDS = {
    "Table":0.08,"Chaise":0.10,"Ordinateur":0.12,
    "Imprimante":0.18,"Videoprojecteur":0.15,
    "Extincteur":0.18,"Souris":0.10,"Clavier":0.10,
}

COCO_FALLBACK = PROJECT_ROOT / "yolo11n-seg.pt"
COCO_LOCAL = Path(__file__).resolve().parent.parent / "yolo11n-seg.pt"
COCO_TO_SCHOOL = {56:"Chaise",60:"Table",62:"Videoprojecteur",63:"Ordinateur",64:"Souris",66:"Clavier"}
CUSTOM_CLASS_NAMES = {0:"Table",1:"Chaise",2:"Ordinateur",3:"Imprimante",4:"Videoprojecteur",5:"Extincteur"}
ROOM_NORMS = {
    "Salle informatique":{"Table":12,"Chaise":12,"Ordinateur":12,"Videoprojecteur":1,"Extincteur":1},
    "Laboratoire":{"Table":10,"Chaise":20,"Extincteur":2},
    "Salle standard":{"Table":15,"Chaise":30,"Videoprojecteur":1},
}



class YoloService:
    """Detection double-passage + seuils par classe + fusion + reco dynamiques."""

    def __init__(self) -> None:
        self.model = None; self.class_names = {}; self._load_model()

    def _load_model(self) -> None:
        if WORLD_MODEL_PATH.exists():
            sz = WORLD_MODEL_PATH.stat().st_size // (1024*1024)
            print(f"[YOLO] World: {WORLD_MODEL_PATH.name} ({sz}MB)")
            self.model = YOLO(str(WORLD_MODEL_PATH))
            self.model.set_classes(WORLD_CLASSES_EN)
            self.class_names = {i:EN_TO_FR[n] for i,n in enumerate(WORLD_CLASSES_EN)}
            print(f"[YOLO] Classes: {sorted(set(EN_TO_FR.values()))}")
        elif CUSTOM_MODEL_PATH.exists():
            print(f"[YOLO] Custom: {CUSTOM_MODEL_PATH}")
            self.model = YOLO(str(CUSTOM_MODEL_PATH)); self.class_names = CUSTOM_CLASS_NAMES
        else:
            coco = COCO_LOCAL if COCO_LOCAL.exists() else COCO_FALLBACK
            if not coco.exists(): print("[YOLO] AUCUN MODELE!"); return
            print(f"[YOLO] Fallback COCO: {coco.name}")
            self.model = YOLO(str(coco)); self.class_names = COCO_TO_SCHOOL
        print(f"[YOLO] OK - {len(self.class_names)} prompts")

    def detect_raw(self, fn: str) -> list:
        ip = UPLOADS_DIR / fn
        if not ip.exists(): return []
        results = self.model(str(ip), conf=0.05, verbose=False)
        dets = []
        for r in results:
            if r.boxes is None: continue
            for b in r.boxes:
                cid = int(b.cls[0])
                if cid not in self.class_names: continue
                name = self.class_names[cid]; conf = float(b.conf[0])
                if conf < PER_CLASS_THRESHOLDS.get(name, 0.10): continue
                dets.append({"nom":name,"quantite":1,"confiance":round(conf,3)})
        agg = {}
        for d in dets:
            n = d["nom"]
            if n not in agg: agg[n] = dict(d)
            else:
                agg[n]["quantite"] += 1
                if d["confiance"] > agg[n]["confiance"]: agg[n]["confiance"] = d["confiance"]
        return list(agg.values())

    def analyze_image(self, fn: str, rt: str = "Salle standard") -> dict:
        return self._build_result(self.detect_raw(fn), rt)

    def analyze_multiple_images(self, fns: list, rt: str = "Salle standard") -> dict:
        """Fusion: MAX quantite + meilleure conf."""
        if not fns: return self._build_result([], rt)
        all_eqs = []
        for fn in fns:
            if not (UPLOADS_DIR / fn).exists(): continue
            all_eqs.extend(self.detect_raw(fn))
        fused = {}
        for eq in all_eqs:
            n = eq["nom"]
            if n not in fused: fused[n] = dict(eq)
            else:
                if eq["quantite"] > fused[n]["quantite"]: fused[n]["quantite"] = eq["quantite"]
                if eq["confiance"] > fused[n]["confiance"]: fused[n]["confiance"] = eq["confiance"]
        return self._build_result(list(fused.values()), rt)

    def _build_result(self, eqs: list, rt: str) -> dict:
        norms = ROOM_NORMS.get(rt, ROOM_NORMS["Salle standard"])
        anom, finds = [], []
        dm = {e["nom"]:e["quantite"] for e in eqs}
        for equip, req in norms.items():
            dq = dm.get(equip, 0)
            if dq < req:
                mq = req - dq
                grav = "ELEVEE" if mq >= 5 else "MOYENNE" if mq >= 2 else "FAIBLE"
                anom.append({"type":f"INSUFF_{equip.upper()}","equipement":equip,
                             "requis":req,"detecte":dq,"manquants":mq,"gravite":grav})
                finds.append(f"{equip}: {dq}/{req} ({mq} manquant(s))")
        total_r = sum(norms.values()); total_d = sum(dm.get(e,0) for e in norms)
        score = min(100, round((total_d/max(total_r,1))*100))
        nd = [{"equipement":e,"requis":r,"detecte":dm.get(e,0),
               "manquants":max(0,r-dm.get(e,0)),"conforme":dm.get(e,0)>=r} for e,r in norms.items()]
        reco = self._recommend(dm, norms, anom, score)
        return {"equipments":eqs,"norms":norms,"norm_details":nd,
                "anomalies":anom,"nbAnomalies":len(anom),"scoreGlobal":score,
                "status":"TERMINEE",
                "findings":finds or ["Aucune anomalie detectee"],
                "recommendations":reco}

    @staticmethod
    def _recommend(detected: dict, norms: dict, anomalies: list, score: int) -> list:
        reco = []
        if score >= 90: reco.append("Excellent! Tout conforme."); return reco
        elif score >= 70: reco.append("Bonne conformite. Ajustements mineurs.")
        elif score >= 50: reco.append("Conformite moyenne. Equipements a completer.")
        else: reco.append("Conformite INSUFFISANTE! Actions urgentes.")
        for a in anomalies:
            eq,mq,rq,dt = a["equipement"],a["manquants"],a["requis"],a["detecte"]
            if eq in ("Extincteur","Videoprojecteur"):
                reco.append(f"CRITIQUE {eq}: {dt}/{rq}. Ajoutez {mq}.")
            elif mq >= 5:
                reco.append(f"ACHAT URGENT {eq}: manque {mq}/{rq} ({dt} present(s)).")
            elif mq >= 2:
                reco.append(f"{eq}: complement {mq} unite(s) ({dt}/{rq}).")
            else:
                reco.append(f"{eq}: 1 manquant. Verifiez le stock.")
        extra = {k:v for k,v in detected.items() if k not in norms}
        if extra:
            s = ", ".join(f"{k}({v}x)" for k,v in extra.items())
            reco.append(f"Supplementaires: {s}.")
        if score < 50: reco.append("Inspection de suivi sous 2 semaines.")
        return reco

yolo_service = YoloService()
