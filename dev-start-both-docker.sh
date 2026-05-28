#!/bin/bash
# Start both Schema and Brick Apps in Docker simultaneously
# Usage: ./dev-start-both-docker.sh [schema_port] [brick_port] [image]
#
# Examples:
#   ./dev-start-both-docker.sh                    # Defaults: schema 5000, brick 5001
#   ./dev-start-both-docker.sh 5000 5001          # Custom ports
#   ./dev-start-both-docker.sh 5000 5001 heinz/dash-gui:latest  # Docker Hub image

SCHEMA_PORT=${1:-5000}
BRICK_PORT=${2:-5001}
IMAGE=${3:-dash-gui}

echo "========================================="
echo "Starting Both DASH-GUI Applications"
echo "========================================="
echo ""
echo "Schema App:"
echo "  Port:  $SCHEMA_PORT"
echo "  URL:   http://localhost:$SCHEMA_PORT"
echo ""
echo "Brick App:"
echo "  Port:  $BRICK_PORT"
echo "  URL:   http://localhost:$BRICK_PORT"
echo ""
echo "Image:   $IMAGE"
echo "========================================="
echo ""

# Check/build image if needed
if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
    if [[ "$IMAGE" == *"/"* ]]; then
        echo "Pulling image from Docker Hub..."
        if ! docker pull "$IMAGE"; then
            echo "  ✗ Failed to pull $IMAGE"
            exit 1
        fi
        echo "  ✓ Pulled $IMAGE"
    else
        echo "Building local Docker image..."
        docker build -t "$IMAGE" .
    fi
fi

# Generate unique container names with timestamp
TIMESTAMP=$(date +%s)
SCHEMA_CONTAINER="dash-gui-schema-${TIMESTAMP}"
BRICK_CONTAINER="dash-gui-brick-${TIMESTAMP}"

echo "Starting containers..."
echo ""

# Start Schema container in background
docker run -d \
    --rm \
    --name "$SCHEMA_CONTAINER" \
    -p "$SCHEMA_PORT:$SCHEMA_PORT" \
    -v "$(pwd)/../ShaclForm-library:/ShaclForm-library" \
    --user "$(id -u):$(id -g)" \
    -e APP=schema \
    -e PORT="$SCHEMA_PORT" \
    -e SHARED_LIBRARIES_ROOT=/ShaclForm-library \
    "$IMAGE" >/dev/null

if [ $? -eq 0 ]; then
    echo "✓ Schema app started (container: $SCHEMA_CONTAINER)"
else
    echo "✗ Failed to start Schema app"
    exit 1
fi

# Start Brick container in background
docker run -d \
    --rm \
    --name "$BRICK_CONTAINER" \
    -p "$BRICK_PORT:$BRICK_PORT" \
    -v "$(pwd)/../ShaclForm-library:/ShaclForm-library" \
    --user "$(id -u):$(id -g)" \
    -e APP=brick \
    -e PORT="$BRICK_PORT" \
    -e SHARED_LIBRARIES_ROOT=/ShaclForm-library \
    "$IMAGE" >/dev/null

if [ $? -eq 0 ]; then
    echo "✓ Brick app started (container: $BRICK_CONTAINER)"
else
    echo "✗ Failed to start Brick app"
    echo "Stopping Schema container..."
    docker stop "$SCHEMA_CONTAINER" >/dev/null 2>&1
    exit 1
fi

echo ""
echo "========================================="
echo "Both apps are running!"
echo "========================================="
echo ""
echo "Access URLs:"
echo "  Schema App: http://localhost:$SCHEMA_PORT"
echo "  Brick App:  http://localhost:$BRICK_PORT"
echo ""
echo "Container names:"
echo "  Schema: $SCHEMA_CONTAINER"
echo "  Brick:  $BRICK_CONTAINER"
echo ""
echo "To stop both containers:"
echo "  docker stop $SCHEMA_CONTAINER $BRICK_CONTAINER"
echo ""
echo "Or run: ./dev-stop-both-docker.sh $SCHEMA_CONTAINER $BRICK_CONTAINER"
echo ""

# Save container names to file for easy stopping
echo "$SCHEMA_CONTAINER $BRICK_CONTAINER" > /tmp/dash-gui-containers.txt
echo "(Container names saved to /tmp/dash-gui-containers.txt)"
