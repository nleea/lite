from rest_framework.test import APITestCase

from apps.accounts.models import User


class AuthTests(APITestCase):
    def test_login_returns_token_with_role_claim(self):
        User.objects.create_user(email="admin@acme.com", password="supersecret1", role="admin")
        resp = self.client.post(
            "/api/auth/login/",
            {"email": "admin@acme.com", "password": "supersecret1"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("access", resp.data)

    def test_password_is_hashed_with_argon2(self):
        user = User.objects.create_user(email="e@x.com", password="supersecret1")
        self.assertTrue(user.password.startswith("argon2"))
        self.assertNotEqual(user.password, "supersecret1")

    def test_register_creates_external_user(self):
        resp = self.client.post(
            "/api/auth/register/",
            {"email": "new@x.com", "password": "supersecret1"},
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(User.objects.get(email="new@x.com").role, "external")

    def test_login_rejects_bad_password(self):
        User.objects.create_user(email="a@x.com", password="supersecret1")
        resp = self.client.post(
            "/api/auth/login/",
            {"email": "a@x.com", "password": "wrong"},
            format="json",
        )
        self.assertEqual(resp.status_code, 401)
