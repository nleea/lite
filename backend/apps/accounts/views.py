"""Auth endpoints: login (JWT) and registration."""

from __future__ import annotations

from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.accounts.serializers import RoleTokenObtainPairSerializer, UserSerializer


class LoginView(TokenObtainPairView):
    """POST email + password → JWT access/refresh tokens (with `rol` claim)."""

    serializer_class = RoleTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    """Open registration (defaults to the external role)."""

    serializer_class = UserSerializer
    permission_classes = [AllowAny]
