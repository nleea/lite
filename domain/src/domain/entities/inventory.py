"""Inventory — products grouped by company."""

from __future__ import annotations

from dataclasses import dataclass, field

from domain.entities.product import Product
from domain.value_objects.nit import Nit


@dataclass(frozen=True)
class InventoryLine:
    """A single product row within a company's inventory."""

    product: Product
    quantity: int = 0


@dataclass(frozen=True)
class Inventory:
    """The set of products a company holds.

    This is a read-model-friendly aggregate: the application layer builds it
    from persisted products to render the inventory view and the PDF export.
    """

    company_nit: Nit
    lines: tuple[InventoryLine, ...] = field(default_factory=tuple)

    def with_line(self, line: InventoryLine) -> Inventory:
        return Inventory(company_nit=self.company_nit, lines=(*self.lines, line))

    @property
    def product_count(self) -> int:
        return len(self.lines)
