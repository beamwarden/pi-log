# Ingestion Sequence

```
Sensor Driver → Scheduler → SQLite Queue → PushClient → Beamwarden
```

Each reading is typed, timestamped, queued, and pushed reliably.
