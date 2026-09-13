from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.tables.base import BaseSQLModel


class UserSQLModel(BaseSQLModel):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    surname: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    pwd: Mapped[str] = mapped_column(String(255), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
