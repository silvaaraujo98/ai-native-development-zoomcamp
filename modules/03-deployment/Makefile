BACKEND_DIR := backend
FRONTEND_DIR := frontend
BACKEND_HOST ?= 127.0.0.1
BACKEND_PORT ?= 8000
UV_CACHE_DIR := $(CURDIR)/$(BACKEND_DIR)/.uv-cache

.PHONY: help install install-backend install-frontend run backend frontend test test-backend clean

help:
	@echo "Targets:"
	@echo "  make install          Install backend and frontend dependencies"
	@echo "  make run              Run the FastAPI backend on http://$(BACKEND_HOST):$(BACKEND_PORT)"
	@echo "  make backend          Run the FastAPI backend on http://$(BACKEND_HOST):$(BACKEND_PORT)"
	@echo "  make frontend         Run the frontend on http://127.0.0.1:4173"
	@echo "  make test             Run backend tests"
	@echo "  make clean            Remove Python cache and pytest cache files"

install: install-backend install-frontend

install-backend:
	UV_CACHE_DIR=$(UV_CACHE_DIR) uv --directory $(BACKEND_DIR) sync

install-frontend:
	cd $(FRONTEND_DIR) && npm install

run: backend

backend:
	UV_CACHE_DIR=$(UV_CACHE_DIR) uv --directory $(BACKEND_DIR) run python -m uvicorn app.main:app --reload --host $(BACKEND_HOST) --port $(BACKEND_PORT)

frontend:
	cd $(FRONTEND_DIR) && npm run dev

test: test-backend

test-backend:
	UV_CACHE_DIR=$(UV_CACHE_DIR) uv --directory $(BACKEND_DIR) run python -m pytest

clean:
	UV_CACHE_DIR=$(UV_CACHE_DIR) uv --directory $(BACKEND_DIR) run python -c "import pathlib, shutil; [shutil.rmtree(p) for p in pathlib.Path('.').rglob('__pycache__')]; shutil.rmtree('.pytest_cache', ignore_errors=True)"
