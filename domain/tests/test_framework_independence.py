"""Guard test: the domain must not depend on any framework.

Walks every module under src/domain and fails if it imports a forbidden
top-level package. This enforces the Clean Architecture boundary automatically.
"""

from __future__ import annotations

import ast
import pathlib

FORBIDDEN_ROOTS = {
    "django",
    "rest_framework",
    "fastapi",
    "starlette",
    "sqlalchemy",
    "pydantic",
    "psycopg",
    "psycopg2",
    "redis",
    "requests",
    "httpx",
}

DOMAIN_SRC = pathlib.Path(__file__).resolve().parents[1] / "src" / "domain"


def _imported_roots(path: pathlib.Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.level == 0:
                roots.add(node.module.split(".")[0])
    return roots


def test_domain_imports_no_framework():
    offenders: dict[str, set[str]] = {}
    for module in DOMAIN_SRC.rglob("*.py"):
        bad = _imported_roots(module) & FORBIDDEN_ROOTS
        if bad:
            offenders[str(module.relative_to(DOMAIN_SRC))] = bad
    assert not offenders, f"Domain layer imports forbidden packages: {offenders}"
