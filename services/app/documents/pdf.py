"""Inventory PDF generation with ReportLab."""

from __future__ import annotations

import io

import reportlab.rl_config
reportlab.rl_config.invariant = 1

from reportlab.lib import colors  # noqa: E402
from reportlab.lib.pagesizes import A4  # noqa: E402
from reportlab.lib.styles import getSampleStyleSheet  # noqa: E402
from reportlab.platypus import (  # noqa: E402
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def build_inventory_pdf(inventory: list[dict]) -> bytes:
    """Render the inventory (products grouped by company) into PDF bytes.

    ``inventory`` shape matches Django's /api/products/inventory/ response:
    ``[{"nit", "name", "products": [{"code","name","prices":[...]}]}]``
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, title="Inventory")
    styles = getSampleStyleSheet()
    story: list = [Paragraph("Inventory Report", styles["Title"]), Spacer(1, 12)]

    for company in inventory:
        story.append(Paragraph(f"{company['name']} — NIT {company['nit']}", styles["Heading2"]))
        data = [["Code", "Name", "Characteristics", "Prices"]]
        for product in company.get("products", []):
            prices = ", ".join(f"{p['amount']} {p['currency']}" for p in product.get("prices", []))
            data.append(
                [
                    product.get("code", ""),
                    product.get("name", ""),
                    product.get("characteristics", ""),
                    prices,
                ]
            )
        table = Table(data, colWidths=[70, 120, 180, 110])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2d3748")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        story.extend([table, Spacer(1, 18)])

    doc.build(story)
    return buffer.getvalue()
