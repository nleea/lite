"""Product serializer with nested multi-currency prices + domain validation."""

from __future__ import annotations

from domain.errors import ValidationError as DomainValidationError
from domain.value_objects import Money
from rest_framework import serializers

from apps.companies.models import Company
from apps.products.mappers import validate_with_domain
from apps.products.models import Product, ProductPrice


class ProductPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPrice
        fields = ["currency", "amount"]


class ProductSerializer(serializers.ModelSerializer):
    prices = ProductPriceSerializer(many=True)
    company = serializers.SlugRelatedField(slug_field="nit", queryset=Company.objects.all())

    class Meta:
        model = Product
        fields = ["id", "code", "name", "characteristics", "company", "quantity", "prices"]
        read_only_fields = ["id"]

    def validate(self, attrs):
        prices_data = attrs.get("prices") or (
            [{"currency": p.currency, "amount": p.amount} for p in self.instance.prices.all()]
            if self.instance
            else []
        )
        try:
            money_list = [Money(p["amount"], p["currency"]) for p in prices_data]
            company = attrs.get("company") or (self.instance.company if self.instance else None)
            validate_with_domain(
                code=attrs.get("code", getattr(self.instance, "code", "")),
                name=attrs.get("name", getattr(self.instance, "name", "")),
                characteristics=attrs.get(
                    "characteristics", getattr(self.instance, "characteristics", "")
                ),
                company_nit=company.nit if company else "",
                prices=money_list,
            )
        except DomainValidationError as exc:
            raise serializers.ValidationError(str(exc)) from exc
        return attrs

    def create(self, validated_data):
        prices = validated_data.pop("prices")
        product = Product.objects.create(**validated_data)
        self._sync_prices(product, prices)
        return product

    def update(self, instance, validated_data):
        prices = validated_data.pop("prices", None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        if prices is not None:
            instance.prices.all().delete()
            self._sync_prices(instance, prices)
        return instance

    @staticmethod
    def _sync_prices(product, prices):
        ProductPrice.objects.bulk_create(
            [ProductPrice(product=product, **price) for price in prices]
        )
