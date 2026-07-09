from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.products.views import ProductViewSet, inventory

router = DefaultRouter()
router.register("", ProductViewSet, basename="product")

urlpatterns = [
    path("inventory/", inventory, name="inventory"),
    *router.urls,
]
