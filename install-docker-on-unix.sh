#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "=== Starting Docker Installation Sequence for Ubuntu ==="

# 1. Remove old or conflicting Docker versions
echo "Removing conflicting Docker packages..."
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do
    sudo apt-get remove -y $pkg || true
done

# 2. Update package index and install prerequisites
echo "Installing prerequisites..."
sudo apt-get update
sudo apt-get install -y ca-certificates curl

# 3. Add Docker's official GPG key
echo "Adding Docker GPG key..."
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://docker.com -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# 4. Set up the stable Docker repository
echo "Setting up repository..."
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://docker.com \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 5. Install Docker Engine, CLI, and Plugins
echo "Installing Docker Engine..."
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 6. Post-installation: Allow running Docker without 'sudo'
echo "Configuring permissions..."
sudo usermod -aG docker $USER

echo "=== Installation Complete! ==="
echo "CRITICAL: Please log out and log back in (or run 'newgrp docker') for the permissions to take effect."
