"""Send the inventory PDF by email via Resend (REST API)."""

from __future__ import annotations

import base64

from app.config import settings


class EmailNotConfigured(RuntimeError):
    pass


def send_inventory_pdf(to_email: str, pdf_bytes: bytes) -> dict:
    """Email the PDF as an attachment. Raises if Resend isn't configured."""
    if not settings.resend_api_key:
        raise EmailNotConfigured("RESEND_API_KEY is not set")

    import resend

    resend.api_key = settings.resend_api_key
    encoded = base64.b64encode(pdf_bytes).decode("ascii")
    return resend.Emails.send(
        {
            "from": settings.email_from,
            "to": [to_email],
            "subject": "Inventory Report",
            "html": "<p>Attached is the requested inventory report.</p>",
            "attachments": [{"filename": "inventory.pdf", "content": encoded}],
        }
    )
