.PHONY: help backend-install backend-test backend-lint backend-run \
        frontend-install frontend-test frontend-lint frontend-build frontend-dev \
        test lint docker-up docker-down

help:
	@echo "JewelMind — common developer commands"
	@echo "  make backend-install   Create backend/.venv and install dependencies"
	@echo "  make backend-test      Run backend pytest suite"
	@echo "  make backend-lint      Run ruff over the backend"
	@echo "  make backend-run       Run the backend with uvicorn (reload)"
	@echo "  make frontend-install  npm install in frontend/"
	@echo "  make frontend-test     Run frontend vitest suite"
	@echo "  make frontend-lint     Run oxlint over the frontend"
	@echo "  make frontend-build    Type-check and build the frontend"
	@echo "  make frontend-dev      Run the Vite dev server"
	@echo "  make test              Run backend and frontend test suites"
	@echo "  make lint               Run backend and frontend linters"
	@echo "  make docker-up          docker compose up --build"
	@echo "  make docker-down        docker compose down"

backend-install:
	python -m venv backend/.venv
	backend/.venv/bin/pip install --upgrade pip
	backend/.venv/bin/pip install -r backend/requirements.txt

backend-test:
	cd backend && .venv/bin/python -m pytest -q

backend-lint:
	cd backend && .venv/bin/python -m ruff check .

backend-run:
	cd backend && .venv/bin/python -m uvicorn jewelmind.api.app:app --reload --host 0.0.0.0 --port 8000

frontend-install:
	cd frontend && npm install

frontend-test:
	cd frontend && npm run test

frontend-lint:
	cd frontend && npm run lint

frontend-build:
	cd frontend && npm run build

frontend-dev:
	cd frontend && npm run dev

test: backend-test frontend-test

lint: backend-lint frontend-lint

docker-up:
	docker compose up --build

docker-down:
	docker compose down
