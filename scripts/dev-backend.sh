#!/usr/bin/env bash
# Runs the JewelMind backend locally without Docker (Linux/macOS/Git Bash).
# Creates backend/.venv on first run if it doesn't exist yet.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$REPO_ROOT/backend/.venv"

if [ ! -d "$VENV_DIR" ]; then
  echo "Creating backend/.venv ..."
  python3 -m venv "$VENV_DIR"
  "$VENV_DIR/bin/pip" install --upgrade pip
  "$VENV_DIR/bin/pip" install -r "$REPO_ROOT/backend/requirements.txt"
fi

cd "$REPO_ROOT/backend"
exec "$VENV_DIR/bin/python" -m uvicorn jewelmind.api.app:app --reload --host 0.0.0.0 --port 8000
