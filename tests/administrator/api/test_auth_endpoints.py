from tests.administrator.admin_test_case import AdminBaseTestCase
from tests.administrator.fixtures import Fixture


class TestAuthEndpoints(AdminBaseTestCase):
    def test_login_success(self):
        Fixture.create_user(
            session=self.session,
            email="luke@jedi.com",
            password="MayThe4thBeWithYou",
        )

        response = self.client.post(
            "/api/v1/login",
            data={"username": "luke@jedi.com", "password": "MayThe4thBeWithYou"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json())
        self.assertEqual(response.json()["token_type"], "bearer")

    def test_login_wrong_password(self):
        Fixture.create_user(
            session=self.session,
            email="luke@jedi.com",
            password="MayThe4thBeWithYou",
        )

        response = self.client.post(
            "/api/v1/login",
            data={"username": "luke@jedi.com", "password": "wrong-password"},
        )

        self.assertEqual(response.status_code, 401)

    def test_login_unknown_user(self):
        response = self.client.post(
            "/api/v1/login",
            data={"username": "ghost@jedi.com", "password": "whatever"},
        )

        self.assertEqual(response.status_code, 401)

    def test_users_me_with_token(self):
        user = Fixture.create_user(
            session=self.session,
            email="leia@jedi.com",
            password="MayThe4thBeWithYou",
        )
        self.client.authenticate(email=user.email, db=self.session)

        response = self.client.get("/api/v1/users/me")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["email"], "leia@jedi.com")

    def test_users_me_without_token(self):
        response = self.client.get("/api/v1/users/me")

        self.assertEqual(response.status_code, 401)
