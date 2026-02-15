# Pi‑Log v2 — Portable, Containerized Multi‑Sensor Logging Hub

Pi‑Log v2 is no longer tied to Raspberry Pi hardware. It becomes a **portable, containerized ingestion substrate** capable of running on any Beamrider node — physical, virtual, ARM, x86, Pi, Jetson, NUC, or cloud edge.

Pi‑Log v2 is the universal logging hub for the Beam ecosystem:
- **Multi‑sensor**
- **Hardware‑agnostic**
- **Container‑first**
- **Extensible via drivers**
- **Deterministic and typed**
- **Managed by Quasar**

This architecture allows any Beamrider to host any number of sensor arrays and push structured telemetry to Beamwarden.

---

## 1. High‑Level Architecture

```
+------------------------------------------------------+
|                    Beamrider Node                    |
|        (Linux host: Pi, Jetson, NUC, VM, etc.)       |
+------------------------------------------------------+
|                 pi-log Container (v2)                |
+------------------------------------------------------+
|  Sensor Drivers (plugins)                            |
|    - Serial sensors                                  |
|    - I2C/SPI sensors                                 |
|    - USB sensors                                     |
|    - Network sensors (MQTT, TCP, HTTP)               |
|    - Virtual sensors (software-only)                 |
+------------------------------------------------------+
|  Sensor Scheduler                                    |
|    - polling intervals                               |
|    - event/interrupt hooks                           |
|    - network subscription                            |
+------------------------------------------------------+
|  Local Queue (SQLite, WAL mode)                      |
|    - crash-safe                                      |
|    - bounded                                         |
|    - replay on restart                               |
+------------------------------------------------------+
|  PushClient                                          |
|    - unified payload                                 |
|    - retries/backoff                                 |
|    - identity headers                                |
+------------------------------------------------------+
|  Beamwarden API                                      |
+------------------------------------------------------+
```

Pi‑Log v2 is a **platform**, not a device agent.

---

## 2. Sensor Driver Model (Hardware‑Agnostic)

Drivers are modular Python components that can run anywhere the container runs.

### Driver Interface

```python
class SensorDriver:
    sensor_type: str
    config: dict

    def read(self) -> SensorReading:
        ...
```

### SensorReading

```python
class SensorReading(BaseModel):
    sensor_type: str
    payload: dict
    timestamp: datetime
```

Drivers may read from:
- `/dev/tty*` (serial)
- `/dev/i2c-*` or `/dev/spidev*`
- USB HID
- network endpoints
- shared memory
- virtual sources

Pi‑log does not care — it only cares that the driver produces a typed reading.

---

## 3. Sensor Scheduler

The scheduler orchestrates all drivers:

- polling intervals
- event‑driven reads
- network subscriptions
- isolation (one driver cannot crash the hub)
- backpressure handling

Example config:

```toml
[[sensor]]
type = "mightyohm"
driver = "app.sensors.mightyohm:MightyOhmDriver"
interval_ms = 1000

[[sensor]]
type = "bme280"
driver = "app.sensors.bme280:BME280Driver"
interval_ms = 5000

[[sensor]]
type = "tcp-json"
driver = "app.sensors.tcp_json:TCPJSONDriver"
host = "192.168.1.50"
port = 9000
```

---

## 4. Local Queue (SQLite)

A single table stores all readings:

```
readings (
    id INTEGER PRIMARY KEY,
    sensor_type TEXT,
    payload JSON,
    timestamp TEXT,
    device_id TEXT,
    pushed INTEGER
)
```

Features:
- WAL mode
- bounded queue
- crash‑safe
- replay on restart
- future: partitioning, batching

---

## 5. PushClient (Unified Ingestion)

Every reading is pushed using the same schema:

```json
{
  "device_id": "beamrider-0001",
  "sensor_type": "bme280",
  "payload": {
      "temperature_c": 22.4,
      "humidity_pct": 41.2
  },
  "timestamp": "2026-02-15T19:06:00Z"
}
```

PushClient responsibilities:
- identity headers
- retries + exponential backoff
- marking rows as pushed
- batching (future)

---

## 6. Beamwarden v2 Ingestion Contract

Beamwarden receives **typed sensor readings**, not device‑specific schemas.

### ReadingCreate schema:

```json
{
  "device_id": "string",
  "sensor_type": "string",
  "payload": { "arbitrary": "json" },
  "timestamp": "ISO8601"
}
```

### Backend model:

```
Node
  └── Sensor (type)
        └── Readings (JSON payload)
```

This is stable, future‑proof, and supports arbitrary sensor arrays.

---

## 7. Configuration v2 (config.toml)

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

Drivers are dynamically imported.

---

## 8. Containerization Strategy

Pi‑log v2 is distributed as a **single container image**:

- Python 3.12
- all core drivers included
- optional drivers installed via plugin mechanism
- config.toml mounted at runtime
- `/dev` passthrough optional
- network sensors require no host access

### Example runtime:

```
docker run -d \
  --name pi-log \
  --device /dev/ttyUSB0 \
  -v /etc/pi-log/config.toml:/app/config.toml:ro \
  ghcr.io/beamwarden/pi-log:latest
```

This works on:
- Raspberry Pi
- Jetson Nano
- x86 NUC
- cloud VMs
- industrial gateways
- anything that runs Docker or Podman

---

## 9. Future Extensions

- hot‑pluggable drivers
- driver discovery (I²C, SPI, USB enumeration)
- network sensor autodiscovery
- batching + compression
- edge analytics (thresholds, alarms, local aggregation)
- multi‑container sensor stacks

---

## 10. Summary

Pi‑Log v2 is a **portable, containerized, multi‑sensor ingestion hub**:

- hardware‑agnostic
- extensible
- deterministic
- container‑first
- fleet‑managed via Quasar
- upstreamed into Beamwarden via a unified schema

This architecture positions Beamwarden to ingest any sensor data from any device footprint, without schema churn or backend rewrites.
