#!/usr/bin/env bash
# Run the Brick App v2 (Qt GUI) using the project's uv-managed virtual environment.
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

export PYTHONPATH="$SCRIPT_DIR${PYTHONPATH:+:$PYTHONPATH}"
cd "$SCRIPT_DIR/brick_app"
exec uv run python main.py --gui "$@"
