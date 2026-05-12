#!/bin/bash
# Build script for Schema App v2 Web Frontend
# This script builds the React/Vite frontend for production deployment
#
# Usage: ./build-web-frontend.sh
# Requirements: Node.js 18+, npm
# Output: static/dist/ directory with bundled frontend
#
# After building, start the Flask server:
#   uv run python run_schema_app_web.py --port 5003
# Then access: http://localhost:5003

set -e  # Exit on error

echo "=========================================="
echo "Building Schema App v2 Web Frontend"
echo "=========================================="

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WEB_DIR="${SCRIPT_DIR}/schema_app_v2/interfaces/web"

echo ""
echo "Step 1: Checking Node.js installation..."
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed"
    echo "Please install Node.js 18+ from https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "ERROR: Node.js version 18+ required, found $(node --version)"
    exit 1
fi

echo "  ✓ Node.js $(node --version)"

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo "ERROR: npm is not installed"
    exit 1
fi

echo "  ✓ npm $(npm --version)"

echo ""
echo "Step 2: Installing dependencies..."
cd "${WEB_DIR}"

if [ ! -d "node_modules" ]; then
    echo "  Installing npm packages (this may take a few minutes)..."
    npm install
else
    echo "  node_modules exists, skipping npm install"
    echo "  (Run 'rm -rf node_modules' and re-run this script to force reinstall)"
fi

echo ""
echo "Step 3: Building production bundle..."
npm run build

echo ""
echo "Step 4: Verifying build output..."
if [ ! -f "static/dist/index.html" ]; then
    echo "ERROR: Build failed - index.html not found in static/dist/"
    exit 1
fi

if [ ! -d "static/dist/assets" ]; then
    echo "ERROR: Build failed - assets directory not found in static/dist/"
    exit 1
fi

echo "  ✓ static/dist/index.html"
echo "  ✓ static/dist/assets/"

echo ""
echo "=========================================="
echo "Build completed successfully!"
echo "=========================================="
echo ""
echo "To start the Flask server:"
echo "  cd ${SCRIPT_DIR}"
echo "  uv run python run_schema_app_web.py --port 5003"
echo ""
echo "Then open: http://localhost:5003"
echo ""
echo "Notes:"
echo "  - Port 5000 may be in use by Docker/Qt app"
echo "  - The built frontend is served from static/dist/"
echo "  - Flask automatically serves static/dist/index.html"
echo ""
