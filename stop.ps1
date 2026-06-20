# DASH GUI — Docker stop script for Windows
# Stops the containers started by start.ps1.

Write-Host "Stopping DASH GUI containers..."
docker stop dash-gui-schema dash-gui-brick 2>$null | Out-Null
Write-Host "DASH GUI stopped."
