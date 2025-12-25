# Pi-Log Device API

Base URL (on the Pi):

- `http://<pi-hostname>:8000`

---

## GET /health

**Description:**
Return basic health information about the Pi-Log service and its database.

****Response 200:****

```json
{
  "status": "ok",
  "uptime_seconds": 123.45,
  "db": {
    "status": "ok",
    "error": null
  }
}
```
---
## GET /readings/latest
**Description:**
Return the most recent reading from the ingestion database.

**Response 200:**

```json
{
  "id": 123,
  "timestamp": "2025-12-24T18:25:42Z",
  "cps": 17.0,
  "cpm": 1020.0,
  "mode": "SLOW",
  "raw": "CPS,17,1,0.09,SLOW,0"
}
```

**Response 404:**

```json
{
  "detail": "No readings available"
}
```
---

## GET /readings?limit=N
**Description:**
Return the last `N` readings (default 10, max 1000).

Query parameters:

*    `limit` (integer, optional, default `10`, min `1`, max `1000`)

**Response 200:**
```json
[
  {
    "id": 123,
    "timestamp": "2025-12-24T18:25:42Z",
    "cps": 17.0,
    "cpm": 1020.0,
    "mode": "SLOW",
    "raw": "CPS,17,1,0.09,SLOW,0"
  }
]
```
---
## GET /metrics
**Description:**
Return high-level ingestion metrics.

**Response 200:**

```json
{
  "ingested_count": 2646,
  "uptime_seconds": 9876.54,
  "version": "0.1.0"
}
```
