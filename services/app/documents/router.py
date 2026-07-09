"""Document endpoints: export inventory PDF and email it (Resend)."""

from __future__ import annotations

import contextlib
import re

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import Principal, current_principal
from app.db import get_session
from app.documents.email import EmailNotConfigured, send_inventory_pdf
from app.documents.service import inventory_pdf_bytes

router = APIRouter(prefix="/inventory", tags=["documents"])

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class SendRequest(BaseModel):
    to_email: str


@router.post("/pdf")
def export_pdf(
    _principal: Principal = Depends(current_principal),
    session: Session = Depends(get_session),
) -> StreamingResponse:
    pdf_bytes = inventory_pdf_bytes(session)
    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=inventory.pdf"},
    )


@router.post("/send", status_code=202)
def send_pdf(
    payload: SendRequest,
    background: BackgroundTasks,
    _principal: Principal = Depends(current_principal),
    session: Session = Depends(get_session),
) -> dict:
    if not _EMAIL_RE.match(payload.to_email):
        raise HTTPException(status_code=400, detail="Invalid destination email")
    pdf_bytes = inventory_pdf_bytes(session)
    background.add_task(_safe_send, payload.to_email, pdf_bytes)
    return {"status": "queued", "to": payload.to_email}


def _safe_send(to_email: str, pdf_bytes: bytes) -> None:
    with contextlib.suppress(EmailNotConfigured):
        send_inventory_pdf(to_email, pdf_bytes)
