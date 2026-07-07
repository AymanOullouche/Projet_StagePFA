from datetime import date
from pathlib import Path
from typing import List, Optional

from fastapi import Depends, FastAPI, File, Header, HTTPException, Response, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import Base, SessionLocal, engine
from .config import API_PREFIX, UPLOADS_DIR
from .auth import (
    authenticate_user,
    create_access_token,
    create_user_with_password,
    decode_access_token,
    get_password_hash,
    update_user_password,
    verify_password,
)
from .yolo_service import yolo_service

app = FastAPI(title="Inspection Scolaire API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        crud.initialize_documents(db)
    finally:
        db.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def parse_bearer_token(authorization: Optional[str]) -> str:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header missing")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header")
    return parts[1]


def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    token = parse_bearer_token(authorization)
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalide ou expiré")
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalide")
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Utilisateur introuvable")
    return user


def require_admin(current_user = Depends(get_current_user)):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès admin requis")
    return current_user


@app.get(f"{API_PREFIX}/health")
def health() -> dict:
    return {"status": "ok"}


@app.post(f"{API_PREFIX}/init")
def init_system(db: Session = Depends(get_db)) -> dict:
    """Initialise la base de données avec les utilisateurs par défaut."""
    from .auth import get_password_hash
    from . import models

    results = []

    # Créer l'admin par défaut
    admin = db.query(models.User).filter(models.User.email == "admin@inspection.ma").first()
    if not admin:
        admin = models.User(
            nom="Admin Systeme",
            email="admin@inspection.ma",
            role="ADMIN",
            hashed_password=get_password_hash("admin123"),
        )
        db.add(admin)
        db.commit()
        results.append("Admin cree: admin@inspection.ma / admin123")

    # Créer l'inspecteur par défaut
    inspector = db.query(models.User).filter(models.User.email == "inspecteur@inspection.ma").first()
    if not inspector:
        inspector = models.User(
            nom="Inspecteur Principal",
            email="inspecteur@inspection.ma",
            role="INSPECTEUR",
            hashed_password=get_password_hash("inspection2025"),
        )
        db.add(inspector)
        db.commit()
        results.append("Inspecteur cree: inspecteur@inspection.ma / inspection2025")

    # Migrer les anciens utilisateurs sans mot de passe
    users_without_password = db.query(models.User).filter(models.User.hashed_password == None).all()
    for user in users_without_password:
        if user.role == "ADMIN":
            user.hashed_password = get_password_hash("admin123")
        else:
            user.hashed_password = get_password_hash("inspection2025")
        db.commit()
        results.append(f"Utilisateur migre: {user.email}")

    return {"status": "initialized", "details": results}


@app.post(f"{API_PREFIX}/auth/login")
def login(data: schemas.UserLogin, db: Session = Depends(get_db)) -> dict:
    user = authenticate_user(db, email=data.email, password=data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email ou mot de passe incorrect")
    access_token = create_access_token(data={"sub": user.email, "role": user.role, "user_id": user.id})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "nom": user.nom,
            "email": user.email,
            "role": user.role,
        },
    }


@app.post(f"{API_PREFIX}/auth/logout")
def logout(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)) -> dict:
    if authorization:
        token = parse_bearer_token(authorization)
        crud.delete_session(db, token)
    return {"status": "logged_out"}


@app.get(f"{API_PREFIX}/auth/me")
def who_am_i(current_user = Depends(get_current_user)) -> dict:
    return {
        "data": {
            "id": current_user.id,
            "nom": current_user.nom,
            "email": current_user.email,
            "role": current_user.role,
        }
    }


@app.post(f"{API_PREFIX}/auth/register")
def register(data: schemas.UserCreate, db: Session = Depends(get_db)) -> dict:
    existing_user = crud.get_user_by_email(db, data.email)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Utilisateur deja existe")
    if not data.password:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Mot de passe requis")
    role = data.role.upper() if data.role else "INSPECTEUR"
    if role not in {"ADMIN", "INSPECTEUR"}:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Role invalide")
    user = create_user_with_password(db, email=data.email, password=data.password, role=role, nom=data.nom)
    return {"data": schemas.UserRead.model_validate(user).model_dump()}


