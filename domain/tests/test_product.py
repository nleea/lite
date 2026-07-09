import pytest

from domain.entities import Product
from domain.errors import ValidationError
from domain.value_objects import Money


def test_product_with_multiple_currencies():
    product = Product.create(
        code="P-1",
        name="Widget",
        characteristics="outdoor, waterproof",
        company_nit="900123456",
        prices=[Money(100, "USD"), Money(400000, "COP")],
    )
    assert product.price_in("USD") == Money(100, "USD")
    assert product.price_in("COP") == Money(400000, "COP")


def test_product_requires_at_least_one_price():
    with pytest.raises(ValidationError):
        Product.create("P-1", "Widget", "desc", "900123456", prices=[])


def test_product_rejects_duplicate_currency():
    with pytest.raises(ValidationError):
        Product.create(
            "P-1", "Widget", "desc", "900123456",
            prices=[Money(100, "USD"), Money(120, "USD")],
        )


def test_product_rejects_invalid_company_nit():
    with pytest.raises(ValidationError):
        Product.create("P-1", "Widget", "desc", "not-a-nit", prices=[Money(1, "USD")])
