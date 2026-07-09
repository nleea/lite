"""Publishes product change events to a Redis Stream.

Django is the publisher; the FastAPI ai-service is the consumer. This is the
pub/sub seam that lets embedding indexing happen without a user token: no one
calls anyone, the fact is published and the actor id travels as data.

Publishing failures are swallowed so a broker outage never breaks a CRUD
operation — indexing is best-effort and self-heals on the next change.
"""

from __future__ import annotations

import logging

from django.conf import settings

logger = logging.getLogger(__name__)

# Event type constants (English, stable contract with the consumer).
PRODUCT_CREATED = "product.created"
PRODUCT_UPDATED = "product.updated"
PRODUCT_DELETED = "product.deleted"


def _client():
    import redis  # imported lazily so the app boots without redis installed

    return redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        decode_responses=True,
    )


def publish_product_event(event_type: str, product_id: str, actor_id: str | None = None) -> None:
    """Append a product event to the stream. Best-effort."""
    try:
        _client().xadd(
            settings.PRODUCT_EVENTS_STREAM,
            {
                "type": event_type,
                "product_id": str(product_id),
                "actor_id": str(actor_id or ""),
            },
        )
    except Exception:  # noqa: BLE001 - never break the request on broker issues
        logger.exception("Failed to publish product event %s for %s", event_type, product_id)
