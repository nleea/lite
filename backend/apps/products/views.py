"""Product CRUD (admin only) + inventory view. Publishes change events."""

from __future__ import annotations

from infrastructure.events.publisher import (
    PRODUCT_CREATED,
    PRODUCT_DELETED,
    PRODUCT_UPDATED,
    publish_product_event,
)
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from apps.accounts.permissions import IsAdmin, IsAdminOrReadOnly
from apps.products.models import Product
from apps.products.serializers import ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.prefetch_related("prices").select_related("company")
    serializer_class = ProductSerializer
    permission_classes = [IsAdmin]

    def _actor_id(self):
        user = getattr(self.request, "user", None)
        return getattr(user, "id", None)

    def perform_create(self, serializer):
        product = serializer.save()
        publish_product_event(PRODUCT_CREATED, product.id, self._actor_id())

    def perform_update(self, serializer):
        product = serializer.save()
        publish_product_event(PRODUCT_UPDATED, product.id, self._actor_id())

    def perform_destroy(self, instance):
        product_id = instance.id
        instance.delete()
        publish_product_event(PRODUCT_DELETED, product_id, self._actor_id())


@api_view(["GET"])
@permission_classes([IsAdminOrReadOnly])
def inventory(request):
    """Products grouped by company (the inventory table)."""
    grouped: dict[str, dict] = {}
    products = Product.objects.select_related("company").prefetch_related("prices")
    for product in products:
        company = product.company
        bucket = grouped.setdefault(
            company.nit,
            {"nit": company.nit, "name": company.name, "products": []},
        )
        bucket["products"].append(ProductSerializer(product).data)
    return Response(list(grouped.values()))
