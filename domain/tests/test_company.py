import pytest

from domain.entities import Company
from domain.errors import ValidationError
from domain.value_objects import Nit


def test_company_create_valid():
    company = Company.create("900123456-7", "Acme", "5th Ave", "555-1000")
    assert company.nit == Nit("900123456-7")
    assert company.name == "Acme"


def test_company_rejects_invalid_nit():
    with pytest.raises(ValidationError):
        Company.create("abc", "Acme", "5th Ave", "555-1000")


def test_company_rejects_empty_name():
    with pytest.raises(ValidationError):
        Company.create("900123456", "  ", "5th Ave", "555-1000")


def test_company_is_immutable():
    company = Company.create("900123456", "Acme", "5th Ave", "555-1000")
    with pytest.raises(Exception):
        company.name = "Other"  # type: ignore[misc]
