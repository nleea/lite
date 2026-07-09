"""Tools the AI agent can call.

Each tool is self-contained (opens its own DB session) so the agent loop can
invoke them freely. They cover advanced catalogue queries and one side effect:
emailing the inventory PDF.
"""

from __future__ import annotations

from decimal import Decimal

from langchain_core.tools import tool
from sqlalchemy import func, select

from app.ai_agent.models import Company, Product
from app.ai_agent.retrieval import format_products, retrieve
from app.db import SessionLocal
from app.documents.email import EmailNotConfigured, send_inventory_pdf
from app.documents.pdf import build_inventory_pdf


def _as_nit(value: str | int | None) -> str | None:
    """NITs are numeric strings; small local models often pass them as ints."""
    return str(value) if value is not None and str(value).strip() else None


@tool
def search_products(
    query: str,
    company_nit: str | int | None = None,
    max_price_usd: float | None = None,
) -> str:
    """Search the catalogue by meaning. Optionally filter by company NIT and/or a
    maximum USD price. Use this for any question about which products match some
    description, use case, or price range."""
    max_price = Decimal(str(max_price_usd)) if max_price_usd is not None else None
    with SessionLocal() as session:
        rows = retrieve(session, query, company_id=_as_nit(company_nit), max_price_usd=max_price)
        return format_products(rows) if rows else "No matching products."


@tool
def list_companies() -> str:
    """List every company with its NIT, name, address and phone."""
    with SessionLocal() as session:
        rows = session.scalars(select(Company)).all()
        if not rows:
            return "There are no companies."
        return "\n".join(f"{c.nit}: {c.name} — {c.address}, {c.phone}" for c in rows)


@tool
def count_products(company_nit: str | int | None = None) -> str:
    """Count products in total, or for a single company when a NIT is given."""
    nit = _as_nit(company_nit)
    with SessionLocal() as session:
        stmt = select(func.count()).select_from(Product)
        if nit:
            stmt = stmt.where(Product.company_id == nit)
        total = session.scalar(stmt) or 0
        scope = f" for company {nit}" if nit else ""
        return f"{total} products{scope}."


@tool
def inventory_summary() -> str:
    """Summarize the inventory: number of products per company."""
    with SessionLocal() as session:
        rows = session.execute(
            select(Company.name, func.count(Product.id))
            .join(Product, Product.company_id == Company.nit, isouter=True)
            .group_by(Company.name)
        ).all()
        if not rows:
            return "The inventory is empty."
        return "\n".join(f"{name}: {count} products" for name, count in rows)


@tool
def anchor_inventory() -> str:
    """Anchor the current inventory PDF's hash on the blockchain for
    tamper-evidence. Use when the user asks to certify, notarize, or anchor the
    inventory on-chain. Returns the transaction and on-chain timestamp."""
    from app.blockchain import registry
    from app.blockchain.registry import BlockchainUnavailable
    from app.documents.service import inventory_pdf_bytes

    with SessionLocal() as session:
        pdf_bytes = inventory_pdf_bytes(session)
    try:
        result = registry.anchor(registry.sha256_hex(pdf_bytes))
        return (
            f"Inventory anchored on-chain. hash={result['hash'][:16]}…, "
            f"tx={result['tx_hash'][:12]}…, block={result['block']}, "
            f"anchored_at={result['anchored_at']}."
        )
    except BlockchainUnavailable as exc:
        return f"Blockchain node unavailable: {exc}"


@tool
def send_inventory_email(to_email: str) -> str:
    """Generate the full inventory PDF and email it to the given address."""
    with SessionLocal() as session:
        grouped: dict[str, dict] = {}
        for product in session.scalars(select(Product)):
            bucket = grouped.setdefault(
                product.company_id,
                {"nit": product.company_id, "name": product.company.name, "products": []},
            )
            bucket["products"].append(
                {
                    "code": product.code,
                    "name": product.name,
                    "characteristics": product.characteristics,
                    "prices": [
                        {"currency": pr.currency, "amount": str(pr.amount)} for pr in product.prices
                    ],
                }
            )
        pdf_bytes = build_inventory_pdf(list(grouped.values()))

    try:
        send_inventory_pdf(to_email, pdf_bytes)
        return f"Inventory PDF sent to {to_email}."
    except EmailNotConfigured:
        return "Email is not configured (RESEND_API_KEY missing); could not send."


TOOLS = [
    search_products,
    list_companies,
    count_products,
    inventory_summary,
    send_inventory_email,
    anchor_inventory,
]
