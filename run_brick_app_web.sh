#!/usr/bin/env bash
# Run the Brick App v2 (Web / Flask) using the project's uv-managed virtual environment.
# Optional arguments are forwarded to the Python launcher:
#   --port <N>        (default 5001)
#   --host <addr>     (default localhost)
#   --debug
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

exec uv run python run_brick_app_web.py "$@"
