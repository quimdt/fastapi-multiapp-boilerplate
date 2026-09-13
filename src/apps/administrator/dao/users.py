import uuid

from src.db.dao.base import BaseDAO
from src.db.tables.users import UserSQLModel


class UsersDAO(BaseDAO):
    def get_all_users(self) -> list[UserSQLModel]:
        return self.db.query(UserSQLModel).all()

    def get_user_by_id(self, user_id: uuid.UUID) -> UserSQLModel:
        return self.get_value_by_id(UserSQLModel, user_id)

    def get_user_by_email(self, email: str) -> UserSQLModel:
        return self.get_value_by_filter(UserSQLModel, email=email)

    def create_user(self, values: dict) -> UserSQLModel:
        return self.create_row(UserSQLModel, values)

    def update_user(self, values: dict, **filters) -> int:
        return self.update_row(UserSQLModel, values, **filters)
