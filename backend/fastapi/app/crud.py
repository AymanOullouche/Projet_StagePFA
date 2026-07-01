from datetime import date
from typing import List, Optional
from uuid import uuid4
from pathlib import Path
import shutil

from sqlalchemy.orm import Session

from . import models, schemas
from .config import UPLOADS_DIR


def get_user_by_email(session: Session, email: str) -> Optional[models.User]:
    return session.query(models.User).filter(models.User.email == email).first()


def create_user(session: Session, email: str, role: str, nom: Optional[str] = None) -> models.User:
    name = nom or ("Admin Systeme" if role == "ADMIN" else "Inspecteur Principal")
    user = models.User(nom=name, email=email, role=role)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def create_session_token(session: Session, user: models.User) -> models.SessionToken:
    token = f"session-{uuid4().hex}"
    session_token = models.SessionToken(user_id=user.id, token=token)
    session.add(session_token)
    session.commit()
    session.refresh(session_token)
    return session_token


def get_session_by_token(session: Session, token: str) -> Optional[models.SessionToken]:
    return session.query(models.SessionToken).filter(models.SessionToken.token == token).first()


def delete_session(session: Session, token: str) -> bool:
    session_token = get_session_by_token(session, token)
    if not session_token:
        return False
    session.delete(session_token)
    session.commit()
    return True


def get_users(session: Session) -> List[models.User]:
    return session.query(models.User).order_by(models.User.id.asc()).all()


def get_etablissements(session: Session) -> List[models.Etablissement]:
    return session.query(models.Etablissement).order_by(models.Etablissement.id.desc()).all()


def get_etablissement(session: Session, etablissement_id: int) -> Optional[models.Etablissement]:
    return session.query(models.Etablissement).filter(models.Etablissement.id == etablissement_id).first()


def create_etablissement(session: Session, data: schemas.EtablissementCreate) -> models.Etablissement:
    etab = models.Etablissement(**data.model_dump())
    session.add(etab)
    session.commit()
    session.refresh(etab)
    return etab


def update_etablissement(session: Session, etablissement_id: int, data: schemas.EtablissementUpdate) -> Optional[models.Etablissement]:
    etab = get_etablissement(session, etablissement_id)
    if not etab:
        return None
    for key, value in data.model_dump().items():
        setattr(etab, key, value)
    session.commit()
    session.refresh(etab)
    return etab


def delete_etablissement(session: Session, etablissement_id: int) -> bool:
    etab = get_etablissement(session, etablissement_id)
    if not etab:
        return False
    session.delete(etab)
    session.commit()
    return True


def get_inspections(session: Session) -> List[models.Inspection]:
    return session.query(models.Inspection).order_by(models.Inspection.date_inspection.desc(), models.Inspection.id.desc()).all()


def get_inspection(session: Session, inspection_id: int) -> Optional[models.Inspection]:
    return session.query(models.Inspection).filter(models.Inspection.id == inspection_id).first()


def create_inspection(session: Session, data: schemas.InspectionCreate) -> models.Inspection:
    inspection = models.Inspection(**data.model_dump())
    session.add(inspection)
    session.commit()
    session.refresh(inspection)
    return inspection


def get_rapports(session: Session) -> List[models.Rapport]:
    return session.query(models.Rapport).order_by(models.Rapport.date_generation.desc(), models.Rapport.id.desc()).all()


def get_rapport(session: Session, rapport_id: int):
    return session.query(models.Rapport).filter(models.Rapport.id == rapport_id).first()


def create_rapport(session: Session, data: schemas.RapportCreate) -> models.Rapport:
    rapport = models.Rapport(**data.model_dump())
    session.add(rapport)
    session.commit()
    session.refresh(rapport)
    return rapport


