FROM python:3.12-slim

ENV POETRY_VERSION=1.8.3 \
    POETRY_NO_INTERACTION=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y build-essential curl && rm -rf /var/lib/apt/lists/*
RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /corner_pocket_backend
COPY pyproject.toml poetry.lock* /corner_pocket_backend/
RUN poetry install --no-root --only main

COPY . /corner_pocket_backend
EXPOSE 8000
CMD ["poetry","run","uvicorn","corner_pocket_backend.main:corner_pocket_backend","--host","0.0.0.0","--port","8000"]
