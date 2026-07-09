"""Role value object — the two user roles defined by the test."""

from __future__ import annotations

from enum import Enum

from domain.errors import ValidationError


class Role(str, Enum):
    """User roles.

    ADMIN can manage companies, products and inventory.
    EXTERNAL can only view companies as a visitor.
    """

    ADMIN = "admin"
    EXTERNAL = "external"

    @classmethod
    def parse(cls, raw: str) -> Role:
        """Build a Role from a string, raising a domain error on bad input."""
        try:
            return cls(str(raw).lower())
        except ValueError as exc:
            raise ValidationError(f"Unknown role: {raw!r}") from exc

    @property
    def is_admin(self) -> bool:
        return self is Role.ADMIN
