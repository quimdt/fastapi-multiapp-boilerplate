import uuid

from tests.administrator.admin_test_case import AdminBaseTestCase
from tests.administrator.fixtures import Fixture


class TestUsersEndpoints(AdminBaseTestCase):
    def setUp(self):
        super().setUp()
        self.admin = Fixture.create_user(
            session=self.session,
            email="admin@acme.com",
            password="admin-secret",
        )
        self.client.authenticate(email=self.admin.email, db=self.session)

    def test_create_user(self):
        response = self.client.post(
            "/api/v1/users",
            json={
                "name": "Leia",
                "surname": "Organa",
                "email": "leia@rebellion.com",
                "password": "trust-the-force",
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["email"], "leia@rebellion.com")
        self.assertTrue(response.json()["active"])

    def test_create_user_duplicate_email(self):
        Fixture.create_user(
            session=self.session, email="han@millennium.com", password="chewie"
        )

        response = self.client.post(
            "/api/v1/users",
            json={
                "name": "Han",
                "surname": "Solo",
                "email": "han@millennium.com",
                "password": "chewie",
            },
        )

        self.assertEqual(response.status_code, 400)

    def test_list_users(self):
        Fixture.create_user(
            session=self.session, email="han@millennium.com", password="chewie"
        )

        response = self.client.get("/api/v1/users")

        self.assertEqual(response.status_code, 200)
        emails = {user["email"] for user in response.json()}
        self.assertIn("han@millennium.com", emails)
        self.assertIn("admin@acme.com", emails)

    def test_get_user_by_id(self):
        target = Fixture.create_user(
            session=self.session, email="chewie@falcon.com", password="solo"
        )

        response = self.client.get(f"/api/v1/users/{target.id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], str(target.id))

    def test_get_user_not_found(self):
        response = self.client.get(f"/api/v1/users/{uuid.uuid4()}")

        self.assertEqual(response.status_code, 404)

    def test_update_user(self):
        target = Fixture.create_user(
            session=self.session, email="boba@fett.com", password="jango"
        )

        response = self.client.patch(
            f"/api/v1/users/{target.id}",
            json={"name": "Jango", "active": False},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "Jango")
        self.assertFalse(response.json()["active"])

    def test_me_endpoint(self):
        response = self.client.get("/api/v1/users/me")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["email"], "admin@acme.com")
