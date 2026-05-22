# Start FastAPI backend for Playwright e2e tests (port 10934)
$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$Runner = Join-Path $ProjectRoot "webapp\e2e_run_backend.py"

if (-not (Test-Path $Python)) {
    Write-Error "Python venv not found at $Python. Run 'uv sync' in project root first."
}

$pids = Get-NetTCPConnection -LocalPort 10934 -ErrorAction SilentlyContinue |
    Where-Object { $_.OwningProcess -gt 4 } |
    Select-Object -ExpandProperty OwningProcess -Unique
foreach ($p in $pids) {
    Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
}

& $Python $Runner
