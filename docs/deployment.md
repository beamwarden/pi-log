# Deployment

## Requirements

- Raspberry Pi OS
- Python 3
- Systemd

## Deploy

```bash
make deploy
```

## Restart service

```bash
make restart
```

## Logs

```bash
make logs
```

## Database

```bash
make db-shell
```

## Service File

`pi-log.service` is managed by Ansible and includes:

- WorkingDirectory=/opt/pi-log
- ExecStartPre=/bin/sleep 5
- ExecStart=/usr/bin/python3 -m app.ingestion_loop
- Logging to /opt/pi-log/logs

# Pi‑Log Deployment & Operations Cheat‑Sheet

This page documents the essential commands for deploying, managing, and debugging
the `pi-log` ingestion service on a Raspberry Pi.

---

## 🚀 Deployment

From the repo root:

```bash
make deploy
```

This performs:

- repo → role sync
- Ansible deploy
- systemd reload
- service restart

---

## 🔧 Service Management (systemctl)

Run these on the Pi or via Ansible:

### Start the service
```bash
sudo systemctl start pi-log.service
```

### Stop the service
```bash
sudo systemctl stop pi-log.service
```

### Restart the service
```bash
sudo systemctl restart pi-log.service
```

### Reload systemd after updating the unit file
```bash
sudo systemctl daemon-reload
```

### Check service status
```bash
sudo systemctl status pi-log.service
```

### Check if the service is running
```bash
systemctl is-active pi-log.service
```

### Check if the service is enabled at boot
```bash
systemctl is-enabled pi-log.service
```

---

## 📜 Logs (journalctl)

### Show last 50 log lines
```bash
journalctl -u pi-log.service -n 50
```

### Follow logs live
```bash
journalctl -u pi-log.service -f
```

### Show logs since last boot
```bash
journalctl -u pi-log.service -b
```

---

## 🗄️ Database Inspection

### Count readings
```bash
sqlite3 /var/lib/pi-log/readings.db 'SELECT COUNT(*) FROM readings;'
```

### Show last 5 readings
```bash
sqlite3 /var/lib/pi-log/readings.db 'SELECT * FROM readings ORDER BY id DESC LIMIT 5;'
```

---

## 🧪 End‑to‑End Test

Inject a fake reading (if using a USB serial device):

```bash
echo 'CPS,17,1,0.09,SLOW,0' | sudo tee /dev/ttyUSB0
```

Then check logs + DB to confirm ingestion.

---
