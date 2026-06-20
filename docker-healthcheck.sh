#!/bin/bash
# Docker health check for both apps
# Uses the PORT environment variable (default 5000)
PORT=${PORT:-5000}
python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT}/')" || exit 1
