"""Domain layer: pure business entities and rules.

This package must not import any web framework, ORM, or HTTP library.
See tests/test_framework_independence.py for the enforced boundary.
"""

from domain.entities import Company, Inventory, InventoryLine, Product, User
from domain.errors import (
    CurrencyMismatchError,
    DomainError,
    PermissionDeniedError,
    ValidationError,
)
from domain.value_objects import Money, Nit, Role

__all__ = [
    # entities
    "Company",
    "Product",
    "User",
    "Inventory",
    "InventoryLine",
    # value objects
    "Money",
    "Nit",
    "Role",
    # errors
    "DomainError",
    "ValidationError",
    "CurrencyMismatchError",
    "PermissionDeniedError",
]
