"""Bootstrap the first administrator user on first execution.

Idempotent: exits without doing anything if the configured admin already exists.
Run standalone with:  python -m src.seed
"""

from sqlalchemy.orm import Session

from src.apps.administrator.auth import get_password_hash
from src.db.dependencies import SessionLocal
from src.db.tables.users import UserSQLModel
from src.settings import settings


def seed_admin_user(db: Session) -> UserSQLModel | None:
    existing = (
        db.query(UserSQLModel)
        .filter(UserSQLModel.email == settings.admin_email)
        .first()
    )
    if existing is not None:
        print(f"Admin user '{settings.admin_email}' already exists, skipping.")
        return None

    user = UserSQLModel(
        name=settings.admin_name,
        surname=settings.admin_surname,
        email=settings.admin_email,
        pwd=get_password_hash(settings.admin_password),
        active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"Admin user '{settings.admin_email}' created.")
    return user


def main() -> None:
    db = SessionLocal()
    try:
        seed_admin_user(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
