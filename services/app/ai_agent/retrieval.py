"""Hybrid retrieval over the product embeddings (pgvector).

Kept separate from the agent so both the agent and its tools can reuse it
without a circular import.
"""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai_agent.embeddings import embed_text
from app.ai_agent.models import ProductEmbedding


def retrieve(
    session: Session,
    question: str,
    *,
    company_id: str | None = None,
    max_price_usd: Decimal | None = None,
    top_k: int = 5,
) -> list[ProductEmbedding]:
    """Hybrid retrieval: metadata WHERE filters + semantic ORDER BY distance."""
    query_vector = embed_text(question)
    stmt = select(ProductEmbedding)
    if company_id:
        stmt = stmt.where(ProductEmbedding.company_id == company_id)
    if max_price_usd is not None:
        stmt = stmt.where(ProductEmbedding.min_price_usd <= max_price_usd)
    stmt = stmt.order_by(ProductEmbedding.embedding.cosine_distance(query_vector)).limit(top_k)
    return list(session.scalars(stmt))


def format_products(rows: list[ProductEmbedding]) -> str:
    if not rows:
        return "(no products)"
    return "\n".join(
        f"- [{row.code}] {row.content}"
        + (f" (min USD price: {row.min_price_usd})" if row.min_price_usd is not None else "")
        for row in rows
    )
