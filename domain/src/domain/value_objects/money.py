"""Money value object — an immutable (amount, currency) pair."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from domain.errors import CurrencyMismatchError, ValidationError

# ISO-4217-style codes we accept in this test. Kept small on purpose.
_ALLOWED_CURRENCIES = frozenset({"USD", "COP", "EUR", "MXN"})


@dataclass(frozen=True)
class Money:
    """A monetary amount in a single currency.

    Amounts are stored as :class:`~decimal.Decimal` to avoid float rounding.
    Instances are immutable; arithmetic returns new instances and refuses to
    mix currencies.
    """

    amount: Decimal
    currency: str

    def __post_init__(self) -> None:
        try:
            amount = Decimal(str(self.amount))
        except (InvalidOperation, TypeError) as exc:
            raise ValidationError(f"Invalid money amount: {self.amount!r}") from exc

        if amount < 0:
            raise ValidationError("Money amount cannot be negative")

        currency = str(self.currency).upper()
        if currency not in _ALLOWED_CURRENCIES:
            raise ValidationError(f"Unsupported currency: {self.currency!r}")

        # Frozen dataclass: bypass the immutability guard to normalize fields.
        object.__setattr__(self, "amount", amount)
        object.__setattr__(self, "currency", currency)

    def add(self, other: Money) -> Money:
        self._assert_same_currency(other)
        return Money(self.amount + other.amount, self.currency)

    def _assert_same_currency(self, other: Money) -> None:
        if self.currency != other.currency:
            raise CurrencyMismatchError(f"Cannot operate on {self.currency} and {other.currency}")

    def __str__(self) -> str:
        return f"{self.amount} {self.currency}"
