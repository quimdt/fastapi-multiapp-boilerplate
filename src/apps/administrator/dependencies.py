from fastapi import Depends
from sqlalchemy.orm import Session

from src.apps.administrator.dao.factory import DAOFactory
from src.db.dependencies import get_db


def get_dao(dao_type: str = "default"):
    def _get_dao(db: Session = Depends(get_db)) -> DAOFactory:
        dao_factory = DAOFactory(db)
        return dao_factory.get_dao(dao_type)

    return _get_dao
