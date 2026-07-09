import pytest

from domain.entities import User
from domain.errors import ValidationError
from domain.rules import (
    can_manage_companies,
    can_manage_products,
    can_use_ai_agent,
    can_view_companies,
)
from domain.value_objects import Role


def test_user_create_normalizes_email_and_role():
    user = User.create("Admin@Example.COM", "admin")
    assert user.email == "admin@example.com"
    assert user.role is Role.ADMIN
    assert user.is_admin


def test_user_rejects_invalid_email():
    with pytest.raises(ValidationError):
        User.create("not-an-email", "external")


def test_user_rejects_unknown_role():
    with pytest.raises(ValidationError):
        User.create("a@b.com", "superuser")


def test_admin_permissions():
    assert can_manage_companies(Role.ADMIN)
    assert can_manage_products(Role.ADMIN)
    assert can_use_ai_agent(Role.ADMIN)
    assert can_view_companies(Role.ADMIN)


def test_external_permissions():
    assert not can_manage_companies(Role.EXTERNAL)
    assert not can_manage_products(Role.EXTERNAL)
    assert not can_use_ai_agent(Role.EXTERNAL)
    assert can_view_companies(Role.EXTERNAL)
