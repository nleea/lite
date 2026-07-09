"""Company entity — identified by its NIT."""

from __future__ import annotations

from dataclasses import dataclass

from domain.errors import ValidationError
from domain.value_objects.nit import Nit


@dataclass(frozen=True)
class Company:
    """A company. Its NIT is the identity (primary key)."""

    nit: Nit
    name: str
    address: str
    phone: str

    def __post_init__(self) -> None:
        if not str(self.name).strip():
            raise ValidationError("Company name cannot be empty")
        if not str(self.address).strip():
            raise ValidationError("Company address cannot be empty")
        if not str(self.phone).strip():
            raise ValidationError("Company phone cannot be empty")

    @classmethod
    def create(cls, nit: str, name: str, address: str, phone: str) -> Company:
        """Factory that builds the NIT value object from a raw string."""
        return cls(nit=Nit(nit), name=name.strip(), address=address.strip(), phone=phone.strip())
