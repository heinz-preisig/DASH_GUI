# Docker Hub Setup Guide

## Automated Publishing with GitHub Actions

This project includes a GitHub Actions workflow that automatically builds and publishes the Docker image to Docker Hub.

### Prerequisites

1. Docker Hub account: `hapdocker`
2. GitHub repository access to set secrets

### Step 1: Create Docker Hub Access Token

1. Login to [Docker Hub](https://hub.docker.com)
2. Go to **Account Settings** → **Security**
3. Click **New Access Token**
4. Name: `github-actions`
5. Permissions: `Read, Write, Delete`
6. Copy the generated token (save it securely)

### Step 2: Add Secrets to GitHub Repository

1. Go to your GitHub repository: `heinz-preisig/DASH_GUI`
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the following secrets:

| Secret Name | Value |
|-------------|-------|
| `DOCKERHUB_USERNAME` | `hapdocker` |
| `DOCKERHUB_TOKEN` | *(your Docker Hub access token)* |

### Step 3: Verify Repository is Public (or plan for private)

- **Public repository**: No additional Docker Hub subscription needed
- **Private repository**: Requires Docker Hub Pro/Paid plan for private repositories

### Step 4: Test the Workflow

The workflow triggers on:
- Push to `main` or `master` branch
- Creation of version tags (e.g., `v1.0.0`)
- Publishing a GitHub Release

**Test manually:**
```bash
# Create a test tag
git tag v0.1.0-test
git push origin v0.1.0-test

# Check Actions tab in GitHub for build status
```

### Manual Publishing (Alternative)

If you prefer to publish manually without GitHub Actions:

```bash
# Login to Docker Hub
docker login -u hapdocker

# Use the publish script
./publish-docker.sh 1.0.0

# Or manually
docker build -t hapdocker/dash-gui:1.0.0 .
docker push hapdocker/dash-gui:1.0.0
```

### Using the Published Image

Once published, users can run the app without building:

```bash
# Pull and run from Docker Hub
./start-schema-app.sh 5000 hapdocker/dash-gui:latest

# Or with explicit docker command
docker run -p 5000:5000 \
  -v "$(pwd)/shared_libraries:/app/shared_libraries" \
  hapdocker/dash-gui:latest
```

### Image Tags

The workflow automatically creates multiple tags:
- `latest` - Always points to the most recent build on the default branch (main/master)
- `master` or `main` - Branch name tag for the latest commit on that branch
- `v1.0.0` - Specific version from Git tag
- `v1.0` - Minor version
- `v1` - Major version
- `sha-abc123` - Specific commit SHA

### Troubleshooting

**Build fails with "unauthorized"**
- Check `DOCKERHUB_TOKEN` is correct and not expired
- Verify `DOCKERHUB_USERNAME` is `hapdocker`

**Image not appearing on Docker Hub**
- Check repository visibility settings on Docker Hub
- Ensure repository name matches: `hapdocker/dash-gui`

**Multi-platform build fails**
- The workflow builds for `linux/amd64` and `linux/arm64`
- This requires Docker Buildx which is set up automatically

---

## Quick Reference

| Action | Command |
|--------|---------|
| Manual publish | `./publish-docker.sh 1.0.0` |
| Start from Hub | `./start-schema-app.sh 5000 hapdocker/dash-gui:latest` |
| Local build | `./start-schema-app.sh` |
| Check image | `docker pull hapdocker/dash-gui:latest` |
