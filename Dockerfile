# syntax=docker/dockerfile:1

FROM python:3.12-slim AS dependencies

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY src ./src

RUN python -m pip install --upgrade pip \
    && python -m pip install --prefix=/install .

FROM python:3.12-slim AS runtime

ARG APP_VERSION=1.0.1
ARG APP_COMMIT=unknown

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    APP_VERSION=${APP_VERSION} \
    APP_COMMIT=${APP_COMMIT}

WORKDIR /app

COPY --from=dependencies /install /usr/local

RUN groupadd --system nonroot \
    && useradd --system --gid nonroot --create-home nonroot

COPY --chown=nonroot:nonroot src ./src

USER nonroot

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:' + __import__('os').environ.get('PORT', '8000') + '/health', timeout=2)"

CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT} --workers 2 --timeout 30 juego_numero.app:app"]
