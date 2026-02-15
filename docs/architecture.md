# pi‑log Architecture

pi‑log is a **portable, containerized multi‑sensor ingestion hub** for Beamrider nodes.
It collects readings from arbitrary sensors, stores them locally, and pushes them to Beamwarden using a unified ingestion schema.

## Components

### Sensor Drivers
Modular Python plugins that read from:
- serial ports
- I²C/SPI buses
- USB devices
- network endpoints
- virtual sources

### Scheduler
Coordinates polling intervals, event‑driven reads, and network subscriptions.

### Local Queue
SQLite database in WAL mode:
- crash‑safe
- bounded
- replay on restart

### PushClient
Handles:
- retries
- backoff
- marking rows as pushed
- identity headers

### Container Runtime
pi‑log runs as a single container image on any Linux host.

---

## Data Flow

```
Sensor Driver → Scheduler → SQLite Queue → PushClient → Beamwarden
```

---

## Deployment

Deployment and provisioning are handled by **Quasar**, not pi‑log.
pi‑log contains no infrastructure code.
