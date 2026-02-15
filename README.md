# pi‑log — Portable Multi‑Sensor Logging Hub

pi‑log is a **containerized, hardware‑agnostic ingestion hub** for Beamrider nodes.
It collects readings from any number of sensors (serial, I²C, SPI, USB, network, or virtual), stores them locally, and pushes structured telemetry to Beamwarden.

pi‑log is:
- **Portable** — runs on ARM, x86, Pi, Jetson, NUC, VMs, industrial gateways
- **Extensible** — sensor drivers are modular Python plugins
- **Deterministic** — every reading is typed, timestamped, and validated
- **Reliable** — local queueing, WAL mode, crash‑safe
- **Fleet‑managed** — deployed and configured by Quasar

---

## Features

### Multi‑Sensor Support
pi‑log supports any number of sensors simultaneously:
- Serial devices
- I²C/SPI peripherals
- USB HID
- Network sensors (TCP, UDP, MQTT, HTTP)
- Virtual/software sensors

### Unified Ingestion Schema
All readings follow the same structure:

```json
{
  "device_id": "beamrider-0001",
  "sensor_type": "bme280",
  "payload": { "temperature_c": 22.4 },
  "timestamp": "2026-02-15T19:06:00Z"
}
```

### Local Queue (SQLite)
- WAL mode
- bounded
- crash‑safe
- replay on restart

### Container‑First
pi‑log is distributed as a single container image:

```
docker run -d \
  --name pi-log \
  --device /dev/ttyUSB0 \
  -v /etc/pi-log/config.toml:/app/config.toml:ro \
  ghcr.io/beamwarden/pi-log:latest
```

---

## Configuration

pi‑log is configured via `config.toml`:

```toml
device_id = "beamrider-0001"
api_url = "http://keep-0001.local:8000/api/readings"
device_token = "..."

[[sensor]]
type = "mightyohm"
driver = "app.sensors.mightyohm:MightyOhmDriver"
interval_ms = 1000

[[sensor]]
type = "tcp-json"
driver = "app.sensors.tcp_json:TCPJSONDriver"
host = "192.168.1.50"
port = 9000
```

---

## Development

### Create a venv
```
make dev
```

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

## Building the Container

```
make build
make push
```

---

## Deployment

Deployment is handled by **Quasar**, the Beamwarden fleet control plane.
pi‑log itself contains **no infrastructure code**.

---

## License

TBD
