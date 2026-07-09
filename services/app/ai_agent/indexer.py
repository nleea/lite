"""Redis Streams consumer: keeps product embeddings in sync.

Reacts to product.created / product.updated / product.deleted events published
by Django. No user token is involved — the fact is consumed and the vector is
upserted or deleted. Runs in a background thread started by the app lifespan.
"""

from __future__ import annotations

import logging
import threading
from decimal import Decimal

from sqlalchemy import delete

from app.ai_agent.embeddings import EmbeddingsUnavailable, build_document, embed_text
from app.ai_agent.models import Product, ProductEmbedding
from app.config import settings
from app.db import SessionLocal

logger = logging.getLogger(__name__)

CONSUMER_GROUP = "ai-indexer"
CONSUMER_NAME = "indexer-1"


def _redis():
    import redis

    return redis.Redis(host=settings.redis_host, port=settings.redis_port, decode_responses=True)


def _reindex_product(product_id: int) -> None:
    with SessionLocal() as session:
        product = session.get(Product, product_id)
        if product is None:
            _delete_embedding(product_id)
            return
        content = build_document(product.name, product.characteristics, product.company.name)
        vector = embed_text(content)
        usd = next((p.amount for p in product.prices if p.currency == "USD"), None)
        row = session.get(ProductEmbedding, product_id)
        if row is None:
            row = ProductEmbedding(product_id=product_id)
            session.add(row)
        row.company_id = product.company_id
        row.code = product.code
        row.content = content
        row.min_price_usd = Decimal(usd) if usd is not None else None
        row.embedding = vector
        session.commit()


def _delete_embedding(product_id: int) -> None:
    with SessionLocal() as session:
        session.execute(delete(ProductEmbedding).where(ProductEmbedding.product_id == product_id))
        session.commit()


def _handle(event_type: str, product_id: int) -> None:
    if event_type == "product.deleted":
        _delete_embedding(product_id)
    else:
        _reindex_product(product_id)


def _ensure_group(client) -> None:
    try:
        client.xgroup_create(settings.product_events_stream, CONSUMER_GROUP, id="0", mkstream=True)
    except Exception as exc:
        if "BUSYGROUP" not in str(exc):
            raise


def _consume_loop() -> None:
    client = _redis()
    _ensure_group(client)
    logger.info("Indexer consuming stream %s", settings.product_events_stream)
    while True:
        try:
            messages = client.xreadgroup(
                CONSUMER_GROUP,
                CONSUMER_NAME,
                {settings.product_events_stream: ">"},
                count=10,
                block=5000,
            )
            for _stream, entries in messages or []:
                for message_id, fields in entries:
                    try:
                        _handle(fields["type"], int(fields["product_id"]))
                    except EmbeddingsUnavailable:
                        logger.warning("Skipping index: embeddings not configured")
                    except Exception:
                        logger.exception("Failed handling event %s", message_id)
                    finally:
                        client.xack(settings.product_events_stream, CONSUMER_GROUP, message_id)
        except Exception:
            logger.exception("Indexer loop error; retrying")


def start_indexer() -> None:
    """Start the consumer in a daemon thread (best-effort)."""
    thread = threading.Thread(target=_consume_loop, name="ai-indexer", daemon=True)
    thread.start()
