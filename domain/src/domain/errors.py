"""Domain-level exceptions.

These are pure business errors. They must never carry HTTP status codes or
framework concepts — the application layer is responsible for translating them
into transport-specific responses.
"""


class DomainError(Exception):
    """Base class for all domain errors."""


class ValidationError(DomainError):
    """Raised when an entity or value object breaks an invariant."""


class CurrencyMismatchError(DomainError):
    """Raised when operating on monetary amounts of different currencies."""


class PermissionDeniedError(DomainError):
    """Raised when a role is not allowed to perform an action."""
