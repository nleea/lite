#!/usr/bin/env bash
set -euo pipefail

# Generate and apply migrations, then start the server.
poetry run python manage.py makemigrations accounts companies products --noinput
poetry run python manage.py migrate --noinput

# Optional: seed an initial admin if env vars are present.
if [[ -n "${DJANGO_SUPERUSER_EMAIL:-}" ]]; then
  poetry run python manage.py createsuperuser --noinput --email "$DJANGO_SUPERUSER_EMAIL" || true
fi

exec poetry run python manage.py runserver 0.0.0.0:8000
