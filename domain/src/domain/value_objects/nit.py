"""Nit value object — the Colombian tax id used as a Company's identity."""

from __future__ import annotations

import re
from dataclasses import dataclass

from domain.errors import ValidationError

# Digits, optionally with a check digit after a dash, e.g. "900123456" or
# "900123456-7". Kept permissive but non-empty and numeric.
_NIT_PATTERN = re.compile(r"^\d{5,15}(-\d)?$")


@dataclass(frozen=True)
class Nit:
    """A validated company tax identifier (primary key of Company)."""

    value: str

    def __post_init__(self) -> None:
        value = str(self.value).strip()
        if not value:
            raise ValidationError("NIT cannot be empty")
        if not _NIT_PATTERN.match(value):
            raise ValidationError(f"Invalid NIT format: {self.value!r}")
        object.__setattr__(self, "value", value)

    def __str__(self) -> str:
        return self.value
