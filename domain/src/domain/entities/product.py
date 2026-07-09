"""Product entity — belongs to a Company, priced in several currencies."""

from __future__ import annotations

from dataclasses import dataclass

from domain.errors import ValidationError
from domain.value_objects.money import Money
from domain.value_objects.nit import Nit


@dataclass(frozen=True)
class Product:
    """A product that belongs to a company.

    ``prices`` holds one :class:`Money` per currency. The mapping is keyed by
    currency code so a product cannot hold two prices in the same currency.
    """

    code: str
    name: str
    characteristics: str
    company_nit: Nit
    prices: dict[str, Money]

    def __post_init__(self) -> None:
        if not str(self.code).strip():
            raise ValidationError("Product code cannot be empty")
        if not str(self.name).strip():
            raise ValidationError("Product name cannot be empty")
        if not self.prices:
            raise ValidationError("Product must have at least one price")
        for currency, money in self.prices.items():
            if currency != money.currency:
                raise ValidationError(
                    f"Price key {currency!r} does not match Money currency {money.currency!r}"
                )

    @classmethod
    def create(
        cls,
        code: str,
        name: str,
        characteristics: str,
        company_nit: str,
        prices: list[Money],
    ) -> Product:
        """Factory: builds the NIT and indexes prices by currency."""
        indexed: dict[str, Money] = {}
        for money in prices:
            if money.currency in indexed:
                raise ValidationError(f"Duplicate price for currency {money.currency}")
            indexed[money.currency] = money
        return cls(
            code=code.strip(),
            name=name.strip(),
            characteristics=characteristics.strip(),
            company_nit=Nit(company_nit),
            prices=indexed,
        )

    def price_in(self, currency: str) -> Money | None:
        return self.prices.get(currency.upper())
