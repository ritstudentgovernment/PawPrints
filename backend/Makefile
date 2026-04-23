# ===== Pawprints 2.0 Makefile =====
# Common dev tasks for consistent local workflows.

# ---- Configurable variables ----
SHELL := /bin/bash
PYTHON ?= python3
SRC ?= pawprints
TESTS ?= tests
VENV ?= .venv

# Tools (override to pin versions or use Poetry/Brew paths)
RUFF ?= ruff
BLACK ?= black
PYTEST ?= pytest
PRECOMMIT ?= pre-commit
DETECT_SECRETS ?= detect-secrets

.DEFAULT_GOAL := help

.PHONY: help all bootstrap fmt lint typecheck test check precommit-install \
        secrets-scan secrets-update secrets-audit clean \
        docker-up docker-down

help:
	@echo ""
	@echo "Targets:"
	@echo "  make all               - Run fmt + lint + typecheck + test + pre-commit"
	@echo "  make bootstrap         - Create venv & install dev tools"
	@echo "  make fmt               - Format code (ruff-format)"
	@echo "  make lint              - Lint (ruff check) + basic hygiene checks"
	@echo "  make test              - Run tests with coverage"
	@echo "  make check             - Run pre-commit on all files (CI parity)"
	@echo "  make precommit-install - Install git hook locally"
	@echo "  make secrets-scan      - Preview secret findings"
	@echo "  make secrets-update    - Refresh .secrets.baseline"
	@echo "  make secrets-audit     - Interactively audit the baseline"
	@echo "  make clean             - Remove caches and build artifacts"
	@echo ""

all: fmt lint typecheck check

# ---- Environment bootstrap ----
bootstrap:
	@test -d $(VENV) || ($(PYTHON) -m venv $(VENV))
	@. $(VENV)/bin/activate && pip install -U pip wheel
	@. $(VENV)/bin/activate && pip install \
		ruff black pytest pytest-cov pre-commit detect-secrets

# ---- Formatting ----
fmt:
	@echo ">> ruff check + fix"
	@$(RUFF) check . --fix
	@echo ">> ruff format"
	@$(RUFF) format .

# ---- Linting (non-destructive) ----
lint:
	@echo ">> ruff check"
	@$(RUFF) check $(SRC)
	@echo ">> trailing whitespace / eof checks (pre-commit-hooks quick pass)"
	@$(PRECOMMIT) run trailing-whitespace --all-files || true
	@$(PRECOMMIT) run end-of-file-fixer --all-files || true

lint-fix:
	@echo ">> ruff check + auto-fix"
	@$(RUFF) check --fix $(SRC)
	@echo ">> trailing whitespace / eof fixes (pre-commit-hooks quick pass)"
	@$(PRECOMMIT) run trailing-whitespace --all-files
	@$(PRECOMMIT) run end-of-file-fixer --all-files

# # ---- Tests ----
test:
	@trap 'docker-compose down --remove-orphans' EXIT;
	@echo "Starting test database..."
	docker-compose up -d testdb
	@echo "Running tests..."
	docker-compose run --rm tests

# ---- Full repo checks (matches CI behavior) ----
check:
	@echo ">> pre-commit (all files)"
	@$(PRECOMMIT) run --all-files

# ---- Pre-commit setup ----
precommit-install:
	@echo ">> Install pre-commit hook"
	@$(PRECOMMIT) install

# ---- Secrets (detect-secrets) ----
secrets-scan:
	@echo ">> detect-secrets scan (preview)"
	@$(DETECT_SECRETS) scan --exclude-files .secrets.baseline

# Creates or refreshes .secrets.baseline based on current tree
secrets-update:
	@echo ">> Updating .secrets.baseline"
	@$(DETECT_SECRETS) scan --exclude-files .secrets.baseline > .secrets.baseline

secrets-audit:
	@echo ">> Auditing .secrets.baseline"
	@$(DETECT_SECRETS) audit .secrets.baseline

# ---- Docker (optional; remove if unused) ----
docker-up:
	@echo ">> docker compose up"
	@docker compose up -d

docker-down:
	@echo ">> docker compose down"
	@docker compose down

# ---- Cleanup ----
clean:
	@echo ">> Removing caches and build artifacts"
	@rm -rf .pytest_cache .ruff_cache .coverage htmlcov $(VENV)
	@find . -name '__pycache__' -type d -exec rm -rf {} +
	@find . -name '*.pyc' -delete
