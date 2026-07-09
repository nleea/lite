# backend

Django + DRF service. It is the **token issuer** (signs JWTs with the shared
HS256 key) and owns CRUD, roles, persistence, and the product event publisher.

## Layout

```
config/                 settings, urls, wsgi
apps/
  accounts/             custom User (email login), JWT login, role permissions
  companies/            Company CRUD (NIT primary key)
  products/             Product CRUD (multi-currency) + inventory view
infrastructure/events/  Redis Streams publisher (product.created/updated/deleted)
```

Every write path builds a domain entity (via `mappers.validate_with_domain`)
so business rules stay in `domain/`, never in serializers.

## Run locally (SQLite, no Docker)

```bash
poetry install
python manage.py makemigrations accounts companies products
python manage.py migrate
python manage.py runserver
```

Leave `POSTGRES_HOST` unset to use SQLite; set it (as docker-compose does) for
PostgreSQL.

## Key endpoints

| Method | Path                     | Who        |
|--------|--------------------------|------------|
| POST   | `/api/auth/login/`       | anyone     |
| POST   | `/api/auth/register/`    | anyone     |
| CRUD   | `/api/companies/`        | read: auth, write: admin |
| CRUD   | `/api/products/`         | admin      |
| GET    | `/api/products/inventory/` | read: auth |
