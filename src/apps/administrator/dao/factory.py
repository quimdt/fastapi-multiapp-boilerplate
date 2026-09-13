
from sqlalchemy.orm import Session

from src.apps.administrator.dao.users import UsersDAO
from src.db.dao.base import BaseDAO


class DAOFactory:
    def __init__(self, db: Session):
        self.db = db

    def get_dao(self, dao_type: str) -> BaseDAO:
        daos = {
            "default": lambda db: BaseDAO(db=db),
            "users": lambda db: UsersDAO(db=db),
        }
        return daos[dao_type](self.db)
