#!/bin/bash
# Build DASH GUI Docker image locally for testing
# Usage: ./build-local.sh [tag]
#   tag: Optional image tag (default: dash-gui)

set -e

TAG=${1:-dash-gui}

echo "=========================================="
echo "Building DASH GUI Docker Image (Local)"
echo "=========================================="
echo "  Tag: ${TAG}"
echo ""

echo "Building..."
docker build -t "${TAG}" .

echo ""
echo "=========================================="
echo "Build complete!"
echo "=========================================="
echo ""
echo "To start the Schema App:"
echo "  ./dev-start-schema-docker.sh 5000 ${TAG}"
echo ""
echo "To start the Brick App:"
echo "  ./dev-start-brick-docker.sh 5001 ${TAG}"
echo ""
