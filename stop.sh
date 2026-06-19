#!/usr/bin/env bash
# DASH GUI — Docker stop script for Linux/macOS
# Stops the containers started by start.sh.

set -e

echo "Stopping DASH GUI containers..."
docker stop dash-gui-schema dash-gui-brick 2>/dev/null || true
echo "DASH GUI stopped."
