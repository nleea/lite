"""Company persistence model. NIT is the primary key (requirement a)."""

from __future__ import annotations

from django.db import models


class Company(models.Model):
    nit = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=50)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.nit})"
