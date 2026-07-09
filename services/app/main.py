"""FastAPI application entrypoint.

Mounts the documents and ai-agent routers and starts the embedding indexer
(Redis Streams consumer) in the background on startup.
"""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.ai_agent.router import router as agent_router
from app.blockchain.router import router as blockchain_router
from app.documents.router import router as documents_router

logging.basicConfig(level=logging.INFO)
_CORS_ORIGINS = os.environ.get("CORS_ALLOW_ORIGINS", "*").split(",")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    log = logging.getLogger(__name__)

    try:
        from app.ai_agent.models import ProductEmbedding
        from app.blockchain.models import BlockchainDeployment
        from app.db import engine

        ProductEmbedding.__table__.create(bind=engine, checkfirst=True)
        BlockchainDeployment.__table__.create(bind=engine, checkfirst=True)
    except Exception:  # noqa: BLE001
        log.exception("Could not ensure service-owned tables")

    try:
        from app.blockchain import registry

        registry.ensure_ready()
    except Exception:  # noqa: BLE001
        log.exception("Blockchain registry not ready (anchoring will 503 until it is)")

    try:
        from app.ai_agent.indexer import start_indexer

        start_indexer()
    except Exception:  # noqa: BLE001
        log.exception("Indexer failed to start")
    yield


app = FastAPI(title="Lite Thinking Services", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(documents_router)
app.include_router(agent_router)
app.include_router(blockchain_router)


@app.get("/health", tags=["meta"])
def health() -> dict:
    return {"status": "ok"}
