from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.companies.models import Company


class CompanyPermissionTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user("admin@x.com", "supersecret1", role="admin")
        self.external = User.objects.create_user("ext@x.com", "supersecret1", role="external")

    def test_admin_can_create_company(self):
        self.client.force_authenticate(self.admin)
        resp = self.client.post(
            "/api/companies/",
            {"nit": "900123456", "name": "Acme", "address": "5th Ave", "phone": "555"},
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(Company.objects.filter(nit="900123456").exists())

    def test_external_cannot_create_company(self):
        self.client.force_authenticate(self.external)
        resp = self.client.post(
            "/api/companies/",
            {"nit": "900123456", "name": "Acme", "address": "5th Ave", "phone": "555"},
            format="json",
        )
        self.assertEqual(resp.status_code, 403)

    def test_external_can_list_companies(self):
        Company.objects.create(nit="900", name="Acme", address="a", phone="1")
        self.client.force_authenticate(self.external)
        resp = self.client.get("/api/companies/")
        self.assertEqual(resp.status_code, 200)

    def test_invalid_nit_rejected_by_domain(self):
        self.client.force_authenticate(self.admin)
        resp = self.client.post(
            "/api/companies/",
            {"nit": "abc", "name": "Acme", "address": "5th Ave", "phone": "555"},
            format="json",
        )
        self.assertEqual(resp.status_code, 400)
