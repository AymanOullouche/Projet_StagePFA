from datetime import date
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

class UserBase(BaseModel):
    email: EmailStr
    role: str = Field(default="INSPECTEUR")

class UserCreate(UserBase):
    nom: Optional[str] = None
    password: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRead(UserBase):
    id: int
    nom: str

    model_config = ConfigDict(from_attributes=True)

class EtablissementBase(BaseModel):
    nom: str
    type: str
    adresse: str
    ville: str
    region: str
    score: Optional[int] = 70

class EtablissementCreate(EtablissementBase):
    pass

class EtablissementUpdate(EtablissementBase):
    pass

class EtablissementRead(EtablissementBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class InspectionBase(BaseModel):
    etablissement_id: int
    salle: str
    statut: Optional[str] = "EN_COURS"
    date_inspection: date
    score_global: Optional[int] = 0
    anomalies: Optional[int] = 0

class InspectionCreate(InspectionBase):
    pass

class InspectionRead(BaseModel):
    id: int
    etablissement_id: int
    etablissement: str
    salle: str
    statut: str
    date_inspection: date
    score_global: int
    anomalies: int

    model_config = ConfigDict(from_attributes=True)

class RapportBase(BaseModel):
    inspection_id: Optional[int] = None
    titre: str
    etablissement: str
    date_generation: date
    statut: Optional[str] = "Brouillon"
    anomalies: Optional[int] = 0

class RapportCreate(RapportBase):
    pass

class RapportRead(RapportBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class UploadImageResponse(BaseModel):
    id: int
    inspection_id: int
    filename: str

class AnalyzeResponse(BaseModel):
    image_id: int
    inspection_id: int
    anomalies: int
    score_global: int
    status: str
    findings: List[str]

class DocumentRead(BaseModel):
    id: int
    titre: str
    statut: str
    date_import: date

    model_config = ConfigDict(from_attributes=True)

class RagQuestion(BaseModel):
    question: str

class RagAnswer(BaseModel):
    question: str
    answer: str
    source_documents: List[DocumentRead]
