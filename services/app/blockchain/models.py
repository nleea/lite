"""Persistence for the deployed contract, so the address survives service
restarts (the Anvil node itself is still ephemeral)."""

from __future__ import annotations

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class BlockchainDeployment(Base):
    __tablename__ = "blockchain_deployment"

    chain_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    address: Mapped[str] = mapped_column(String)
    abi: Mapped[str] = mapped_column(Text)  # JSON-encoded contract ABI
