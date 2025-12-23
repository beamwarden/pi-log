# Deployment

## Requirements

- Raspberry Pi OS
- Python 3
- Systemd
- Ansible on the control machine

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
