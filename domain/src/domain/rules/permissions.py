"""Role-based business rules.

These functions express *who may do what* in pure domain terms. The application
layer calls them to authorize actions; it does not re-implement the policy.
"""

from __future__ import annotations

from domain.value_objects.role import Role


def can_manage_companies(role: Role) -> bool:
    """Only admins may create/edit/delete companies."""
    return role.is_admin


def can_manage_products(role: Role) -> bool:
    """Only admins may register products and inventory."""
    return role.is_admin


def can_view_companies(role: Role) -> bool:
    """Both admin and external users may view companies."""
    return role in (Role.ADMIN, Role.EXTERNAL)


def can_use_ai_agent(role: Role) -> bool:
    """The AI agent is restricted to admins only."""
    return role.is_admin
