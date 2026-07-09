from decimal import Decimal

import pytest

from domain.errors import CurrencyMismatchError, ValidationError
from domain.value_objects import Money


def test_money_normalizes_amount_and_currency():
    money = Money("10.50", "usd")
    assert money.amount == Decimal("10.50")
    assert money.currency == "USD"


def test_money_rejects_negative_amount():
    with pytest.raises(ValidationError):
        Money(-1, "USD")


def test_money_rejects_unknown_currency():
    with pytest.raises(ValidationError):
        Money(10, "XYZ")


def test_money_add_same_currency():
    assert Money(10, "USD").add(Money(5, "USD")) == Money(15, "USD")


def test_money_add_different_currency_raises():
    with pytest.raises(CurrencyMismatchError):
        Money(10, "USD").add(Money(5, "COP"))
