"""
Service YOLO pour la detection d'equipements dans les salles de classe.
Mappe les classes COCO vers les equipements scolaires :
Tables, Chaises, Ordinateurs, Videoprojecteurs.
"""

from pathlib import Path
from typing import Any, Dict, List

from ultralytics import YOLO

from .config import UPLOADS_DIR

# Mapping des classes COCO vers equipements scolaires
# 56=chair, 60=dining table, 63=laptop, 62=tv, 64=mouse, 66=keyboard
COCO_TO_SCHOOL: Dict[int, str] = {
    56: "Chaise",
    60: "Table",
    63: "Ordinateur",
    62: "Videoprojecteur",
    64: "Souris",
    66: "Clavier",
}

MAJOR_EQUIPMENTS = {"Table", "Chaise", "Ordinateur", "Videoprojecteur"}

ROOM_NORMS: Dict[str, Dict[str, int]] = {
    "Salle informatique": {
        "Table": 12, "Chaise": 12, "Ordinateur": 12, "Videoprojecteur": 1,
    },
    "Laboratoire": {
        "Table": 10, "Chaise": 20,
    },
    "Salle standard": {
        "Table": 15, "Chaise": 30, "Videoprojecteur": 1,
    },
}


class YoloService:
    """Service YOLO pour la detection d'equipements dans les images.
    Utilise ``yolo11n-seg.pt`` (pre-entraine sur COCO).
    """

    def __init__(self) -> None:
        self.model = YOLO("yolo11n-seg.pt")

    def detect_raw(self, stored_filename: str) -> List[Dict[str, Any]]:
        """Detecte tous les objets pertinents (classes COCO mappees) dans l'image."""
        image_path = UPLOADS_DIR / stored_filename
        if not image_path.exists():
            return []

        results = self.model(str(image_path))
        detections: List[Dict[str, Any]] = []

        for result in results:
            if result.boxes is None:
                continue
            for box in result.boxes:
                class_id = int(box.cls[0])
                if class_id not in COCO_TO_SCHOOL:
                    continue
                equip_name = COCO_TO_SCHOOL[class_id]
                detections.append({
                    "nom": equip_name,
                    "quantite": 1,
                    "confiance": round(float(box.conf[0]), 3),
                })

        # Agregation par type d'equipement
        aggregated: Dict[str, Dict[str, Any]] = {}
        for det in detections:
            nom = det["nom"]
            if nom not in aggregated:
                aggregated[nom] = {
                    "nom": nom,
                    "quantite": det["quantite"],
                    "confiance": det["confiance"],
                }
            else:
                aggregated[nom]["quantite"] += det["quantite"]
                if det["confiance"] > aggregated[nom]["confiance"]:
                    aggregated[nom]["confiance"] = det["confiance"]

        return list(aggregated.values())

    def analyze_image(
        self,
        stored_filename: str,
        room_type: str = "Salle standard",
    ) -> Dict[str, Any]:
        """Analyse une image et retourne un resultat standardise pour l'inspection.

        Args:
            stored_filename: Nom du fichier stocke sur le disque.
            room_type: Type de salle (Salle informatique, Laboratoire, Salle standard).

        Returns:
            Dictionnaire avec equipments, norms, anomalies, scoreGlobal, status, findings.
        """
        equipments = self.detect_raw(stored_filename)
        norms = ROOM_NORMS.get(room_type, ROOM_NORMS["Salle standard"])

        anomalies_list: List[Dict[str, Any]] = []
        findings: List[str] = []

        detected_map = {eq["nom"]: eq["quantite"] for eq in equipments}

        for equip, required_qty in norms.items():
            detected_qty = detected_map.get(equip, 0)
            if detected_qty < required_qty:
                manquants = required_qty - detected_qty
                anomalies_list.append({
                    "type": f"INSUFFISANCE_{equip.upper()}",
                    "equipement": equip,
                    "requis": required_qty,
                    "detecte": detected_qty,
                    "manquants": manquants,
                    "gravite": "ELEVEE" if manquants >= 5 else "MOYENNE",
                })
                findings.append(
                    f"{equip}: {detected_qty}/{required_qty} detecte(s) ({manquants} manquant(s))"
                )

        # Calcul du score
        total_required = sum(norms.values())
        total_detected = sum(detected_map.get(equip, 0) for equip in norms)
        score = min(100, round((total_detected / max(total_required, 1)) * 100))

        norm_details = []
        for equip, required_qty in norms.items():
            detected_qty = detected_map.get(equip, 0)
            norm_details.append({
                "equipement": equip,
                "requis": required_qty,
                "detecte": detected_qty,
                "manquants": max(0, required_qty - detected_qty),
                "conforme": detected_qty >= required_qty,
            })

        return {
            "equipments": equipments,
            "norms": norms,
            "norm_details": norm_details,
            "anomalies": anomalies_list,
            "nbAnomalies": len(anomalies_list),
            "scoreGlobal": score,
            "status": "TERMINEE",
            "findings": findings
            or ["Aucune anomalie detectee. Tous les equipements sont conformes."],
        }


yolo_service = YoloService()