@app.post(f"{API_PREFIX}/auth/change-password")
def change_password(data: schemas.UserLogin, current_user = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    if not verify_password(data.password, current_user.hashed_password or ""):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Mot de passe actuel incorrect")
    current_user = update_user_password(db, current_user, data.password)
    return {"status": "password_updated"}


@app.get(f"{API_PREFIX}/users")
def list_users(db: Session = Depends(get_db), current_user = Depends(require_admin)) -> dict:
    users = crud.get_users(db)
    return {"data": [schemas.UserRead.model_validate(user).model_dump() for user in users]}


@app.post(f"{API_PREFIX}/users")
def create_user(data: schemas.UserCreate, db: Session = Depends(get_db), current_user = Depends(require_admin)) -> dict:
    existing_user = crud.get_user_by_email(db, data.email)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Utilisateur deja existe")
    if not data.password:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Mot de passe requis")
    role = data.role.upper() if data.role else "INSPECTEUR"
    if role not in {"ADMIN", "INSPECTEUR"}:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Role invalide")
    user = create_user_with_password(db, email=data.email, password=data.password, role=role, nom=data.nom)
    return {"data": schemas.UserRead.model_validate(user).model_dump()}


@app.get(f"{API_PREFIX}/etablissements")
def list_etablissements(db: Session = Depends(get_db), current_user = Depends(get_current_user)) -> dict:
    etablissements = crud.get_etablissements(db)
    return {"data": [schemas.EtablissementRead.model_validate(etab).model_dump() for etab in etablissements]}


@app.post(f"{API_PREFIX}/etablissements")
def create_etablissement(data: schemas.EtablissementCreate, db: Session = Depends(get_db), current_user = Depends(require_admin)) -> dict:
    etab = crud.create_etablissement(db, data)
    return {"data": schemas.EtablissementRead.model_validate(etab).model_dump()}


@app.put(f"{API_PREFIX}/etablissements/{{etablissement_id}}")
def update_etablissement(etablissement_id: int, data: schemas.EtablissementUpdate, db: Session = Depends(get_db), current_user = Depends(require_admin)) -> dict:
    etab = crud.update_etablissement(db, etablissement_id, data)
    if not etab:
        raise HTTPException(status_code=404, detail="Etablissement introuvable")
    return {"data": schemas.EtablissementRead.model_validate(etab).model_dump()}


@app.delete(f"{API_PREFIX}/etablissements/{{etablissement_id}}")
def remove_etablissement(etablissement_id: int, db: Session = Depends(get_db), current_user = Depends(require_admin)) -> dict:
    deleted = crud.delete_etablissement(db, etablissement_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Etablissement introuvable")
    return {"deleted": True}


@app.get(f"{API_PREFIX}/inspections")
def list_inspections(db: Session = Depends(get_db), current_user = Depends(get_current_user)) -> dict:
    inspections = crud.get_inspections(db)
    data = []
    for inspection in inspections:
        data.append(
            {
                "id": inspection.id,
                "etablissementId": inspection.etablissement_id,
                "etablissement": inspection.etablissement.nom if inspection.etablissement else "",
                "salle": inspection.salle,
                "statut": inspection.statut,
                "dateInspection": inspection.date_inspection.isoformat(),
                "scoreGlobal": inspection.score_global,
                "anomalies": inspection.anomalies,
            }
        )
    return {"data": data}


@app.post(f"{API_PREFIX}/inspections")
def create_inspection(data: schemas.InspectionCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)) -> dict:
    inspection = crud.create_inspection(db, data)
    etab = inspection.etablissement
    return {
        "data": {
            "id": inspection.id,
            "etablissementId": inspection.etablissement_id,
            "etablissement": etab.nom if etab else "",
            "salle": inspection.salle,
            "statut": inspection.statut,
            "dateInspection": inspection.date_inspection.isoformat(),
            "scoreGlobal": inspection.score_global,
            "anomalies": inspection.anomalies,
        }
    }


@app.post(f"{API_PREFIX}/inspections/{{inspection_id}}/images")
async def upload_inspection_image(inspection_id: int, image: UploadFile = File(...), db: Session = Depends(get_db), current_user = Depends(get_current_user)) -> dict:
    inspection = crud.get_inspection(db, inspection_id)
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection introuvable")
    file_content = await image.read()
    uploaded = crud.create_inspection_image(db, inspection_id, image.filename, image.content_type or "image/jpeg", file_content)
    return {"data": {"id": uploaded.id, "inspectionId": uploaded.inspection_id, "filename": uploaded.filename, "stored_filename": uploaded.stored_filename}}


@app.get(f"{API_PREFIX}/images/{{image_id}}")
def serve_image(image_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    image = crud.get_inspection_image(db, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image introuvable")
    file_path = UPLOADS_DIR / image.stored_filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Fichier image introuvable sur le disque")
    return FileResponse(path=str(file_path), media_type=image.content_type, filename=image.filename)


@app.post(f"{API_PREFIX}/images/{{image_id}}/analyze")
def analyze_image(image_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)) -> dict:
    """Analyse une image avec YOLO et met a jour l'inspection."""
    image = crud.get_inspection_image(db, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image introuvable")
    if not image.stored_filename:
        raise HTTPException(status_code=400, detail="Image non stockee sur le disque")

    inspection = image.inspection
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection introuvable")

    salle = (inspection.salle or "").strip()
    if any(k in salle for k in ["informatique", "info"]):
        room_type = "Salle informatique"
    elif "laboratoire" in salle.lower():
        room_type = "Laboratoire"
    else:
        room_type = "Salle standard"

    try:
        result = yolo_service.analyze_image(image.stored_filename, room_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur YOLO : {str(e)}")

    inspection.score_global = result["scoreGlobal"]
    inspection.anomalies = result["nbAnomalies"]
    inspection.statut = "TERMINEE"
    db.commit()
    db.refresh(inspection)

    return {
        "data": {
            "imageId": image.id,
            "inspectionId": image.inspection_id,
            "filename": image.filename,
            "roomType": room_type,
            "equipments": result["equipments"],
            "norms": result["norms"],
            "anomalies": result["anomalies"],
            "nbAnomalies": result["nbAnomalies"],
            "scoreGlobal": result["scoreGlobal"],
            "status": result["status"],
            "findings": result["findings"],
            "recommendations": result.get("recommendations", []),
        }
    }


@app.post(f"{API_PREFIX}/inspections/{{inspection_id}}/analyze-all")
def analyze_all_images(inspection_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)) -> dict:
    """Analyse TOUTES les images d'une inspection et FUSIONNE les resultats."""
    inspection = crud.get_inspection(db, inspection_id)
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection introuvable")
    images = crud.get_inspection_images(db, inspection_id)
    if not images:
        raise HTTPException(status_code=400, detail="Aucune image trouvee")
    salle = (inspection.salle or "").strip()
    if any(k in salle for k in ["informatique", "info"]):
        room_type = "Salle informatique"
    elif "laboratoire" in salle.lower():
        room_type = "Laboratoire"
    else:
        room_type = "Salle standard"
    filenames = [img.stored_filename for img in images if img.stored_filename]
    if not filenames:
        raise HTTPException(status_code=400, detail="Aucune image stockee")
    try:
        result = yolo_service.analyze_multiple_images(filenames, room_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur YOLO fusion: {str(e)}")
    inspection.score_global = result["scoreGlobal"]
    inspection.anomalies = result["nbAnomalies"]
    inspection.statut = "TERMINEE"
    db.commit()
    db.refresh(inspection)
    return {
        "data": {
            "inspectionId": inspection.id,
            "imagesAnalyzed": len(filenames),
            "roomType": room_type,
            "equipments": result["equipments"],
            "norms": result["norms"],
            "norm_details": result["norm_details"],
            "anomalies": result["anomalies"],
            "nbAnomalies": result["nbAnomalies"],
            "scoreGlobal": result["scoreGlobal"],
            "status": result["status"],
            "findings": result["findings"],
            "recommendations": result.get("recommendations", []),
        }
    }


@app.get(f"{API_PREFIX}/rapports")
def list_rapports(db: Session = Depends(get_db), current_user = Depends(get_current_user)) -> dict:
    rapports = crud.get_rapports(db)
    return {"data": [schemas.RapportRead.model_validate(rapport).model_dump() for rapport in rapports]}


@app.post(f"{API_PREFIX}/rapports")
def create_rapport(data: schemas.RapportCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)) -> dict:
    rapport = crud.create_rapport(db, data)
    return {"data": schemas.RapportRead.model_validate(rapport).model_dump()}


@app.get(f"{API_PREFIX}/rapports/{{rapport_id}}")
def get_rapport_detail(rapport_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)) -> dict:
    rapport = crud.get_rapport(db, rapport_id)
    if not rapport:
        raise HTTPException(status_code=404, detail="Rapport introuvable")
    return {"data": schemas.RapportRead.model_validate(rapport).model_dump()}


@app.get(f"{API_PREFIX}/rapports/{{rapport_id}}/pdf")
def get_rapport_pdf(rapport_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)) -> Response:
    rapport = crud.get_rapport(db, rapport_id)
    if not rapport:
        raise HTTPException(status_code=404, detail="Rapport introuvable")

    inspection = None
    if rapport.inspection_id:
        inspection = crud.get_inspection(db, rapport.inspection_id)

    pdf_bytes = generate_report_pdf(rapport, inspection)
    filename = f"rapport_{rapport.id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.get(f"{API_PREFIX}/rag/documents")
def list_rag_documents(db: Session = Depends(get_db), current_user = Depends(get_current_user)) -> dict:
    documents = crud.get_documents(db)
    return {"data": [schemas.DocumentRead.model_validate(doc).model_dump() for doc in documents]}


@app.post(f"{API_PREFIX}/rag/questions")
def rag_question(data: schemas.RagQuestion, db: Session = Depends(get_db), current_user = Depends(get_current_user)) -> dict:
    answer, sources = crud.answer_rag_question(db, data.question)
    return {
        "data": {
            "question": data.question,
            "answer": answer,
            "source_documents": [schemas.DocumentRead.model_validate(doc).model_dump() for doc in sources],
        }
    }
