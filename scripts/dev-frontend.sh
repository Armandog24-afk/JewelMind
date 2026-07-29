#!/usr/bin/env bash
# Runs the JewelMind frontend dev server locally without Docker.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="$REPO_ROOT/frontend"

if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
  echo "Installing frontend dependencies ..."
  npm --prefix "$FRONTEND_DIR" install
fi

npm --prefix "$FRONTEND_DIR" run dev
