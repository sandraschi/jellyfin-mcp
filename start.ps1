# jellyfin-mcp starter
param([switch]$BackendOnly)
$ErrorActionPreference = "Stop"
$Repo = $PSScriptRoot
$UV = "C:\Users\sandr\.local\bin\uv.exe"
Write-Host "=== jellyfin-mcp ===" -ForegroundColor Cyan
& $UV run python -m jellyfin_mcp
