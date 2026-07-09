FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false

COPY domain /app/domain
COPY services /app/services

WORKDIR /app/services
RUN poetry install --no-root --no-interaction

EXPOSE 8001
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
