# DASH GUI — Docker start script for Windows
# Starts both the Schema App and Brick App web interfaces in Docker.
#
# Requirements: Docker installed and running (Docker Desktop recommended).
# Data is persisted in the ShaclForm-library sibling directory.
#
# Usage: .\start.ps1 [options]
#   -Open              Open both apps in the default browser
#   -Image <image>     Docker image to use (default: dash-gui)
#   -SchemaPort <n>    Port for Schema App (default: 5000)
#   -BrickPort <n>     Port for Brick App (default: 5001)

param(
    [switch]$Open,
    [string]$Image = "dash-gui",
    [int]$SchemaPort = 5000,
    [int]$BrickPort = 5001
)

# Check Docker is installed and running
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error "Docker is not installed. Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
}

try {
    $null = docker info 2>$null
} catch {
    Write-Error "Docker daemon is not running. Please start Docker first."
    exit 1
}

# Resolve project root and library path
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$LibraryDir = Join-Path $ScriptDir "..\ShaclForm-library"

if (-not (Test-Path $LibraryDir)) {
    Write-Warning "ShaclForm-library not found next to DASH_GUI. Creating empty directory."
    New-Item -ItemType Directory -Force -Path $LibraryDir | Out-Null
}

# Check/build image if not present
$localImage = docker image inspect $Image 2>$null
if (-not $localImage) {
    if ($Image -match "/") {
        Write-Host "Pulling image $Image from Docker Hub..."
        docker pull $Image
    } else {
        Write-Host "Building local Docker image $Image..."
        docker build -t $Image $ScriptDir
    }
}

# Use fixed container names so a matching stop script works
$SchemaContainer = "dash-gui-schema"
$BrickContainer = "dash-gui-brick"

$SchemaUrl = "http://localhost:$SchemaPort"
$BrickUrl = "http://localhost:$BrickPort"

Write-Host "Starting DASH GUI..."

# Remove any previous containers with the same names so the script is idempotent
docker rm -f $SchemaContainer $BrickContainer 2>$null | Out-Null

# Start Schema App container
$schemaId = docker run -d --rm `
    --name $SchemaContainer `
    -p "$SchemaPort`:$SchemaPort" `
    -v "$LibraryDir`:/ShaclForm-library" `
    -e APP=schema `
    -e PORT=$SchemaPort `
    -e HOST=0.0.0.0 `
    -e SHARED_LIBRARIES_ROOT=/ShaclForm-library `
    $Image 2>$null

if (-not $schemaId) {
    Write-Error "Failed to start Schema App container."
    exit 1
}

# Start Brick App container
$brickId = docker run -d --rm `
    --name $BrickContainer `
    -p "$BrickPort`:$BrickPort" `
    -v "$LibraryDir`:/ShaclForm-library" `
    -e APP=brick `
    -e PORT=$BrickPort `
    -e HOST=0.0.0.0 `
    -e SHARED_LIBRARIES_ROOT=/ShaclForm-library `
    $Image 2>$null

if (-not $brickId) {
    Write-Error "Failed to start Brick App container. Stopping Schema App..."
    docker stop $SchemaContainer 2>$null | Out-Null
    exit 1
}

# Wait for services to become reachable
Write-Host "Waiting for services to start..."
$ready = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        $schemaResponse = Invoke-WebRequest -Uri "$SchemaUrl/" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
        $brickResponse = Invoke-WebRequest -Uri "$BrickUrl/" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($schemaResponse -and $schemaResponse.StatusCode -eq 200 -and $brickResponse -and $brickResponse.StatusCode -eq 200) {
            $ready = $true
            break
        }
    } catch {
        # Service not ready yet
    }
    Start-Sleep -Seconds 1
}

Write-Host ""
Write-Host "DASH GUI is running:"
Write-Host "  Schema App: $SchemaUrl"
Write-Host "  Brick App:  $BrickUrl"
Write-Host ""
Write-Host "Stop with: .\stop.ps1"

# Open browser if requested
if ($Open) {
    Start-Process $SchemaUrl
    Start-Process $BrickUrl
}
