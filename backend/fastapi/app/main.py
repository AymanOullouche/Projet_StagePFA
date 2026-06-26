from datetime import date
from typing import List, Optional

from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import Base, SessionLocal, engine
from .config import API_PREFIX

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


def get_current_session(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    token = parse_bearer_token(authorization)
    session_token = crud.get_session_by_token(db, token)
    if not session_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session invalide ou expirée")
    return session_token


def get_current_user(current_session = Depends(get_current_session)):
    return current_session.user


def require_admin(current_user = Depends(get_current_user)):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès admin requis")
    return current_user


@app.get(f"{API_PREFIX}/health")
def health() -> dict:
    return {"status": "ok"}


@app.post(f"{API_PREFIX}/auth/login")
def login(data: schemas.UserBase, db: Session = Depends(get_db)) -> dict:
    role = data.role.upper()
    if role not in {"ADMIN", "INSPECTEUR"}:
        raise HTTPException(status_code=422, detail="Role invalide")
    user = crud.get_user_by_email(db, data.email)
    if not user:
        user = crud.create_user(db, email=data.email, role=role)
    session_token = crud.create_session_token(db, user)
    return {
        "token": session_token.token,
        "type": "Bearer",
        "user": {
            "id": user.id,
            "nom": user.nom,
            "email": user.email,
            "role": user.role,
        },
    }


@app.post(f"{API_PREFIX}/auth/logout")
def logout(current_session = Depends(get_current_session), db: Session = Depends(get_db)) -> dict:
    crud.delete_session(db, current_session.token)
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


@app.get(f"{API_PREFIX}/users")
def list_users(db: Session = Depends(get_db), current_user = Depends(require_admin)) -> dict:
    users = crud.get_users(db)
    return {"data": [schemas.UserRead.model_validate(user).model_dump() for user in users]}


@app.post(f"{API_PREFIX}/users")
def create_user(data: schemas.UserCreate, db: Session = Depends(get_db), current_user = Depends(require_admin)) -> dict:
    existing_user = crud.get_user_by_email(db, data.email)
    if existing_user:
        raise HTTPException(status_code=409, detail="Utilisateur deja existe")
    user = crud.create_user(db, email=data.email, role=data.role.upper(), nom=data.nom)
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
def upload_inspection_image(inspection_id: int, image: UploadFile = File(...), db: Session = Depends(get_db), current_user = Depends(get_current_user)) -> dict:
    inspection = crud.get_inspection(db, inspection_id)
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection introuvable")
    uploaded = crud.create_inspection_image(db, inspection_id, image.filename, image.content_type)
    return {"data": {"id": uploaded.id, "inspectionId": uploaded.inspection_id, "filename": uploaded.filename}}


@app.post(f"{API_PREFIX}/images/{{image_id}}/analyze")
def analyze_image(image_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)) -> dict:
    image = crud.analyze_image(db, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image ou inspection introuvable")
    inspection = image.inspection
    return {
        "data": {
            "imageId": image.id,
            "inspectionId": image.inspection_id,
            "anomalies": inspection.anomalies,
            "scoreGlobal": inspection.score_global,
            "status": inspection.statut,
            "findings": ["Détection simulée d’anomalies", "Proposition de mise à niveau des équipements"],
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
