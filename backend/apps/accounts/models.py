"""Custom User model: email login + domain Role."""

from __future__ import annotations

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from domain.value_objects import Role

from apps.accounts.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """Application user. Authenticates by email; role drives authorization."""

    ROLE_CHOICES = [(role.value, role.value) for role in Role]

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=Role.EXTERNAL.value)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    def __str__(self) -> str:
        return f"{self.email} ({self.role})"

    @property
    def is_admin(self) -> bool:
        return self.role == Role.ADMIN.value
