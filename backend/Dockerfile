FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false

# The domain package is a path dependency, so copy it alongside the backend.
COPY domain /app/domain
COPY backend /app/backend

WORKDIR /app/backend
RUN poetry install --no-root --no-interaction

RUN chmod +x entrypoint.sh
EXPOSE 8000
CMD ["./entrypoint.sh"]
