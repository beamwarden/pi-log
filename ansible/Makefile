# ----------------------------------------
# Ansible Deployment & Role Dev Makefile
# ----------------------------------------

INVENTORY=inventory.ini
PLAYBOOK=deploy.yml
ROLE_DIR=roles/pi_log
SCENARIO=default
SERVICE=pi-log.service

.PHONY: deploy restart logs tail status lint test converge verify destroy idempotence

# -------------------------
# Deployment Commands
# -------------------------

deploy: sync-app
	ansible-playbook -i $(INVENTORY) $(PLAYBOOK) --tags pi_log --diff

restart:
	ansible -i $(INVENTORY) all -m systemd -a "name=$(SERVICE) state=restarted"

status:
	ansible -i $(INVENTORY) all -m systemd -a "name=$(SERVICE) state=started"

logs:
	ansible -i $(INVENTORY) all -m shell -a "journalctl -u $(SERVICE) -n 50"

tail:
	ansible -i $(INVENTORY) all -m shell -a "journalctl -u $(SERVICE) -f"

# -------------------------
# Role Development (Molecule)
# -------------------------

lint:
	ansible-lint $(ROLE_DIR)

converge:
	cd $(ROLE_DIR) && molecule converge -s $(SCENARIO)

verify:
	cd $(ROLE_DIR) && molecule verify -s $(SCENARIO)

destroy:
	cd $(ROLE_DIR) && molecule destroy -s $(SCENARIO)

test:
	cd $(ROLE_DIR) && molecule test -s $(SCENARIO)

idempotence:
	cd $(ROLE_DIR) && molecule converge -s $(SCENARIO)
	cd $(ROLE_DIR) && molecule idempotence -s $(SCENARIO)

# ----------------------------------------
# Sync repo app → Ansible role
# ----------------------------------------

ROLE_APP_DIR=roles/pi_log/files/app
REPO_APP_DIR=../app

.PHONY: sync-app sync-check

sync-app:
	@echo "🔄 Syncing repo app → role..."
	rm -rf $(ROLE_APP_DIR)
	mkdir -p $(ROLE_APP_DIR)
	cp -r $(REPO_APP_DIR)/* $(ROLE_APP_DIR)/
	@echo "✅ Sync complete."

sync-check:
	@echo "📂 Checking role app directory..."
	ls -l $(ROLE_APP_DIR)

# ----------------------------------------
# Systemctl wrappers (run via Ansible)
# ----------------------------------------

SERVICE=pi-log.service
INVENTORY=inventory.ini

.PHONY: restart status logs tail stop start

start:
	ansible -i $(INVENTORY) all -m systemd -a "name=$(SERVICE) state=started"

stop:
	ansible -i $(INVENTORY) all -m systemd -a "name=$(SERVICE) state=stopped"

restart:
	ansible -i $(INVENTORY) all -m systemd -a "name=$(SERVICE) state=restarted"

status:
	ansible -i $(INVENTORY) all -m systemd -a "name=$(SERVICE) state=started"

logs:
	ansible -i $(INVENTORY) all -m shell -a "journalctl -u $(SERVICE) -n 50"

tail:
	ansible -i $(INVENTORY) all -m shell -a "journalctl -u $(SERVICE) -f"
