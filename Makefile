PI_HOST=beamrider-0001.local
PI_USER=jeb

help: ## Show help
	@echo ""
	@echo "Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?##' Makefile | sed 's/:.*##/: /' | column -t -s ':'
	@echo ""

.PHONY: venv install freeze test lint run \
		check-ansible deploy restart logs db-shell \
		ping hosts ssh doctor clean reset-pi \
		pi-status pi-journal \
		lint converge verify destroy test idempotence

# -------------------------------------------------------------------
# Python environment
# -------------------------------------------------------------------

venv: ## Create Python virtual environment
	python3 -m venv .venv

install: venv ## Install Python dependencies
	.venv/bin/pip install -r requirements.txt

freeze: ## Freeze dependencies to requirements.txt
	.venv/bin/pip freeze > requirements.txt

# -------------------------------------------------------------------
# Local development
# -------------------------------------------------------------------

check-venv:
	@test -n "$$VIRTUAL_ENV" || (echo "ERROR: .venv not activated"; exit 1)

test: check-venv install ## Run application test suite (CI parity)
	.venv/bin/pytest

lint: ## Run flake8 + black checks
	.venv/bin/flake8 app
	.venv/bin/black --check app

run: ## Run ingestion loop locally
	.venv/bin/python -m app.ingestion_loop

# -------------------------------------------------------------------
# Deployment to Raspberry Pi (via Ansible)
# -------------------------------------------------------------------

check-ansible: ## Validate Ansible syntax, inventory, lint, and dry-run
	ansible-playbook -i ansible/inventory.ini ansible/deploy.yml --syntax-check
	ansible-inventory -i ansible/inventory.ini --list >/dev/null
	ansible-lint ansible/
	ansible-playbook -i ansible/inventory.ini ansible/deploy.yml --check

deploy: ## Deploy to Raspberry Pi via Ansible
	ansible-playbook -i ansible/inventory.ini ansible/deploy.yml

restart: ## Restart pi-log service on the Pi
	ansible pi1 -i ansible/inventory.ini -m systemd -a "name=pi-log state=restarted"

logs: ## Tail ingestion logs on the Pi
	ssh $(PI_USER)@$(PI_HOST) "sudo journalctl -u pi-log -n 50"

db-shell: ## Open SQLite shell on the Pi
	ssh $(PI_USER)@$(PI_HOST) "sudo sqlite3 /opt/pi-log/readings.db"

ping: ## Ping the Raspberry Pi via Ansible
	ansible pi1 -i ansible/inventory.ini -m ping

hosts: ## Show parsed Ansible inventory
	ansible-inventory -i ansible/inventory.ini --list

ssh: ## SSH into the Raspberry Pi
	ssh $(PI_USER)@$(PI_HOST)

# -------------------------------------------------------------------
# Pi health + maintenance
# -------------------------------------------------------------------

doctor: ## Run full environment + Pi health checks
	@echo "Checking Python..."
	@python3 --version
	@echo ""

	@echo "Checking virtual environment..."
	@[ -d ".venv" ] && echo "venv OK" || echo "venv missing"
	@echo ""

	@echo "Checking Python dependencies..."
	@.venv/bin/pip --version
	@echo ""

	@echo "Checking Ansible..."
	@ansible --version
	@ansible-inventory -i ansible/inventory.ini --list >/dev/null && echo "Inventory OK"
	@echo ""

	@echo "Checking SSH connectivity..."
	@ssh -o BatchMode=yes -o ConnectTimeout=5 $(PI_USER)@$(PI_HOST) "echo SSH OK" || echo "SSH FAILED"
	@echo ""

	@echo "Checking systemd service..."
	@ssh $(PI_USER)@$(PI_HOST) "systemctl is-active pi-log" || true

clean: ## Remove virtual environment and Python cache files
	rm -rf .venv
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

reset-pi: ## Wipe /opt/pi-log on the Pi and redeploy
	ssh $(PI_USER)@$(PI_HOST) "sudo systemctl stop pi-log || true"
	ssh $(PI_USER)@$(PI_HOST) "sudo rm -rf /opt/pi-log/*"
	ansible-playbook -i ansible/inventory.ini ansible/deploy.yml
	ssh $(PI_USER)@$(PI_HOST) "sudo systemctl restart pi-log"

# -------------------------------------------------------------------
# Systemd inspection
# -------------------------------------------------------------------

pi-status: ## Show pi-log systemd status
	ssh $(PI_USER)@$(PI_HOST) "systemctl status pi-log"

pi-journal: ## Follow pi-log journal output
	ssh $(PI_USER)@$(PI_HOST) "journalctl -u pi-log -f"

# -------------------------------------------------------------------
# Patch utilities
# -------------------------------------------------------------------

apply-patch: ## Apply a patch from patches/ by name: make apply-patch FILE=20251223-ingestion-refactor.patch
	@if [ -z "$(FILE)" ]; then \
		echo "ERROR: You must specify FILE=<YYYYMMDD-slug.patch>"; \
		exit 1; \
	fi
	git apply patches/$(FILE)

diff: ## Generate a patch of uncommitted changes into patches/YYYYMMDD-changes.patch
	@mkdir -p patches
	@ts=$$(date +"%Y%m%d"); \
		git diff > patches/$$ts-changes.patch; \
		echo "Created patches/$$ts-changes.patch"

# -------------------------------------------------------------------
# Release utilities
# -------------------------------------------------------------------

release: ## Usage: make release VERSION=0.1.1
	@if [ -z "$(VERSION)" ]; then \
		echo "ERROR: You must specify VERSION=X.Y.Z"; \
		exit 1; \
	fi
	@echo "Bumping version to $(VERSION)"
	sed -i '' "s/^version:.*/version: $(VERSION)/" galaxy.yml
	git add galaxy.yml
	git commit -m "Release v$(VERSION)"
	git tag v$(VERSION)
	git push
	git push --tags
	@echo "Release v$(VERSION) pushed. GitHub Actions will publish to Galaxy."

.PHONY: deploy
deploy:
	cd ansible && make deploy
