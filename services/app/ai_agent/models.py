"""SQLAlchemy models.

Read-only reflections of the core tables Django writes, plus the embeddings
table this service owns (pgvector). Table names match Django's defaults.
"""

from __future__ import annotations

from decimal import Decimal

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config import settings
from app.db import Base


class Company(Base):
    __tablename__ = "companies_company"

    nit: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    address: Mapped[str] = mapped_column(String)
    phone: Mapped[str] = mapped_column(String)


class Product(Base):
    __tablename__ = "products_product"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String)
    characteristics: Mapped[str] = mapped_column(Text)
    company_id: Mapped[str] = mapped_column(ForeignKey("companies_company.nit"))
    quantity: Mapped[int] = mapped_column()

    company: Mapped[Company] = relationship(lazy="joined")
    prices: Mapped[list[ProductPrice]] = relationship(lazy="selectin")


class ProductPrice(Base):
    __tablename__ = "products_productprice"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products_product.id"))
    currency: Mapped[str] = mapped_column(String)
    amount: Mapped[Decimal] = mapped_column(Numeric)


class ProductEmbedding(Base):
    """Owned by this service. One vector per product + filterable metadata."""

    __tablename__ = "ai_product_embedding"

    product_id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[str] = mapped_column(String, index=True)
    code: Mapped[str] = mapped_column(String)
    content: Mapped[str] = mapped_column(Text)
    min_price_usd: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    embedding: Mapped[list[float]] = mapped_column(Vector(settings.embedding_dimensions))
