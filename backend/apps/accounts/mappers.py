"""Translation between the Django User model and the domain User entity."""

from __future__ import annotations

from domain.entities import User as DomainUser

from apps.accounts.models import User as UserModel


def to_domain(user: UserModel) -> DomainUser:
    """Build a pure domain User from a persisted Django user."""
    return DomainUser.create(email=user.email, role=user.role)
