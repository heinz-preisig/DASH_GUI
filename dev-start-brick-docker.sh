#!/bin/bash
# Start Brick App in Docker
# Usage: ./start-brick-app.sh [port]

PORT=${1:-5001}
IMAGE=${2:-dash-gui}

echo "Starting Brick App..."
echo "  Port: $PORT"
echo "  URL: http://localhost:$PORT"
echo ""

# Build if image doesn't exist
if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
    echo "Building Docker image..."
    docker build -t "$IMAGE" .
fi

# Run container as current user to prevent permission issues
docker run -it \
    --rm \
    -p "$PORT:$PORT" \
    -v "$(pwd)/../ShaclForm_library:/ShaclForm_library" \
    --user "$(id -u):$(id -g)" \
    -e APP=brick \
    -e PORT="$PORT" \
    -e SHARED_LIBRARIES_ROOT=/ShaclForm_library \
    "$IMAGE"
