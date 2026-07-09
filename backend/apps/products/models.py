"""Product persistence. Prices live in a related table (multi-currency)."""

from __future__ import annotations

from django.db import models

from apps.companies.models import Company


class Product(models.Model):
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    characteristics = models.TextField(blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="products")
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["company_id", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "code"], name="unique_product_code_per_company"
            )
        ]

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


class ProductPrice(models.Model):
    """One price per currency for a product (the multi-currency requirement)."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="prices")
    currency = models.CharField(max_length=3)
    amount = models.DecimalField(max_digits=18, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["product", "currency"], name="unique_currency_per_product"
            )
        ]

    def __str__(self) -> str:
        return f"{self.amount} {self.currency}"
