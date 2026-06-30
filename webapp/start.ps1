Param([switch]$Headless)
$SkipFrontend = $Headless

# --- SOTA Headless Standard ---
if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {
    Start-Process pwsh -ArgumentList '-NoProfile', '-File', $PSCommandPath, '-Headless' -WindowStyle Hidden
    exit
}
# ------------------------------

$WebPort = 10935
$BackendPort = 10934
$FleetStartPath = Join-Path $ProjectRoot "scripts\FleetStartMode.ps1"
if (-not (Test-Path -LiteralPath $FleetStartPath)) {
    Write-Host "ERROR: Missing vendored launcher helper: $FleetStartPath" -ForegroundColor Red
    exit 1
}
. $FleetStartPath

$ProjectRoot = Split-Path -Parent $PSScriptRoot

# 0. Ensure npm root
$NpmRoot = $PSScriptRoot
if (-not (Test-Path (Join-Path $NpmRoot "package.json"))) {
    $NpmRoot = Join-Path $PSScriptRoot "frontend"
}
if (-not (Test-Path (Join-Path $NpmRoot "package.json"))) {
    Write-Host "ERROR: package.json not found in $PSScriptRoot or $PSScriptRoot\frontend." -ForegroundColor Red
    exit 1
}

# 1. Kill port squatters
Write-Host "Checking for port squatters on $WebPort and $BackendPort..." -ForegroundColor Yellow
$pids = Get-NetTCPConnection -LocalPort $WebPort, $BackendPort -ErrorAction SilentlyContinue |
    Where-Object { $_.OwningProcess -gt 4 } |
    Select-Object -ExpandProperty OwningProcess -Unique

foreach ($p in $pids) {
    try {
        $proc = Get-Process -Id $p -ErrorAction SilentlyContinue
        if ($proc) {
            Write-Host "Found squatter '$($proc.Name)' (PID: $p). Terminating..." -ForegroundColor Red
            Stop-Process -Id $p -Force -ErrorAction Stop
        }
    } catch {
        Write-Host "Warning: Could not terminate PID $p." -ForegroundColor Gray
    }
}

# 2. Install deps
Set-Location $NpmRoot
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Gray
    npm install
}

# 3. Start Python backend
Write-Host "Starting Python backend on port $BackendPort ..." -ForegroundColor Cyan
$BackendDir = Join-Path $ProjectRoot "webapp\backend"
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$backendCmd = "`$env:PYTHONPATH = '$ProjectRoot\src;$BackendDir'; Set-Location '$BackendDir'; & '$VenvPython' -m uvicorn app.main:app --host 127.0.0.1 --port $BackendPort --log-level info"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -WindowStyle Normal

# 4. Wait for backend readiness
$maxRetries = 30
$retryCount = 0
$backendReady = $false
Write-Host "Waiting for backend readiness..." -ForegroundColor Yellow -NoNewline

while (-not $backendReady -and $retryCount -lt $maxRetries) {
    try {
        $resp = Invoke-WebRequest -Uri "http://127.0.0.1:$BackendPort/health" -Method Get -TimeoutSec 2 -ErrorAction Stop
        if ($resp.StatusCode -eq 200) { $backendReady = $true }
    } catch { }
    if (-not $backendReady) {
        Write-Host "." -NoNewline
        Start-Sleep -Seconds 1
        $retryCount++
    }
}

if ($backendReady) {
    Write-Host " [READY]" -ForegroundColor Green
} else {
    Write-Host " [TIMEOUT/ERROR]" -ForegroundColor Red
}

# 5. Start frontend
Set-Location $NpmRoot
Write-Host "Starting Next.js frontend on port $WebPort ..." -ForegroundColor Green

$frontendUrl = "http://127.0.0.1:$WebPort/"
$pollAndOpen = "for (`$i = 0; `$i -lt 60; `$i++) { try { `$null = Invoke-WebRequest -Uri '$frontendUrl' -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop; Start-Process '$frontendUrl'; exit } catch { Start-Sleep -Seconds 1 } }"
Start-Process powershell -ArgumentList "-NoProfile", "-WindowStyle", "Hidden", "-Command", $pollAndOpen

Write-Host "Browser will open automatically when frontend is ready." -ForegroundColor Gray
if ($SkipFrontend) { return }
npm run dev
