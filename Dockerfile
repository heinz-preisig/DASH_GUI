# DASH GUI - Web Interface Only
# Multi-stage build for smaller image

FROM node:18-slim AS node-builder

# Cache-busting arguments - forces rebuild when GitHub Actions runs
ARG BUILD_TIMESTAMP=unknown
ARG GIT_SHA=unknown

WORKDIR /app/web

# Copy web interface package files
COPY schema_app/interfaces/web/package*.json ./

# Install npm dependencies
RUN npm install

# Copy web interface source
COPY schema_app/interfaces/web/src ./src
COPY schema_app/interfaces/web/vite.config.js ./
COPY schema_app/interfaces/web/index.html ./

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

# Copy React build from node-builder (verified to exist)
COPY --from=node-builder /app/web/static ./schema_app/interfaces/web/static

# Verify the React build was copied correctly
RUN ls -la /app/schema_app/interfaces/web/static/dist/ && \
    test -f /app/schema_app/interfaces/web/static/dist/index.html && \
    echo "✓ React build verified"

# Copy application code (excluding node_modules and other dev artifacts)
COPY . .

# Make entrypoint executable
RUN chmod +x docker-entrypoint.sh

# Final verification: Ensure React build is present
RUN if [ -f /app/schema_app/interfaces/web/static/dist/index.html ]; then \
        echo "✓ React build present in final image"; \
        ls -la /app/schema_app/interfaces/web/static/dist/; \
    else \
        echo "✗ ERROR: React build missing!"; \
        exit 1; \
    fi

# Expose web ports (both apps)
EXPOSE 5000 5001

# Health check (works for both apps, checks schema app by default)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/')" || exit 1

# Default data path — mounted outside the /app code tree
ENV SHARED_LIBRARIES_ROOT=/ShaclForm-library

# Use entrypoint script for flexible app selection
ENTRYPOINT ["./docker-entrypoint.sh"]
