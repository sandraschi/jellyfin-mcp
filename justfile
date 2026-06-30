set windows-shell := ["pwsh.exe", "-NoLogo", "-Command"]
import 'scripts/just/fleet.just'

# jellyfin-mcp Project Management

default:
    @just --list

version:
    @uv run python -c "import pathlib, tomllib; p = pathlib.Path('pyproject.toml'); print(tomllib.loads(p.read_text(encoding='utf-8'))['project']['version'])"

# --- Basic Workflow ---

install:
    uv sync
    pre-commit install

start:
    uv run jellyfin-mcp

webapp:
    @powershell -ExecutionPolicy Bypass -File webapp/start.ps1

# --- Quality Gates ---

lint:
    @echo "--- Checking Python (Ruff) ---"
    ruff check .
    @echo "--- Checking JS/TS (Biome) ---"
    cd webapp/frontend && npx @biomejs/biome check .

fix:
    ruff check . --fix
    ruff format .
    cd webapp/frontend && npx @biomejs/biome check --write .

fmt:
    ruff format .
    cd webapp/frontend && npx @biomejs/biome format --write .

test:
    @pytest tests/ -v -m "not slow"

test-all:
    @pytest tests/ -v

test-unit:
    @pytest tests/unit -v

test-integration:
    @pytest tests/integration -v -m "integration and not slow"

test-slow:
    @pytest tests/integration/test_rag.py -v -m slow

e2e:
    Set-Location webapp/frontend
    npx playwright install chromium
    npx playwright test

e2e-ui:
    Set-Location webapp/frontend
    npx playwright test --ui

e2e-headed:
    Set-Location webapp/frontend
    npx playwright test --headed

e2e-serve:
    Set-Location webapp/frontend
    npx playwright test -g "@noop"

ci: lint test

# --- Build & Clean ---

build:
    @echo "Building jellyfin-mcp package"
    @echo "Done"

build-native:
    Set-Location '{{justfile_directory()}}\native'
    $env:Path = "$env:USERPROFILE\.cargo\bin;$env:Path"
    .\build.ps1

build-native-debug:
    Set-Location '{{justfile_directory()}}\native'
    $env:Path = "$env:USERPROFILE\.cargo\bin;$env:Path"
    npx @tauri-apps/cli build --debug

tauri-sidecar:
    pwsh -NoLogo -File '{{justfile_directory()}}\native\build-sidecar.ps1'

tauri-build:
    Set-Location '{{justfile_directory()}}\native'
    $env:Path = "$env:USERPROFILE\.cargo\bin;$env:Path"
    .\build.ps1

tauri-dev:
    Set-Location '{{justfile_directory()}}\native'
    $env:Path = "$env:USERPROFILE\.cargo\bin;$env:Path"
    npm install
    npx @tauri-apps/cli dev

# Run CUA smoke test against installed NSIS app
cua-nsis-test:
    C:\Windows\py.exe scripts/cua-smoke.py

clean:
    @powershell -Command "Remove-Item -Recurse -Force .pytest_cache, .ruff_cache, dist, build, htmlcov -ErrorAction SilentlyContinue"
    @powershell -Command "Get-ChildItem -Path . -Recurse -Directory -Filter __pycache__ -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue"
