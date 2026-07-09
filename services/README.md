# services (FastAPI)

The **validator** side of the system. It never issues tokens — it validates the
JWT Django signed (shared HS256 key) and reads the `rol` claim offline.

## Two routers

```
app/
  auth.py            validate JWT, require_admin dependency
  db.py              SQLAlchemy engine (reads Django tables, owns embeddings)
  documents/         PDF export (ReportLab) + email (Resend)  → any authed user
  ai_agent/          embeddings · Redis indexer · hybrid RAG  → admin only
```

| Method | Path                 | Who    | Notes                                  |
|--------|----------------------|--------|----------------------------------------|
| POST   | `/inventory/pdf`     | authed | streams the inventory PDF              |
| POST   | `/inventory/send`    | authed | emails the PDF via Resend (202)        |
| POST   | `/inventory/anchor`  | admin  | anchors the PDF's SHA-256 on-chain     |
| POST   | `/inventory/verify`  | authed | verifies an uploaded PDF against chain |
| GET    | `/blockchain/info`   | authed | contract address, chain id, node state |
| POST   | `/agent/chat`        | admin  | tool-calling agent over the catalogue  |
| GET    | `/health`            | open   |                                        |

## Blockchain anchoring (`app/blockchain/`)

A Solidity `DocumentRegistry` contract, deployed to a local Anvil EVM, stores the
SHA-256 of the inventory PDF (`hash → timestamp`, first-write-wins). The service
compiles it with `py-solc-x` and deploys it with `web3.py` on startup, persisting
the address in Postgres (`blockchain_deployment`) so it survives service restarts.
`anchor` is admin-only; `verify` recomputes a PDF's hash and checks the chain. The
agent also exposes an `anchor_inventory` tool.

## Data flow

- **PDF/email**: synchronous, uses the caller's user token. No broker.
- **Embeddings**: the indexer consumes `product.created|updated|deleted` from
  Redis Streams and upserts/deletes vectors in `ai_product_embedding` (pgvector).
- **Providers**: embeddings via OpenAI (Anthropic has none), generation via
  Claude/OpenAI, orchestrated by LangChain.

## Run locally

```bash
poetry install
uvicorn app.main:app --reload --port 8001
```

Requires the same `.env` as the backend (shared `JWT_SIGNING_KEY`).
