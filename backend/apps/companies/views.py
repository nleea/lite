"""Company CRUD. Admins write; any authenticated user reads (external visitor)."""

from __future__ import annotations

from rest_framework import viewsets

from apps.accounts.permissions import IsAdminOrReadOnly
from apps.companies.models import Company
from apps.companies.serializers import CompanySerializer


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "nit"
