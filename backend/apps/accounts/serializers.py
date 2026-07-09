"""Auth serializers: JWT with a `rol` claim + user registration/read."""

from __future__ import annotations

from domain.entities import User as DomainUser
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.accounts.models import User


class RoleTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Adds `rol` and `type` claims so FastAPI can authorize offline."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["rol"] = user.role
        token["type"] = "user"
        return token


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["id", "email", "role", "password"]
        read_only_fields = ["id"]

    def validate(self, attrs):
        # Validate through the domain
        DomainUser.create(email=attrs["email"], role=attrs.get("role", "external"))
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)
