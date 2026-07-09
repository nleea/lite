"""User entity — authenticates by email, carries a Role."""

from __future__ import annotations

import re
from dataclasses import dataclass

from domain.errors import ValidationError
from domain.value_objects.role import Role

_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass(frozen=True)
class User:
    """An application user.

    The domain models identity and role only. Password hashing lives in the
    infrastructure layer (the domain never sees credentials).
    """

    email: str
    role: Role

    def __post_init__(self) -> None:
        email = str(self.email).strip().lower()
        if not _EMAIL_PATTERN.match(email):
            raise ValidationError(f"Invalid email: {self.email!r}")
        object.__setattr__(self, "email", email)

    @classmethod
    def create(cls, email: str, role: str | Role) -> User:
        parsed_role = role if isinstance(role, Role) else Role.parse(role)
        return cls(email=email, role=parsed_role)

    @property
    def is_admin(self) -> bool:
        return self.role.is_admin
