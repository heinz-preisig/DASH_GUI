# Requires -RunAsAdministrator

Write-Host "=== Starting Docker Desktop Installation Sequence ===" -ForegroundColor Cyan

# 1. Enable WSL and Virtualization features
Write-Host "Enabling WSL 2 and Virtualization platform..." -ForegroundColor Yellow
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# 2. Set WSL version 2 as default
Write-Host "Setting WSL default version to 2..." -ForegroundColor Yellow
wsl --set-default-version 2

# 3. Download the official Docker Desktop Installer
$installerPath = "$env:TEMP\DockerDesktopInstaller.exe"
$downloadUrl = "https://docker.com"

Write-Host "Downloading Docker Desktop Installer (this may take a few minutes)..." -ForegroundColor Yellow
Invoke-WebRequest -Uri $downloadUrl -OutFile $installerPath

# 4. Install Docker Desktop silently with WSL2 backend
Write-Host "Installing Docker Desktop silently..." -ForegroundColor Yellow
# --quiet runs it silently, --backend=wsl ensures it uses WSL2 instead of Hyper-V
Start-Process -FilePath $installerPath -ArgumentList "--quiet", "--backend=wsl" -Wait

# 5. Cleanup
Write-Host "Cleaning up installer file..." -ForegroundColor Yellow
Remove-Item -Path $installerPath -Force

Write-Host "=== Installation Complete! ===" -ForegroundColor Green
Write-Host "CRITICAL: Please RESTART your computer now to finalize the setup." -ForegroundColor Red
