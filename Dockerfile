FROM python:3.14-slim AS base

WORKDIR /app

COPY pyproject.toml .
COPY src/ src/

RUN pip install --no-cache-dir .

ENTRYPOINT ["pulse_url"]
