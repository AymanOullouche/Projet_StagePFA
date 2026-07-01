from datetime import date, datetime
from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(120), nullable=False)
    email = Column(String(160), unique=True, index=True, nullable=False)
    role = Column(String(20), nullable=False, default="INSPECTEUR")
    hashed_password = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    sessions = relationship("SessionToken", back_populates="user", cascade="all, delete")


class SessionToken(Base):
    __tablename__ = "session_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(120), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="sessions")


class Etablissement(Base):
    __tablename__ = "etablissements"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(160), nullable=False)
    type = Column(String(50), nullable=False)
    adresse = Column(String(255), nullable=False)
    ville = Column(String(100), nullable=False)
    region = Column(String(140), nullable=False)
    score = Column(Integer, nullable=False, default=70)
    created_at = Column(DateTime, default=datetime.utcnow)
    inspections = relationship("Inspection", back_populates="etablissement", cascade="all, delete")

class Inspection(Base):
    __tablename__ = "inspections"

    id = Column(Integer, primary_key=True, index=True)
    etablissement_id = Column(Integer, ForeignKey("etablissements.id", ondelete="CASCADE"), nullable=False)
    salle = Column(String(120), nullable=False)
    statut = Column(String(20), nullable=False, default="EN_COURS")
    date_inspection = Column(Date, nullable=False)
    score_global = Column(Integer, nullable=False, default=0)
    anomalies = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    etablissement = relationship("Etablissement", back_populates="inspections")
    images = relationship("InspectionImage", back_populates="inspection", cascade="all, delete")

class Rapport(Base):
    __tablename__ = "rapports"

    id = Column(Integer, primary_key=True, index=True)
    inspection_id = Column(Integer, ForeignKey("inspections.id", ondelete="SET NULL"), nullable=True)
    titre = Column(String(180), nullable=False)
    etablissement = Column(String(160), nullable=False)
    date_generation = Column(Date, nullable=False)
    statut = Column(String(20), nullable=False, default="Brouillon")
    anomalies = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class InspectionImage(Base):
    __tablename__ = "inspection_images"

    id = Column(Integer, primary_key=True, index=True)
    inspection_id = Column(Integer, ForeignKey("inspections.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=True)  # Nom du fichier stocké sur disque
    content_type = Column(String(90), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    inspection = relationship("Inspection", back_populates="images")

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String(180), nullable=False)
    statut = Column(String(80), nullable=False, default="Indexe")
    content = Column(Text, nullable=False)
    date_import = Column(Date, nullable=False)
