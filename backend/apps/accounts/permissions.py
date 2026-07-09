"""Role-based DRF permissions, delegating the policy to the domain rules."""

from __future__ import annotations

from domain.rules import can_manage_companies
from domain.value_objects import Role
from rest_framework.permissions import SAFE_METHODS, BasePermission


def _role_of(request) -> Role | None:
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return None
    try:
        return Role.parse(user.role)
    except Exception:
        return None


class IsAdmin(BasePermission):
    """Allow only authenticated admins."""

    def has_permission(self, request, view) -> bool:
        role = _role_of(request)
        return role is not None and role.is_admin


class IsAdminOrReadOnly(BasePermission):
    """Admins may write; any authenticated user may read (external visitor)."""

    def has_permission(self, request, view) -> bool:
        if request.method in SAFE_METHODS:
            return bool(getattr(request, "user", None) and request.user.is_authenticated)
        role = _role_of(request)
        return role is not None and can_manage_companies(role)
