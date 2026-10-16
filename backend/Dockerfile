# syntax=docker/dockerfile:1

# ---- Build stage: install dependencies into an isolated virtualenv ----
FROM python:3.13-slim AS build
ENV PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
COPY requirements.txt /tmp/requirements.txt
RUN python -m venv /opt/venv \
 && /opt/venv/bin/pip install -r /tmp/requirements.txt \
 && /opt/venv/bin/pip uninstall --yes pip

# ---- Runtime stage: no compilers, no pip cache, non-root ----
FROM python:3.13-slim
ARG APP_VERSION=dev
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_VERSION=${APP_VERSION}
LABEL org.opencontainers.image.title="stockpilot-backend" \
      org.opencontainers.image.revision="${APP_VERSION}"

# pip is not needed at runtime, and Trivy flags HIGH CVEs in the libraries it vendors
# (urllib3, msgpack), so remove it from the base image too. Smaller image, smaller attack surface.
RUN python -m pip uninstall --yes --root-user-action=ignore pip \
 && groupadd --system --gid 10001 app \
 && useradd --system --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app

WORKDIR /app
COPY --from=build /opt/venv /opt/venv
COPY alembic.ini ./
COPY alembic ./alembic
COPY app ./app

USER 10001:10001
EXPOSE 8000

# Migrations are NOT run here: Compose runs a one-shot `migrate` service and Kubernetes runs a Job,
# so several replicas never race to migrate the same database.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]
