# DASH GUI - Web Interface Only
# Multi-stage build for smaller image

FROM node:18-slim AS node-builder

WORKDIR /app/web

# Copy web interface package files
COPY schema_app_v2/interfaces/web/package*.json ./

# Install npm dependencies
RUN npm install

# Copy web interface source
COPY schema_app_v2/interfaces/web/src ./src
COPY schema_app_v2/interfaces/web/vite.config.js ./
COPY schema_app_v2/interfaces/web/index.html ./

# Build React app
RUN npm run build

FROM python:3.13-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Create virtual environment and install dependencies (no Qt for web)
RUN uv venv .venv && \
    uv pip install flask flask-cors rdflib pandas --system

# Production stage
FROM python:3.13-slim

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages

# Copy React build from node-builder
COPY --from=node-builder /app/web/static ./schema_app_v2/interfaces/web/static

# Copy application code (excluding node_modules and other dev artifacts)
COPY . .

# Make entrypoint executable
RUN chmod +x docker-entrypoint.sh

# Expose web ports (both apps)
EXPOSE 5000 5001

# Health check (works for both apps, checks schema app by default)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/')" || exit 1

# Use entrypoint script for flexible app selection
ENTRYPOINT ["./docker-entrypoint.sh"]
