from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.companies.models import Company
from apps.products.models import Product


class ProductTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user("admin@x.com", "supersecret1", role="admin")
        self.external = User.objects.create_user("ext@x.com", "supersecret1", role="external")
        self.company = Company.objects.create(nit="900123456", name="Acme", address="a", phone="1")

    def _payload(self):
        return {
            "code": "P-1",
            "name": "Widget",
            "characteristics": "outdoor, waterproof",
            "company": "900123456",
            "quantity": 5,
            "prices": [
                {"currency": "USD", "amount": "100.00"},
                {"currency": "COP", "amount": "400000.00"},
            ],
        }

    def test_admin_creates_product_with_multi_currency(self):
        self.client.force_authenticate(self.admin)
        resp = self.client.post("/api/products/", self._payload(), format="json")
        self.assertEqual(resp.status_code, 201)
        product = Product.objects.get(code="P-1")
        self.assertEqual(product.prices.count(), 2)

    def test_external_cannot_create_product(self):
        self.client.force_authenticate(self.external)
        resp = self.client.post("/api/products/", self._payload(), format="json")
        self.assertEqual(resp.status_code, 403)

    def test_inventory_groups_by_company(self):
        self.client.force_authenticate(self.admin)
        self.client.post("/api/products/", self._payload(), format="json")
        resp = self.client.get("/api/products/inventory/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data[0]["nit"], "900123456")
        self.assertEqual(len(resp.data[0]["products"]), 1)
