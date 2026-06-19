#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "=== Starting Docker Desktop Installation Sequence for macOS ==="

# 1. Detect Processor Architecture (Apple Silicon vs Intel)
ARCH=$(uname -m)
if [ "$ARCH" = "arm64" ]; then
    echo "Detected Apple Silicon (M-series) Mac..."
    DOWNLOAD_URL="https://docker.com"
elif [ "$ARCH" = "x86_64" ]; then
    echo "Detected Intel Mac..."
    DOWNLOAD_URL="https://docker.com"
else
    echo "Unknown processor architecture: $ARCH"
    exit 1
fi

# 2. Download Docker DMG to the Downloads folder
DMG_PATH="$HOME/Downloads/Docker.dmg"
echo "Downloading Docker Desktop (this may take a few minutes)..."
curl -L "$DOWNLOAD_URL" -o "$DMG_PATH"

# 3. Mount the DMG file
echo "Mounting disk image..."
VOLUME_PATH=$(hdiutil mount "$DMG_PATH" | tail -n 1 | awk -F '\t' '{print $3}')

# 4. Copy Docker to the Applications folder
echo "Installing Docker Desktop to /Applications..."
sudo cp -R "$VOLUME_PATH/Docker.app" /Applications/

# 5. Unmount the DMG file and clean up
echo "Unmounting and cleaning up..."
hdiutil unmount "$VOLUME_PATH"
rm "$DMG_PATH"

# 6. Initialize Docker privileged background components
echo "Initializing background system components..."
/Applications/Docker.app/Contents/MacOS/Docker --unattended --install-privileged-components

echo "=== Installation Complete! ==="
echo "You can now open Docker from your Applications folder or Launchpad."
