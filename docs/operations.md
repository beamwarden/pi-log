# Pi‑Log Operations Guide

This document provides the essential operational knowledge for running,
monitoring, and maintaining the Pi‑Log ingestion service on a Raspberry Pi.
It is written for maintainers who need fast, reliable procedures without
digging through code or playbooks.

---

# 1. Overview

Pi‑Log is a systemd‑managed ingestion service that:

- reads Geiger counter data from a serial device,
- stores readings in a local SQLite database,
- optionally pushes data to external APIs (LogExp, custom endpoints),
- exposes logs via journald and rotating log files,
- is deployed and updated via Ansible.

This guide covers day‑to‑day operations, debugging, and verification.

---

# 2. Service Management

All service control is done through systemd.

## Start the service
```bash
sudo systemctl start pi-log.service
```
## Stop the service
```bash
sudo systemctl stop pi-log.service
```
## Restart the service
```bash
sudo systemctl restart pi-log.service
```
## Check service status
```bash
sudo systemctl status pi-log.service
```
## Reload systemd after updating the unit file
```bash
sudo systemctl daemon-reload
```
## Check if the service is running
```bash
systemctl is-active pi-log.service
```
## Check if the service is enabled at boot
```bash
systemctl is-enabled pi-log.service
```
---
# 3. Logs & Monitoring
Pi‑Log uses:

* journald for live operational logs,
* rotating file logs at `/opt/pi-log/logs/pi-log.log`.

## View last 50 log lines
```bash
journalctl -u pi-log.service -n 50
```

## Follow logs live
```bash
journalctl -u pi-log.service -f
```

## View logs since last boot
```bash
journalctl -u pi-log.service -b
```

## View rotating file logs
```bash
tail -n 50 /opt/pi-log/logs/pi-log.log
```
---
# 4. Database Inspection

The ingestion database lives at: `/var/lib/pi-log/readings.db`

## Count total readings
```bash
sqlite3 /var/lib/pi-log/readings.db 'SELECT COUNT(*) FROM readings;'
```

## Show last 5 readings
```bash
sqlite3 /var/lib/pi-log/readings.db 'SELECT * FROM readings ORDER BY id DESC LIMIT 5;'
```
# 5. Serial Device Verification
Check that the Geiger counter is detected:
```bash
ls -l /dev/ttyUSB*
```
If no device appears:
* check cabling,
* check power,
* check USB port,
* check that the device is not claimed by another service.
---
# 6. End‑to‑End Ingestion Test
Inject a synthetic reading (for testing only):
```bash
echo 'CPS,17,1,0.09,SLOW,0' | sudo tee /dev/ttyUSB0
```
Then verify:
* logs show ingestion,
* DB count increases,
* optional push endpoints receive data.
---
# 7. Deployment Workflow (Ansible)

All deployments are done from the `ansible/` directory.
## Deploy the latest code
```bash
make deploy
```
This performs:
* repo → role sync,
* application copy,
* config deployment,
* logging config deployment,
* systemd reload,
* service restart.

## Restart the service via Ansible
```bash
make restart
```

## View logs via Ansible
```bash
make logs
```

## Follow logs live via Ansible
```bash
make tail
```
---
# 8. Real‑Time Monitoring
```bash
journalctl -u pi-log.service -f & \
watch -n 2 'sqlite3 /var/lib/pi-log/readings.db "SELECT COUNT(*) FROM readings;"'
```
This is the fastest way to confirm the ingestion loop is alive.
---
# 9. Directory Layout
```t
/opt/pi-log/
    app/                # deployed application code
    logs/               # rotating log files
    config.toml         # ingestion configuration

/var/lib/pi-log/
    readings.db         # ingestion database

/etc/systemd/system/
    pi-log.service      # systemd unit file
```
---
# 10. Troubleshooting
## Service starts then exits immediately
* Check `/opt/pi-log/app/ingestion_loop.py` for truncated or stale code.
* Ensure `make deploy` was used (syncs repo → role).
* Confirm systemd unit uses:
```bash
StandardOutput=journal
StandardError=journal
```
## No logs in journald
* Systemd unit may still be using `append:` redirection.
* Redeploy with updated template.

## DB not updating
* Check serial device availability.
* Check logs for parsing errors.
* Confirm ingestion loop is running (`make tail`).
---
# 11. Contact & Ownership

This project is maintained by the repo owner.
All operational changes should be documented in this file and reflected in the Ansible role.
