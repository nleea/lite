"""Root URL configuration."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/companies/", include("apps.companies.urls")),
    path("api/products/", include("apps.products.urls")),
]
