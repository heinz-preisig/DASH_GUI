#!/bin/bash
# Build and publish DASH GUI Docker image to Docker Hub
#
# Usage: ./publish-docker.sh [tag]
#   tag: Optional image tag (default: latest)
#
# Prerequisites:
#   - Docker installed and running
#   - Logged in to Docker Hub: docker login
#   - Docker Hub username (default: hapdocker, override with DOCKERHUB_USER env var)
#
# Example:
#   ./publish-docker.sh 1.0.0
#   DOCKERHUB_USER=myuser ./publish-docker.sh latest

set -e

# Get tag from args or default to latest
TAG=${1:-latest}

#
if [ -z "$DOCKERHUB_USER" ]; then
    DOCKERHUB_USER="hapdocker"
    echo "Using default Docker Hub username: $DOCKERHUB_USER"
    echo "(Set DOCKERHUB_USER env var to override)"
    echo ""
fi

IMAGE_NAME="${DOCKERHUB_USER}/dash-gui"
FULL_TAG="${IMAGE_NAME}:${TAG}"

echo "=========================================="
echo "Publishing DASH GUI to Docker Hub"
echo "=========================================="
echo "  Image: ${IMAGE_NAME}"
echo "  Tag:   ${TAG}"
echo "  Full:  ${FULL_TAG}"
echo ""

# Check if logged in to Docker Hub
echo "Step 1: Checking Docker Hub login..."
if ! docker info >/dev/null 2>&1; then
    echo "Error: Docker daemon not running"
    exit 1
fi

if ! docker system info 2>/dev/null | grep -q "Username"; then
    echo "Not logged in to Docker Hub"
    echo "Please run: docker login"
    exit 1
fi

echo "  ✓ Logged in to Docker Hub"
echo ""

# Build the image
echo "Step 2: Building Docker image..."
docker build -t "${FULL_TAG}" -t "${IMAGE_NAME}:latest" .

echo "  ✓ Build complete"
echo ""

# Push to Docker Hub
echo "Step 3: Pushing to Docker Hub..."
echo "  Pushing ${FULL_TAG}..."
docker push "${FULL_TAG}"

if [ "$TAG" != "latest" ]; then
    echo "  Pushing ${IMAGE_NAME}:latest..."
    docker push "${IMAGE_NAME}:latest"
fi

echo "  ✓ Push complete"
echo ""

echo "=========================================="
echo "Published successfully!"
echo "=========================================="
echo ""
echo "Users can now run:"
echo "  docker pull ${FULL_TAG}"
echo "  ./start-schema-app.sh 5000 ${FULL_TAG}"
echo ""
echo "Or simply:"
echo "  docker run -p 5000:5000 ${FULL_TAG}"
echo ""
