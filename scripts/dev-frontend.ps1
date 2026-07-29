# Runs the JewelMind frontend dev server locally without Docker (Windows PowerShell).
$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$frontendDir = Join-Path $repoRoot "frontend"

if (-not (Test-Path (Join-Path $frontendDir "node_modules"))) {
    Write-Host "Installing frontend dependencies ..."
    npm --prefix $frontendDir install
}

npm --prefix $frontendDir run dev