def create_inspection_image(session: Session, inspection_id: int, filename: str, content_type: str, file_content: bytes) -> models.InspectionImage:
    """Crée une image d'inspection en la sauvegardant sur le disque."""
    file_id = uuid4().hex
    file_ext = Path(filename).suffix or ".jpg"
    stored_filename = f"{file_id}{file_ext}"
    
    # Sauvegarder le fichier sur le disque
    file_path = UPLOADS_DIR / stored_filename
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # Créer l'enregistrement en base de données
    image = models.InspectionImage(
        inspection_id=inspection_id, 
        filename=filename,
        stored_filename=stored_filename,
        content_type=content_type
    )
    session.add(image)
    session.commit()
    session.refresh(image)
    return image


def analyze_image(session: Session, image_id: int) -> Optional[models.InspectionImage]:
    image = session.query(models.InspectionImage).filter(models.InspectionImage.id == image_id).first()
    if not image:
        return None
    inspection = get_inspection(session, image.inspection_id)
    if not inspection:
        return None
    # Simulation simple d'analyse d'image. Le calcul peut être remplacé par un service YOLO.
    inspection.anomalies = max(inspection.anomalies, 2)
    inspection.score_global = min(100, inspection.score_global + 12)
    inspection.statut = "TERMINEE"
    session.commit()
    return image


def detect_equipments_from_image(session: Session, image_id: int) -> List[dict]:
    """Placeholder pour intégration YOLO : retourne une liste d'équipements détectés.
    À remplacer par l'appel au modèle YOLO sur l'image stockée.
    """
    # Simulation de détection
    return [
        {"id": 1, "nom": "Ordinateur", "quantite": 12, "confiance": 0.92},
        {"id": 2, "nom": "Extincteur", "quantite": 1, "confiance": 0.88},
    ]


def get_inspection_image(session: Session, image_id: int) -> Optional[models.InspectionImage]:
    """Récupère une image d'inspection par son ID."""
    return session.query(models.InspectionImage).filter(models.InspectionImage.id == image_id).first()


def get_inspection_images(session: Session, inspection_id: int) -> List[models.InspectionImage]:
    """Récupère toutes les images d'une inspection."""
    return session.query(models.InspectionImage).filter(models.InspectionImage.inspection_id == inspection_id).all()


def delete_inspection_image(session: Session, image_id: int) -> bool:
    """Supprime une image d'inspection (fichier et enregistrement BD)."""
    image = get_inspection_image(session, image_id)
    if not image:
        return False
    
    # Supprimer le fichier du disque
    if image.stored_filename:
        file_path = UPLOADS_DIR / image.stored_filename
        try:
            if file_path.exists():
                file_path.unlink()
        except Exception:
            pass  # Ignorer les erreurs de suppression de fichier
    
    # Supprimer l'enregistrement de la BD
    session.delete(image)
    session.commit()
    return True


def get_documents(session: Session) -> List[models.Document]:
    return session.query(models.Document).order_by(models.Document.date_import.desc()).all()


def initialize_documents(session: Session) -> None:
    if session.query(models.Document).count() > 0:
        return
    docs = [
        models.Document(
            titre="Normes salles informatiques",
            statut="Indexe",
            content="Les normes de securite et d equipement des salles informatiques exigent extincteurs, ventilation et postes de travail conforms.",
            date_import=date(2026, 6, 14),
        ),
        models.Document(
            titre="Guide securite infrastructures scolaires",
            statut="Indexe",
            content="Le guide precise les verifications a realiser dans les etablissements scolaires, notamment accessibilite, evacuation et materiel didactique.",
            date_import=date(2026, 6, 15),
        ),
    ]
    session.add_all(docs)
    session.commit()


def answer_rag_question(session: Session, question: str) -> tuple[str, List[models.Document]]:
    documents = get_documents(session)
    sources = documents[:2]
    answer = (
        f"Réponse simulée pour '{question}'. "
        "Les documents indexés fournissent des recommandations sur les normes et la sécurité."
    )
    return answer, sources
