# pi‑log Troubleshooting

## Common Issues

### Sensor not producing data
- check driver configuration
- check device permissions (`/dev/tty*`, `/dev/i2c-*`)
- check container runtime flags

### Push failures
- verify Beamwarden URL
- verify device token
- check network connectivity

### Queue growth
- Beamwarden unreachable
- PushClient retrying
- inspect logs

---

## Logs

Use the container runtime to inspect logs:

```
docker logs -f pi-log
```

---

## Deployment Issues

Deployment is handled by **Quasar**.
If deployment fails, check Quasar logs and playbooks.
