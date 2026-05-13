#!/bin/bash
# Start Schema App in Docker
# Usage: ./start-schema-app.sh [port] [image]
#
# Examples:
#   ./start-schema-app.sh                    # Local build, port 5000
#   ./start-schema-app.sh 5003               # Local build, port 5003
#   ./start-schema-app.sh 5000 heinz/dash-gui:latest  # Docker Hub image

PORT=${1:-5000}
IMAGE=${2:-dash-gui}

echo "Starting Schema App..."
echo "  Port:  $PORT"
echo "  Image: $IMAGE"
echo "  URL:   http://localhost:$PORT"
echo ""

# Check if image exists locally
if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
    # Check if it looks like a Docker Hub image (contains /)
    if [[ "$IMAGE" == *"/"* ]]; then
        echo "Pulling image from Docker Hub..."
        if docker pull "$IMAGE"; then
            echo "  ✓ Pulled $IMAGE"
        else
            echo "  ✗ Failed to pull $IMAGE"
            exit 1
        fi
    else
        echo "Building local Docker image..."
        docker build -t "$IMAGE" .
    fi
fi

# Run container
echo "Starting container..."
docker run -it \
    --rm \
    -p "$PORT:$PORT" \
    -v "$(pwd)/shared_libraries:/app/data" \
    -e APP=schema \
    -e PORT="$PORT" \
    "$IMAGE"
