"""Blockchain endpoints: anchor the inventory PDF hash and verify a PDF."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.auth import Principal, current_principal, require_admin
from app.blockchain import registry
from app.blockchain.registry import BlockchainUnavailable
from app.db import get_session
from app.documents.service import inventory_pdf_bytes

router = APIRouter(tags=["blockchain"])


@router.post("/inventory/anchor")
def anchor_inventory(
    _admin: Principal = Depends(require_admin),
    session: Session = Depends(get_session),
) -> dict:
    """Generate the inventory PDF and anchor its SHA-256 on-chain (admin only)."""
    pdf_bytes = inventory_pdf_bytes(session)
    pdf_hash = registry.sha256_hex(pdf_bytes)
    try:
        return registry.anchor(pdf_hash)
    except BlockchainUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/inventory/verify")
async def verify_pdf(
    _principal: Principal = Depends(current_principal),
    file: UploadFile = File(...),
) -> dict:
    """Verify an uploaded PDF against the chain: is its hash anchored, and when."""
    content = await file.read()
    pdf_hash = registry.sha256_hex(content)
    try:
        return registry.verify(pdf_hash)
    except BlockchainUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/blockchain/info")
def blockchain_info(_principal: Principal = Depends(current_principal)) -> dict:
    """Contract address, chain id and node reachability."""
    return registry.info()
