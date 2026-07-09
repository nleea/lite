"""Shared inventory → PDF helpers, reused by the documents and blockchain routers."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai_agent.models import Product
from app.documents.pdf import build_inventory_pdf


def load_inventory(session: Session) -> list[dict]:
    """Products grouped by company (same shape Django exposes)."""
    grouped: dict[str, dict] = {}
    for product in session.scalars(select(Product)):
        company = product.company
        bucket = grouped.setdefault(
            company.nit, {"nit": company.nit, "name": company.name, "products": []}
        )
        bucket["products"].append(
            {
                "code": product.code,
                "name": product.name,
                "characteristics": product.characteristics,
                "prices": [
                    {"currency": p.currency, "amount": str(p.amount)} for p in product.prices
                ],
            }
        )
    return list(grouped.values())


def inventory_pdf_bytes(session: Session) -> bytes:
    return build_inventory_pdf(load_inventory(session))
