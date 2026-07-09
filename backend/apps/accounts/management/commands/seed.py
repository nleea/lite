"""Seed the database with demo data.

Idempotent: running it repeatedly updates existing rows instead of duplicating.
Users come from the project README; companies/products are demo fixtures.

Usage:
    python manage.py seed
    python manage.py seed --flush   # wipe companies/products first
"""

from __future__ import annotations

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.companies.models import Company
from apps.products.models import Product, ProductPrice

User = get_user_model()

# (email, password, role, is_staff, is_superuser)
USERS = [
    ("admin@acme.com", "admin12345", "admin", True, True),
    ("externo@demo.com", "externo12345", "external", False, False),
]

# nit -> company fields
COMPANIES = [
    {
        "nit": "900123456-1",
        "name": "Acme Corp",
        "address": "Calle 100 #7-21, Bogota",
        "phone": "+57 601 555 0100",
    },
    {
        "nit": "800987654-2",
        "name": "Globex S.A.S.",
        "address": "Cra 43A #1-50, Medellin",
        "phone": "+57 604 555 0200",
    },
]

# (company_nit, code, name, characteristics, quantity, [(currency, amount), ...])
PRODUCTS = [
    (
        "900123456-1",
        "ACM-001",
        "Widget Pro",
        "High-durability industrial widget",
        150,
        [("COP", "89000.00"), ("USD", "22.50")],
    ),
    (
        "900123456-1",
        "ACM-002",
        "Widget Lite",
        "Lightweight consumer widget",
        320,
        [("COP", "45000.00"), ("USD", "11.25")],
    ),
    (
        "800987654-2",
        "GLX-100",
        "Gizmo X",
        "Next-gen smart gizmo",
        75,
        [("COP", "250000.00"), ("USD", "62.00"), ("EUR", "57.00")],
    ),
]


class Command(BaseCommand):
    help = "Seed the database with demo users, companies and products."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete existing companies/products before seeding.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["flush"]:
            ProductPrice.objects.all().delete()
            Product.objects.all().delete()
            Company.objects.all().delete()
            self.stdout.write(self.style.WARNING("Flushed companies and products."))

        self._seed_users()
        self._seed_companies()
        self._seed_products()
        self.stdout.write(self.style.SUCCESS("Seed complete."))

    def _seed_users(self):
        for email, password, role, is_staff, is_superuser in USERS:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={"role": role, "is_staff": is_staff, "is_superuser": is_superuser},
            )
            user.role = role
            user.is_staff = is_staff
            user.is_superuser = is_superuser
            user.is_active = True
            user.set_password(password)  # always (re)set so credentials are known
            user.save()
            verb = "Created" if created else "Updated"
            self.stdout.write(f"  {verb} user {email} ({role})")

    def _seed_companies(self):
        for data in COMPANIES:
            Company.objects.update_or_create(nit=data["nit"], defaults=data)
            self.stdout.write(f"  Company {data['name']} ({data['nit']})")

    def _seed_products(self):
        for company_nit, code, name, characteristics, quantity, prices in PRODUCTS:
            company = Company.objects.get(nit=company_nit)
            product, _ = Product.objects.update_or_create(
                company=company,
                code=code,
                defaults={
                    "name": name,
                    "characteristics": characteristics,
                    "quantity": quantity,
                },
            )
            for currency, amount in prices:
                ProductPrice.objects.update_or_create(
                    product=product,
                    currency=currency,
                    defaults={"amount": Decimal(amount)},
                )
            self.stdout.write(f"  Product {code} - {name} ({len(prices)} prices)")
