#!/usr/bin/env bash
# Run the full pytest test suite from the project root.

set -euo pipefail

cd "$(dirname "$0")"

uv run python -m pytest tests/ -v
