from sqlalchemy.orm import Session

from src.db.dao.base import BaseDAO


class DAOFactory:
    def __init__(self, db: Session):
        self.db = db

    def get_dao(self, dao_type: str = "default") -> BaseDAO:
        daos = {
            "default": lambda db: BaseDAO(db=db),
        }
        return daos[dao_type](self.db)
