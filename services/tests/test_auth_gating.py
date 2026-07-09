import time

import jwt
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


def test_health_is_open():
    assert client.get("/health").json() == {"status": "ok"}


def test_agent_requires_token():
    # No Authorization header → HTTPBearer rejects (401/403 depending on version).
    assert client.post("/agent/chat", json={"question": "hi"}).status_code in (401, 403)


def test_agent_rejects_external_role():
    resp = client.post(
        "/agent/chat",
        json={"question": "hi"},
        headers={"Authorization": f"Bearer {_token('external')}"},
    )
    assert resp.status_code == 403


def test_agent_admin_clears_auth_gate():
    # Admin must clear authz: the response is anything BUT 401/403. Whether it is
    # 200 (provider reachable) or 503 (provider down) depends on the environment;
    # either way it proves the admin was authorized.
    resp = client.post(
        "/agent/chat",
        json={"question": "hi"},
        headers={"Authorization": f"Bearer {_token('admin')}"},
    )
    assert resp.status_code not in (401, 403)


def test_invalid_signature_rejected():
    bad = jwt.encode({"sub": "1", "rol": "admin"}, "wrong-key", algorithm="HS256")
    resp = client.post(
        "/agent/chat",
        json={"question": "hi"},
        headers={"Authorization": f"Bearer {bad}"},
    )
    assert resp.status_code == 401
