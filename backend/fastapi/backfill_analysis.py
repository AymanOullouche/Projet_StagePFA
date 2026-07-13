import json
import sqlite3
from sqlalchemy import text

from app.database import SessionLocal, engine
from app.models import Inspection
from app.yolo_service import yolo_service


def room_type_of(salle):
    s = (salle or "").strip().lower()
    if "informatique" in s or " info" in s:
        return "Salle informatique"
    if "laboratoire" in s:
        return "Laboratoire"
    return "Salle standard"


# Ensure column exists (idempotent)
with engine.connect() as conn:
    cols = [r[1] for r in conn.execute(text("PRAGMA table_info(inspections)"))]
    if "resultat_analyse" not in cols:
        conn.execute(text("ALTER TABLE inspections ADD COLUMN resultat_analyse TEXT"))
        conn.commit()
        print("Colonne resultat_analyse ajoutee.")

db = SessionLocal()
n = 0
for insp in db.query(Inspection).all():
    imgs = [i.stored_filename for i in insp.images if i.stored_filename]
    if not imgs:
        continue
    rt = room_type_of(insp.salle)
    try:
        result = yolo_service.analyze_multiple_images(imgs, rt)
    except Exception as e:
        print(f"insp {insp.id}: ERREUR {e}")
        continue
    insp.resultat_analyse = json.dumps(result, ensure_ascii=False, default=str)
    insp.score_global = result["scoreGlobal"]
    insp.anomalies = result["nbAnomalies"]
    insp.statut = "TERMINEE"
    db.commit()
    n += 1
    print(f"insp {insp.id} ({rt}): score={result['scoreGlobal']} anomalies={result['nbAnomalies']}")

print(f"Backfill termine: {n} inspections mises a jour.")
