# jellyfin-mcp starter (fleet-standard minimal)
param([switch]$BackendOnly)
$ErrorActionPreference = "Stop"
$Repo = $PSScriptRoot
$UV = "C:\Users\sandr\.local\bin\uv.exe"
$BackendPort = 10934
$FrontendPort = 10935
Write-Host "=== jellyfin-mcp ===" -ForegroundColor Cyan

# Port zombie clearing before bind (10934 backend)
$zombie = Get-NetTCPConnection -LocalPort $BackendPort -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
foreach ($pid_ in $zombie) {
  try { Stop-Process -Id $pid_ -Force -ErrorAction Stop; Write-Host "cleared PID $pid_ on $BackendPort" } catch { Write-Host "PID $pid_ already gone" }
}

$backend = Start-Process -FilePath $UV -ArgumentList "run","python","-m","jellyfin_mcp","--http","--port",$BackendPort -WorkingDirectory $Repo -PassThru -WindowStyle Hidden

# Backend readiness TCP poll (not fixed sleep), 30x2s
$ready = $false
for ($i = 0; $i -lt 30; $i++) {
  Start-Sleep -Seconds 2
  $c = Get-NetTCPConnection -LocalPort $BackendPort -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($c) { $ready = $true; break }
}
if (-not $ready) { Write-Host "backend did not bind $BackendPort in 60s" -ForegroundColor Red; exit 1 }
Write-Host "backend on $BackendPort" -ForegroundColor Green

if ($BackendOnly) { exit 0 }

# Frontend (Next.js) via webapp start
$fe = Join-Path $Repo "webapp\frontend"
if (Test-Path (Join-Path $fe "package.json")) {
  Start-Process -FilePath "powershell.exe" -ArgumentList "-NoProfile","-Command","cd '$fe'; npm run dev" -WorkingDirectory $fe
  Start-Sleep -Seconds 5
  Start-Process "http://localhost:$FrontendPort"
} else {
  Write-Host "no frontend package.json, backend-only" -ForegroundColor Yellow
}
