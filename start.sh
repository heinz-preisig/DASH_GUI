#!/usr/bin/env bash
# DASH GUI — Docker start script for Linux/macOS
# Starts both the Schema App and Brick App web interfaces in Docker.
#
# Requirements: Docker installed and running.
# Data is persisted in the ShaclForm-library sibling directory.
#
# Usage: ./start.sh [options]
#   --open              Open both apps in the default browser
#   --image <image>     Docker image to use (default: dash-gui)
#   --schema-port <n>   Port for Schema App (default: 5000)
#   --brick-port <n>    Port for Brick App (default: 5001)
#   --help              Show this help

set -e

SCHEMA_PORT=5000
BRICK_PORT=5001
IMAGE="dash-gui"
OPEN_BROWSER=false
SCHEMA_CONTAINER="dash-gui-schema"
BRICK_CONTAINER="dash-gui-brick"

usage() {
    echo "Usage: ./start.sh [options]"
    echo "Options:"
    echo "  --open              Open both apps in the default browser"
    echo "  --image <image>     Docker image to use (default: dash-gui, or a Hub image like hapdocker/dash-gui:latest)"
    echo "  --schema-port <n>   Port for Schema App (default: 5000)"
    echo "  --brick-port <n>    Port for Brick App (default: 5001)"
    echo "  --help              Show this help"
    exit 0
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --open) OPEN_BROWSER=true; shift ;;
        --image) IMAGE="$2"; shift 2 ;;
        --schema-port) SCHEMA_PORT="$2"; shift 2 ;;
        --brick-port) BRICK_PORT="$2"; shift 2 ;;
        --help) usage ;;
        *) echo "Unknown option: $1"; usage ;;
    esac
done

# Check Docker is installed and running
if ! command -v docker >/dev/null 2>&1; then
    echo "Error: Docker is not installed."
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! docker info >/dev/null 2>&1; then
    echo "Error: Docker daemon is not running. Please start Docker first."
    exit 1
fi

# Resolve project root and library path
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIBRARY_DIR="$(cd "$SCRIPT_DIR/../ShaclForm-library" 2>/dev/null && pwd)" || true

if [[ ! -d "$LIBRARY_DIR" ]]; then
    echo "Warning: ShaclForm-library not found next to DASH_GUI. Creating empty directory."
    LIBRARY_DIR="$SCRIPT_DIR/../ShaclForm-library"
    mkdir -p "$LIBRARY_DIR"
fi

# Check/build image if not present
if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
    if [[ "$IMAGE" == *"/"* ]]; then
        echo "Pulling image $IMAGE from Docker Hub..."
        docker pull "$IMAGE"
    else
        echo "Building local Docker image $IMAGE..."
        docker build -t "$IMAGE" "$SCRIPT_DIR"
    fi
fi

# Check port availability (best-effort)
for port in "$SCHEMA_PORT" "$BRICK_PORT"; do
    if command -v lsof >/dev/null 2>&1 && lsof -i ":$port" >/dev/null 2>&1; then
        echo "Error: Port $port is already in use. Stop the existing service or choose a different port."
        exit 1
    fi
    if command -v ss >/dev/null 2>&1 && ss -tln 2>/dev/null | grep -q ":$port[[:space:]]"; then
        echo "Error: Port $port is already in use. Stop the existing service or choose a different port."
        exit 1
    fi
done

# Remove any previous containers with the same names so the script is idempotent
# (their --rm flag will also clean them up automatically when stopped)
docker rm -f "$SCHEMA_CONTAINER" "$BRICK_CONTAINER" >/dev/null 2>&1 || true

echo "Starting DASH GUI..."

docker run -d --rm \
    --name "$SCHEMA_CONTAINER" \
    -p "$SCHEMA_PORT:$SCHEMA_PORT" \
    -v "$LIBRARY_DIR:/ShaclForm-library" \
    -e APP=schema \
    -e PORT="$SCHEMA_PORT" \
    -e HOST=0.0.0.0 \
    -e SHARED_LIBRARIES_ROOT=/ShaclForm-library \
    "$IMAGE" >/dev/null

if [[ $? -ne 0 ]]; then
    echo "Error: Failed to start Schema App container."
    exit 1
fi

docker run -d --rm \
    --name "$BRICK_CONTAINER" \
    -p "$BRICK_PORT:$BRICK_PORT" \
    -v "$LIBRARY_DIR:/ShaclForm-library" \
    -e APP=brick \
    -e PORT="$BRICK_PORT" \
    -e HOST=0.0.0.0 \
    -e SHARED_LIBRARIES_ROOT=/ShaclForm-library \
    "$IMAGE" >/dev/null

if [[ $? -ne 0 ]]; then
    echo "Error: Failed to start Brick App container. Stopping Schema App..."
    docker stop "$SCHEMA_CONTAINER" >/dev/null 2>&1 || true
    exit 1
fi

# Wait for services to become reachable
SCHEMA_URL="http://localhost:$SCHEMA_PORT"
BRICK_URL="http://localhost:$BRICK_PORT"

echo "Waiting for services to start..."
for i in {1..30}; do
    if curl -s "$SCHEMA_URL/" >/dev/null 2>&1 && curl -s "$BRICK_URL/" >/dev/null 2>&1; then
        break
    fi
    sleep 1
done

echo ""
echo "DASH GUI is running:"
echo "  Schema App: $SCHEMA_URL"
echo "  Brick App:  $BRICK_URL"
echo ""
echo "Stop with: ./stop.sh"

# Open browser if requested
if [[ "$OPEN_BROWSER" == true ]]; then
    if command -v xdg-open >/dev/null 2>&1; then
        xdg-open "$SCHEMA_URL" >/dev/null 2>&1 || true
        xdg-open "$BRICK_URL" >/dev/null 2>&1 || true
    elif command -v open >/dev/null 2>&1; then
        open "$SCHEMA_URL" >/dev/null 2>&1 || true
        open "$BRICK_URL" >/dev/null 2>&1 || true
    else
        echo "Could not detect a browser opener. Please open the URLs manually."
    fi
fi
