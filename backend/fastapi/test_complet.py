"""Test complet: Auth + Etab + Inspection + Upload + YOLO"""
import requests, json, sys, io, os, traceback
from PIL import Image, ImageDraw

BASE = "http://localhost:8000/api"

def log(msg):
    print(msg)
    sys.stdout.flush()

log("=" * 60)
log("  TEST PLATEFORME INSPECTION SCOLAIRE")
log("=" * 60)

try:
    r = requests.get(f"{BASE}/health", timeout=5)
    log(f"1. Health: {r.json()}")

    r = requests.post(f"{BASE}/init", timeout=5)
    log(f"2. Init DB: {r.status_code}")

    r = requests.post(f"{BASE}/auth/login",
        json={"email": "admin@inspection.ma", "password": "admin123"}, timeout=5)
    log(f"3. Login: {r.status_code}")

    if r.status_code != 200:
        log(f"   ERREUR: {r.text[:300]}")
        sys.exit(1)

    body = r.json()
    data = body.get("data", body)
    token = data.get("access_token") or data.get("token")
    if not token:
        log(f"   STRUCTURE: {list(data.keys())}")
        sys.exit(1)
    headers = {"Authorization": f"Bearer {token}"}
    log(f"   Token: {token[:40]}...")

    r = requests.get(f"{BASE}/etablissements", headers=headers, timeout=5)
    j = r.json()
    etabs = j.get("data", j.get("etablissements", []))
    log(f"4. Etablissements: {len(etabs) if isinstance(etabs,list) else j}")

    if not etabs:
        r = requests.post(f"{BASE}/etablissements", headers=headers,
            json={"nom": "Lycee Test YOLO", "type": "Lycee",
                  "adresse": "123 Rue", "ville": "Rabat",
                  "region": "Rabat-Sale-Kenitra", "score": 70}, timeout=5)
        etab = r.json().get("data", r.json())
        etab_id = etab["id"]
        log(f"   Cree: #{etab_id}")
    else:
        etab_id = etabs[0]["id"]
        log(f"   Utilise: #{etab_id} {etabs[0].get('nom','')}")

    r = requests.post(f"{BASE}/inspections", headers=headers,
        json={"etablissement_id": etab_id, "salle": "Salle informatique",
              "date_inspection": "2026-07-01", "statut": "EN_COURS",
              "score_global": 0, "anomalies": 0}, timeout=5)
    insp = r.json().get("data", r.json())
    insp_id = insp["id"]
    log(f"5. Inspection: #{insp_id} salle={insp.get('salle','?')}")

    img = Image.new("RGB", (640, 480), (200, 200, 200))
    draw = ImageDraw.Draw(img)
    draw.rectangle([50, 50, 200, 180], fill=(100, 150, 200), outline="black")
    draw.rectangle([250, 80, 380, 200], fill=(80, 120, 180), outline="black")
    draw.rectangle([420, 60, 550, 190], fill=(90, 140, 210), outline="black")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)

    r = requests.post(f"{BASE}/inspections/{insp_id}/images",
        headers=headers, files={"image": ("salle.jpg", buf, "image/jpeg")}, timeout=30)
    img_data = r.json().get("data", r.json())
    image_id = img_data["id"]
    log(f"6. Upload: #{image_id}")

    log("7. Analyse YOLO...")
    r = requests.post(f"{BASE}/images/{image_id}/analyze",
        headers=headers, timeout=30)
    if r.status_code != 200:
        log(f"   ERREUR: {r.status_code} {r.text[:300]}")
        sys.exit(1)

    result = r.json().get("data", r.json())
    log(f"   Status: {result.get('status','?')}")
    log(f"   Score: {result.get('scoreGlobal','?')}/100")
    log(f"   Room: {result.get('roomType','?')}")
    log(f"   Equipements: {len(result.get('equipments',[]))}")
    for eq in result.get("equipments", []):
        log(f"     - {eq['nom']}: {eq['quantite']}x conf={eq.get('confiance',0):.1%}")
    log(f"   Anomalies: {result.get('nbAnomalies',0)}")
    for a in result.get("anomalies", []):
        log(f"     - {a.get('equipement','?')}: {a.get('detecte',0)}/{a.get('requis',0)} gravite={a.get('gravite','?')}")
    log("   Findings:")
    for f in result.get("findings", []):
        log(f"     - {f}")

    r = requests.get(f"{BASE}/inspections", headers=headers, timeout=5)
    inspections = r.json().get("data", [])
    updated = next((i for i in inspections if i["id"] == insp_id), None)
    if updated:
        log(f"8. Inspection maj: score={updated.get('score_global','?')} anomalie={updated.get('anomalies','?')} statut={updated.get('statut','?')}")

    log("=" * 60)
    log("  TOUS LES TESTS REUSSIS !")
    log(f"  Inspection #{insp_id} - Score YOLO: {result.get('scoreGlobal','?')}/100")
    log("=" * 60)

except Exception as e:
    log(f"ERREUR: {e}")
    traceback.print_exc()
    sys.exit(1)
