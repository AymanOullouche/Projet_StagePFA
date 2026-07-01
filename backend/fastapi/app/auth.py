from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from . import models, schemas
from .config import API_PREFIX

# Configuration JWT
SECRET_KEY = "CHANGE_ME_IN_PRODUCTION_USE_ENV_VAR"  # À mettre dans .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 heures

# Configuration pour le hachage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie un mot de passe en clair contre un hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Génère un hash bcrypt pour un mot de passe."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crée un token JWT avec expiration."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Décode et valide un token JWT."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
    """Authentifie un utilisateur avec email et mot de passe."""
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        return None
    if not user.hashed_password:
        # Compatibilité avec les anciens utilisateurs sans mot de passe
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_user_with_password(db: Session, email: str, password: str, role: str, nom: Optional[str] = None) -> models.User:
    """Crée un utilisateur avec un mot de passe hashé."""
    name = nom or ("Admin Systeme" if role == "ADMIN" else "Inspecteur Principal")
    hashed_password = get_password_hash(password)
    user = models.User(nom=name, email=email, role=role, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user_password(db: Session, user: models.User, new_password: str) -> models.User:
    """Met à jour le mot de passe d'un utilisateur."""
    user.hashed_password = get_password_hash(new_password)
    db.commit()
    db.refresh(user)
    return user