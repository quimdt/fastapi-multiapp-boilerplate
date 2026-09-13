from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.apps.administrator.app import administrator_app
from src.apps.administrator.auth import create_access_token
from src.db.dependencies import get_db
from src.db.tables.users import UserSQLModel
from tests.base import BaseTestCase


class AuthenticatedTestClient(TestClient):
    """Custom TestClient that includes an authentication method."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.headers["Authorization"] = ""

    def authenticate(self, email: str, db: Session):
        """Authenticate a user and set the Authorization header."""

        user = db.query(UserSQLModel).filter(UserSQLModel.email == email).first()
        access_token = create_access_token(data={"sub": email, "scopes": ["me:read"]})
        self.headers["Authorization"] = f"Bearer {access_token}"

        return user


class AdminBaseTestCase(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = AuthenticatedTestClient(administrator_app)

    def setUp(self):
        super().setUp()

        def override_get_db():
            yield self.session

        administrator_app.dependency_overrides[get_db] = override_get_db

    def tearDown(self):
        super().tearDown()
        administrator_app.dependency_overrides.clear()
