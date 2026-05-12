#!/bin/bash
# Docker entrypoint - allows choosing which app to start

APP=${APP:-schema}  # Default to schema app
PORT=${PORT:-5000}
HOST=${HOST:-0.0.0.0}

case "$APP" in
  schema|schema-app|schemaweb)
    echo "Starting Schema App Web on http://${HOST}:${PORT}"
    exec python run_schema_app_web.py --host "$HOST" --port "$PORT"
    ;;
  brick|brick-app|brickweb)
    echo "Starting Brick App Web on http://${HOST}:${PORT}"
    exec python run_brick_app_web.py --host "$HOST" --port "$PORT"
    ;;
  *)
    echo "Unknown APP: $APP"
    echo "Use: APP=schema (default) or APP=brick"
    exit 1
    ;;
esac
