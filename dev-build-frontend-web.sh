#!/bin/bash
# Build script for Schema App Web UI
# This script handles Node.js installation and React frontend build

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WEB_DIR="$SCRIPT_DIR/schema_app_v2/interfaces/web"

echo "=== Schema App Web UI Build Script ==="
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if Node.js is installed
if command_exists node; then
    echo "✓ Node.js is already installed: $(node --version)"
    NODE_VERSION=$(node --version)
else
    echo "✗ Node.js not found. Installing via nvm..."
    
    # Install nvm if not present
    if [ ! -d "$HOME/.nvm" ]; then
        echo "Installing nvm..."
        curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
    fi
    
    # Load nvm
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    
    # Install Node.js LTS
    echo "Installing Node.js LTS..."
    nvm install --lts
    nvm use --lts
fi

# Load nvm if we just installed it
if [ -d "$HOME/.nvm" ]; then
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    nvm use --lts 2>/dev/null || true
fi

# Check if npm is installed
if ! command_exists npm; then
    echo "✗ npm not found. Please install Node.js properly."
    exit 1
fi

echo "✓ npm version: $(npm --version)"
echo ""

# Navigate to web directory
cd "$WEB_DIR"

# Install npm dependencies
echo "Installing npm dependencies..."
if [ ! -d "node_modules" ]; then
    npm install
else
    echo "node_modules already exists, skipping npm install"
fi
echo ""

# Build React app
echo "Building React app..."
npm run build
echo ""

# Check if build succeeded
if [ -d "static/dist" ]; then
    echo "✓ Build successful! Static files are in: $WEB_DIR/static/dist"
    echo ""
    echo "To run the web interface:"
    echo "  cd $SCRIPT_DIR"
    echo "  uv run python run_schema_app_web.py"
else
    echo "✗ Build failed. static/dist directory not found."
    exit 1
fi

echo ""
echo "=== Build Complete ==="
