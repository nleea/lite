"""Product model <-> domain entity translation."""

from __future__ import annotations

from domain.entities import Product as DomainProduct
from domain.value_objects import Money

from apps.products.models import Product


def to_domain(product: Product) -> DomainProduct:
    prices = [Money(price.amount, price.currency) for price in product.prices.all()]
    return DomainProduct.create(
        code=product.code,
        name=product.name,
        characteristics=product.characteristics,
        company_nit=product.company_id,
        prices=prices,
    )


def validate_with_domain(
    code: str, name: str, characteristics: str, company_nit: str, prices: list[Money]
) -> DomainProduct:
    return DomainProduct.create(
        code=code,
        name=name,
        characteristics=characteristics,
        company_nit=company_nit,
        prices=prices,
    )
