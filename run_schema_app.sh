#!/usr/bin/env bash
# Run the Schema App v2 (Qt GUI) using the project's uv-managed virtual environment.
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

exec uv run python run_schema_app.py "$@"
