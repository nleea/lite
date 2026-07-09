import time

import jwt
from app.blockchain.registry import _hash_bytes, sha256_hex
from app.config import settings
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def _token(role: str) -> str:
    return jwt.encode(
        {"sub": "1", "rol": role, "type": "user", "exp": int(time.time()) + 300},
        settings.jwt_signing_key,
        algorithm=settings.jwt_algorithm,
    )


def test_sha256_hex_is_deterministic():
    assert sha256_hex(b"abc") == sha256_hex(b"abc")
    assert sha256_hex(b"abc") != sha256_hex(b"abd")


def test_hash_bytes_is_32_bytes():
    assert len(_hash_bytes(sha256_hex(b"anything"))) == 32
    # tolerates a 0x prefix
    assert len(_hash_bytes("0x" + sha256_hex(b"x"))) == 32


def test_anchor_requires_admin():
    resp = client.post(
        "/inventory/anchor", headers={"Authorization": f"Bearer {_token('external')}"}
    )
    assert resp.status_code == 403


def test_info_requires_auth():
    assert client.get("/blockchain/info").status_code in (401, 403)
