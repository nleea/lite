from app.documents.pdf import build_inventory_pdf


def test_build_inventory_pdf_returns_pdf_bytes():
    inventory = [
        {
            "nit": "900123456",
            "name": "Acme",
            "products": [
                {
                    "code": "P-1",
                    "name": "Widget",
                    "characteristics": "outdoor",
                    "prices": [
                        {"currency": "USD", "amount": "100.00"},
                        {"currency": "COP", "amount": "400000.00"},
                    ],
                }
            ],
        }
    ]
    pdf = build_inventory_pdf(inventory)
    assert pdf[:4] == b"%PDF"
    assert len(pdf) > 500
