# pi‑log Operations Guide

pi‑log is designed to run as a container on any Beamrider node.
This guide covers local development and runtime behavior.

## Local Development

### Run tests
```
make test
```

### Lint + typecheck
```
make lint
make typecheck
```

### Run locally
```
make run
```

---

## Runtime Behavior

### Startup
- loads config.toml
- initializes drivers
- starts scheduler
- opens SQLite queue
- begins ingestion loop

### Failure Modes
- driver errors are isolated
- queue is crash‑safe
- PushClient retries with backoff

---

## Deployment

Deployment is performed by **Quasar**.
pi‑log does not contain systemd units, Ansible roles, or provisioning logic.
