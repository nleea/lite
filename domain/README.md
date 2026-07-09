# domain

Pure-Python business layer for the Lite Thinking application, following Clean
Architecture. This package contains **only** entities, value objects, and
business rules.

## The one rule

This package **must not** import any framework:

- no `django` / `rest_framework`
- no `fastapi` / HTTP libraries
- no `sqlalchemy` / ORM / database drivers

Dependencies always point *inward*, toward this package. `backend/` and
`services/` import `domain`; `domain` imports nobody. A guard test
(`tests/test_framework_independence.py`) enforces this automatically.

## Contents

```
src/domain/
├── errors.py           domain exceptions (never HTTP)
├── value_objects/      Money, Nit, Role
├── entities/           Company, Product, User, Inventory
└── rules/              permissions (role-based)
```

## Consumed by the backend / services

```toml
# in backend/ and services/ pyproject.toml
domain = { path = "../domain", develop = true }
```

## Tests

```bash
poetry install
poetry run pytest
```
