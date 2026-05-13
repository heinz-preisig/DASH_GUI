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

# Run container
docker run -it \
    --rm \
    -p "$PORT:$PORT" \
    -v "$(pwd)/shared_libraries:/app/data" \
    -e APP=brick \
    -e PORT="$PORT" \
    "$IMAGE"
