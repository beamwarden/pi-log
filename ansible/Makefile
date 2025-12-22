# ------------------------------
# Ansible Role Development Tools
# ------------------------------

ROLE_DIR=roles/pi_log
SCENARIO=default

.PHONY: lint test converge verify destroy idempotence

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
