"""Company serializer with domain-delegated validation."""

from __future__ import annotations

from domain.errors import ValidationError as DomainValidationError
from rest_framework import serializers

from apps.companies.mappers import validate_with_domain
from apps.companies.models import Company


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["nit", "name", "address", "phone"]

    def validate(self, attrs):
        """Delegate business validation to the domain layer."""
        # On update, fall back to existing values for partial payloads.
        instance = getattr(self, "instance", None)

        def pick(field):
            if field in attrs:
                return attrs[field]
            return getattr(instance, field) if instance else ""

        try:
            validate_with_domain(
                nit=pick("nit"),
                name=pick("name"),
                address=pick("address"),
                phone=pick("phone"),
            )
        except DomainValidationError as exc:
            raise serializers.ValidationError(str(exc)) from exc
        return attrs
