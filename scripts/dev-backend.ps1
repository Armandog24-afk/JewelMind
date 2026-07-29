# Runs the JewelMind backend locally without Docker (Windows PowerShell).
# Creates backend/.venv on first run if it doesn't exist yet.
$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$venvPython = Join-Path $repoRoot "backend\.venv\Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
    Write-Host "Creating backend/.venv ..."
    python -m venv (Join-Path $repoRoot "backend\.venv")
    & $venvPython -m pip install --upgrade pip
    & $venvPython -m pip install -r (Join-Path $repoRoot "backend\requirements.txt")
}

& $venvPython -m uvicorn jewelmind.api.app:app --reload --host 0.0.0.0 --port 8000 --app-dir (Join-Path $repoRoot "backend")
