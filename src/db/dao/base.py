import logging
import uuid

from sqlalchemy import Table
from sqlalchemy.exc import (
    DataError,
    IntegrityError,
    InvalidRequestError,
    NoResultFound,
    OperationalError,
    ProgrammingError,
    StatementError,
)
from sqlalchemy.orm import Session

from src.db.exceptions import DBError, NotFound

logger = logging.getLogger(__name__)


class BaseDAO:
    def __init__(self, db: Session):
        self.db = db

    def get_value_by_id(self, table: Table, id: uuid.UUID):
        try:
            value = self.db.query(table).get(id)
        except NoResultFound:
            raise NotFound()
        if value is None:
            raise NotFound()
        return value

    def get_value_by_filter(self, table: Table, **filter):
        try:
            value = self.db.query(table).filter_by(**filter).one()
        except NoResultFound:
            raise NotFound()
        return value

    def get_values_by_filter(self, table: Table, **filter):
        try:
            return self.db.query(table).filter_by(**filter).all()
        except NoResultFound:
            raise NotFound()

    def create_row(self, table: Table, values: dict, commit=True):
        try:
            table_name = table.__tablename__
            row = table(**values)
            self.db.add(row)
            if commit:
                self.db.commit()
                self.db.refresh(row)
            else:
                self.db.flush()
            return row
        except IntegrityError:
            self.db.rollback()
            logger.error(f"error:db:create_{table_name}_row_constraint", exc_info=True)
            raise DBError()
        except OperationalError:
            self.db.rollback()
            logger.error(f"error:db:create_{table_name}_connection", exc_info=True)
            raise DBError()
        except DataError:
            self.db.rollback()
            logger.error(f"error:db:create_{table_name}_invalid_data", exc_info=True)
            raise DBError()
        except InvalidRequestError:
            self.db.rollback()
            logger.error(f"error:db:create_{table_name}_invalid_request", exc_info=True)
            raise DBError()
        except StatementError:
            self.db.rollback()
            logger.error(
                f"error:db:create_{table_name}_invalid_statement", exc_info=True
            )
            raise DBError()
        except ProgrammingError:
            self.db.rollback()
            logger.error(f"error:db:create_{table_name}_invalid_query", exc_info=True)
            raise DBError()

    def get_or_create_row(self, table: Table, values: dict, commit=True, **kwargs):
        instance = self.db.query(table).filter_by(**kwargs).one_or_none()
        if instance:
            return instance, False
        else:
            kwargs |= values or {}
            instance = table(**kwargs)
            try:
                self.db.add(instance)
                if commit:
                    self.db.commit()
            except Exception:
                self.db.rollback()
                instance = self.db.query(table).filter_by(**kwargs).one()
                return instance, False
            else:
                return instance, True

    def create_rows(self, table: Table, values: list, commit=True):
        """Create all rows to any Table passed as argument with list values."""
        try:
            table_name = table.__tablename__
            rows = [table(**value) for value in values]
            self.db.add_all(rows)
            if commit:
                self.db.commit()
                for row in rows:
                    self.db.refresh(row)
        except IntegrityError:
            if commit:
                self.db.rollback()
            logger.error(f"error:db:create_{table_name}_row_constraint")
            raise DBError()
        except OperationalError:
            if commit:
                self.db.rollback()
            logger.error(f"error:db:create_{table_name}_connection", exc_info=True)
            raise DBError()
        except DataError:
            if commit:
                self.db.rollback()
            logger.error(f"error:db:create_{table_name}_invalid_data", exc_info=True)
            raise DBError()
        except InvalidRequestError:
            if commit:
                self.db.rollback()
            logger.error(f"error:db:create_{table_name}_invalid_request", exc_info=True)
            raise DBError()
        except StatementError:
            if commit:
                self.db.rollback()
            logger.error(
                f"error:db:create_{table_name}_invalid_statement", exc_info=True
            )
            raise DBError()
        except ProgrammingError:
            self.db.rollback()
            logger.error(f"error:db:create_{table_name}_invalid_query", exc_info=True)
            raise DBError()

        return rows

    def update_row(self, table: Table, values: dict, commit=True, **filter):
        try:
            table_name = table.__tablename__
            row = self.db.query(table).filter_by(**filter).update(values)
            if commit:
                self.db.commit()
                self.db.flush()
            return row
        except IntegrityError:
            self.db.rollback()
            logger.error(f"error:db:update_{table_name}_row_constraint", exc_info=True)
            raise DBError()
        except OperationalError:
            self.db.rollback()
            logger.error(f"error:db:update_{table_name}_connection", exc_info=True)
            raise DBError()
        except DataError:
            self.db.rollback()
            logger.error(f"error:db:update_{table_name}_invalid_data", exc_info=True)
            raise DBError()
        except InvalidRequestError:
            self.db.rollback()
            logger.error(f"error:db:update_{table_name}_invalid_request", exc_info=True)
            raise DBError()
        except StatementError:
            self.db.rollback()
            logger.error(
                f"error:db:update_{table_name}_invalid_statement", exc_info=True
            )
            raise DBError()
        except ProgrammingError:
            self.db.rollback()
            logger.error(f"error:db:update_{table_name}_invalid_query", exc_info=True)
            raise DBError()
