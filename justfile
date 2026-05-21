set windows-shell := ["pwsh.exe", "-NoLogo", "-Command"]

# jellyfin-mcp Project Management

default:
    @pwsh.exe -NoProfile -ExecutionPolicy Bypass -File ../mcp-central-docs/scripts/just-dashboard.ps1 -Path .

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
    @pytest --cov=src/jellyfin_mcp tests/ -v

e2e:
    cd webapp/frontend && npx playwright test

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

clean:
    @powershell -Command "Remove-Item -Recurse -Force .pytest_cache, .ruff_cache, dist, build, htmlcov -ErrorAction SilentlyContinue"
    @powershell -Command "Get-ChildItem -Path . -Recurse -Directory -Filter __pycache__ -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue"
