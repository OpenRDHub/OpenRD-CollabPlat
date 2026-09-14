# syntax=docker/dockerfile:1.7

ARG NODE_VERSION=22-bookworm-slim
ARG PYTHON_VERSION=3.12-slim-bookworm

# Build the Vue application once, then copy only its static output into Nginx.
FROM node:${NODE_VERSION} AS frontend-builder

WORKDIR /build/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
ARG VITE_ENABLE_MOCK=false
ENV VITE_ENABLE_MOCK=${VITE_ENABLE_MOCK}
# Type checking remains a separate CI step; this stage produces deployable assets.
RUN npm run build-only


# Frontend production image. The official Nginx entrypoint renders the template
# with BACKEND_HOST and BACKEND_PORT when the container starts.
FROM nginx:1.27-alpine AS frontend

ENV BACKEND_HOST=backend \
    BACKEND_PORT=8000

COPY docker/nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=frontend-builder /build/frontend/dist/ /usr/share/nginx/html/

EXPOSE 80
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget -q -O /dev/null http://127.0.0.1/healthz || exit 1


# Resolve Python dependencies from the committed uv lock file.
FROM python:${PYTHON_VERSION} AS backend-dependencies

COPY --from=ghcr.io/astral-sh/uv:0.8.14 /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app/backend
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project


# Backend production image. PostgreSQL and Redis are supplied as external
# services through DATABASE_URL and REDIS_URL.
FROM python:${PYTHON_VERSION} AS backend

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/backend/.venv/bin:${PATH}" \
    APP_ENV=production \
    APP_PORT=8000 \
    UPLOAD_DIR=/app/backend/uploads

WORKDIR /app/backend
COPY --from=backend-dependencies /app/backend/.venv ./.venv
COPY backend/ ./

RUN groupadd --system openrd \
    && useradd --system --gid openrd --home-dir /app/backend openrd \
    && mkdir -p /app/backend/uploads \
    && chown -R openrd:openrd /app/backend

USER openrd
EXPOSE 8000
VOLUME ["/app/backend/uploads"]

HEALTHCHECK --interval=30s --timeout=3s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:' + __import__('os').environ.get('APP_PORT', '8000') + '/api/v1/health', timeout=2)" || exit 1

CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port \"${APP_PORT:-8000}\""]
