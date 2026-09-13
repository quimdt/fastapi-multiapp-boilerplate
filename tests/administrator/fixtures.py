from src.apps.administrator.auth import get_password_hash
from src.db.tables.users import UserSQLModel


class Fixture:
    """Reusable fixtures for setting up test data."""

    @staticmethod
    def create_user(session, **kwargs):
        defaults = {
            "name": "Luke",
            "surname": "Skywalker",
            "email": "luke.skywalker@jedi.com",
            "active": True,
        }
        defaults.update(kwargs)

        password = defaults.pop("password", None) or defaults.pop(
            "pwd", "MayThe4thBeWithYou"
        )
        defaults["pwd"] = get_password_hash(password=password)

        user = UserSQLModel(**defaults)
        session.add(user)
        session.commit()
        session.refresh(user)
        user.password = password

        return user
