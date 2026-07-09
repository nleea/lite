"""Company model <-> domain entity translation."""

from __future__ import annotations

from domain.entities import Company as DomainCompany

from apps.companies.models import Company


def to_domain(company: Company) -> DomainCompany:
    return DomainCompany.create(
        nit=company.nit,
        name=company.name,
        address=company.address,
        phone=company.phone,
    )


def validate_with_domain(nit: str, name: str, address: str, phone: str) -> DomainCompany:
    """Run domain invariants before persisting. Raises domain ValidationError."""
    return DomainCompany.create(nit=nit, name=name, address=address, phone=phone)
