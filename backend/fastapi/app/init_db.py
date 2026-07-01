from sqlalchemy.orm import Session

from .database import SessionLocal
from . import models
from .auth import get_password_hash


def init_db() -> None:
    db = SessionLocal()
    try:
        # Créer un admin par défaut si aucun utilisateur n'existe
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
            print("Admin cree: admin@inspection.ma / admin123")

        # Créer un inspecteur par défaut si aucun utilisateur n'existe
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
            print("Inspecteur cree: inspecteur@inspection.ma / inspection2025")

        # Migrer les anciens utilisateurs sans mot de passe
        users_without_password = db.query(models.User).filter(models.User.hashed_password == None).all()
        for user in users_without_password:
            if user.role == "ADMIN":
                user.hashed_password = get_password_hash("admin123")
            else:
                user.hashed_password = get_password_hash("inspection2025")
            db.commit()
            print(f"Utilisateur migre: {user.email}")

    finally:
        db.close()


if __name__ == "__main__":
    init_db()