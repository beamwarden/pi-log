# filename: Makefile
# ========================================================================
# Beamwarden pi-log — Unified Makefile (Application Only)
# Python Dev • Local Ingestion • Docker Build/Push • Pi Ops via Quasar
# ========================================================================

# ------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------

PI_HOST        := beamrider-0001.local
PI_USER        := jeb
SERVICE        := pi-log

IMAGE          := ghcr.io/beamwarden/pi-log
TAG            := latest

PYTHON         := /opt/homebrew/bin/python3.12
VENV           := .venv

# ------------------------------------------------------------------------
# Help
# ------------------------------------------------------------------------

help: ## Show help
	@echo ""
	@echo "Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?##' Makefile | sed 's/:.*##/: /' | column -t -s ':'
	@echo ""

.PHONY: help

# ------------------------------------------------------------------------
# Python Environment
# ------------------------------------------------------------------------

dev: ## Full local dev bootstrap (fresh venv + deps + sanity checks)
	rm -rf $(VENV)
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r requirements.txt
	$(VENV)/bin/python3 --version
	$(VENV)/bin/python3 -c "import app, pytest, requests; print('Imports OK')"
	@echo ""
	@echo "✔ Development environment ready"
	@echo "Activate with: source $(VENV)/bin/activate"

bootstrap: ## Create venv and install dependencies (first-time setup)
	rm -rf $(VENV)
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r requirements.txt

install: check-venv ## Install dependencies into existing venv
	$(VENV)/bin/pip install -r requirements.txt

freeze: ## Freeze dependencies to requirements.txt
	$(VENV)/bin/pip freeze > requirements.txt

check-venv:
	@test -n "$$VIRTUAL_ENV" || (echo "ERROR: .venv not activated"; exit 1)

clean-pyc:
	find . -type d -name "__pycache__" -exec rm -rf {} +

clean: ## Remove venv + Python cache files
	rm -rf $(VENV)
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# ------------------------------------------------------------------------
# Local Ingestion Agent (run.py + config.toml)
# ------------------------------------------------------------------------

run: check-venv ## Run ingestion agent locally
	$(VENV)/bin/python run.py

dev-run: run ## Alias for local ingestion run

health: ## Curl the local health endpoint
	curl -s http://localhost:8080/health | jq .

# ------------------------------------------------------------------------
# Linting, Type Checking, Tests
# ------------------------------------------------------------------------

lint: check-venv ## Run ruff lint + format check
	$(VENV)/bin/ruff check .
	$(VENV)/bin/ruff format --check .

typecheck: check-venv ## Run mypy type checking
	$(VENV)/bin/mypy app

test: check-venv ## Run pytest suite
	$(VENV)/bin/pytest -q

ci: clean-pyc check-venv ## Full local CI (lint + typecheck + tests)
	$(VENV)/bin/ruff check .
	$(VENV)/bin/mypy .
	$(VENV)/bin/pytest -q
	@echo ""
	@echo "✔ Local CI passed"

# ------------------------------------------------------------------------
# Docker Build + Push + Release
# ------------------------------------------------------------------------

build: ## Build the pi-log container image
	docker build -t $(IMAGE):$(TAG) .

push: ## Push the container image to GHCR
	docker push $(IMAGE):$(TAG)

publish: build push ## Build and push the container image
	@echo "✔ Image built and pushed to GHCR"

# Release is now build+push only; deployment is Quasar's job
release: publish ## Full release (container only)
	@echo "✔ Container release completed"

run-container: ## Run the container locally (binds config.toml + serial)
	docker run --rm -it \
		--device /dev/ttyUSB0 \
		--volume $(PWD)/config.toml:/app/config.toml:ro \
		$(IMAGE):$(TAG)

logs-container: ## Tail logs from a locally running container
	docker logs -f pi-log

# ------------------------------------------------------------------------
# Pi Service Management (via SSH)
# ------------------------------------------------------------------------

restart: ## Restart pi-log service on the Pi
	ssh $(PI_USER)@$(PI_HOST) "sudo systemctl restart $(SERVICE)"

start: ## Start pi-log service
	ssh $(PI_USER)@$(PI_HOST) "sudo systemctl start $(SERVICE)"

stop: ## Stop pi-log service
	ssh $(PI_USER)@$(PI_HOST) "sudo systemctl stop $(SERVICE)"

status: ## Show pi-log systemd status
	ssh $(PI_USER)@$(PI_HOST) "systemctl status $(SERVICE)"

logs: ## Show last 50 log lines from the Pi
	ssh $(PI_USER)@$(PI_HOST) "sudo journalctl -u $(SERVICE) -n 50"

tail: ## Follow live logs from the Pi
	ssh $(PI_USER)@$(PI_HOST) "sudo journalctl -u $(SERVICE) -f"

db-shell: ## Open SQLite shell on the Pi
	ssh $(PI_USER)@$(PI_HOST) "sudo sqlite3 /var/lib/pi-log/readings.db"

# ------------------------------------------------------------------------
# Pi Health + Maintenance
# ------------------------------------------------------------------------

ping: ## Ping the Raspberry Pi
	ssh $(PI_USER)@$(PI_HOST) "echo ping"

ssh: ## SSH into the Raspberry Pi
	ssh $(PI_USER)@$(PI_HOST)

doctor: ## Full environment + Pi health checks
	@echo "Checking Python..."; python3 --version; echo ""
	@echo "Checking virtual environment..."; \
		[ -d ".venv" ] && echo "venv OK" || echo "venv missing"; echo ""
	@echo "Checking SSH connectivity..."; \
		ssh -o BatchMode=yes -o ConnectTimeout=5 $(PI_USER)@$(PI_HOST) "echo SSH OK" || echo "SSH FAILED"; echo ""
	@echo "Checking systemd service..."; \
		ssh $(PI_USER)@$(PI_HOST) "systemctl is-active $(SERVICE)" || true
