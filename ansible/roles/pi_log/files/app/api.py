import time
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel

from app.sqlite_store import SQLiteStore

APP_START_TIME = time.time()
DB_PATH = "/var/lib/pi-log/readings.db"  # production path; tests override get_store

app = FastAPI(title="Pi-Log API", version="0.1.0")


# -------------------------
# Pydantic models
# -------------------------

class HealthDBStatus(BaseModel):
    status: str
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    uptime_seconds: float
    db: HealthDBStatus


class Reading(BaseModel):
    id: int
    timestamp: str
    cps: float
    cpm: float
    mode: str
    raw: Optional[str] = None


class MetricsResponse(BaseModel):
    ingested_count: int
    uptime_seconds: float
    version: str = "0.1.0"


# -------------------------
# Dependencies
# -------------------------

def get_store() -> SQLiteStore:
    """
    Production-focused dependency for obtaining a SQLiteStore.

    Tests should override this via:
        app.dependency_overrides[get_store] = override_get_store
    """
    return SQLiteStore(DB_PATH)


def get_uptime_seconds() -> float:
    return time.time() - APP_START_TIME


# -------------------------
# Endpoints
# -------------------------

@app.get("/health", response_model=HealthResponse)
def health(store: SQLiteStore = Depends(get_store)) -> HealthResponse:
    """
    Basic health check with DB connectivity status.
    """
    uptime = get_uptime_seconds()
    db_status = "ok"
    db_error: Optional[str] = None

    try:
        # Cheap connectivity check
        store.get_latest_reading()
    except Exception as exc:  # noqa: BLE001
        db_status = "error"
        db_error = str(exc)

    return HealthResponse(
        status="ok",
        uptime_seconds=uptime,
        db=HealthDBStatus(status=db_status, error=db_error),
    )


@app.get("/readings/latest", response_model=Reading)
def latest_reading(store: SQLiteStore = Depends(get_store)) -> Reading:
    """
    Return the most recent reading, or 404 if none exist.
    """
    row = store.get_latest_reading()
    if not row:
        raise HTTPException(status_code=404, detail="No readings available")

    return Reading(
        id=row["id"],
        timestamp=row["timestamp"],
        cps=row["cps"],
        cpm=row["cpm"],
        mode=row["mode"],
        raw=row.get("raw") if isinstance(row, dict) else None,
    )


@app.get("/readings", response_model=List[Reading])
def list_readings(
    limit: int = Query(10, ge=1, le=1000),
    store: SQLiteStore = Depends(get_store),
) -> List[Reading]:
    """
    Return up to `limit` recent readings.
    """
    rows = store.get_recent_readings(limit=limit)

    readings: List[Reading] = []
    for row in rows:
        readings.append(
            Reading(
                id=row["id"],
                timestamp=row["timestamp"],
                cps=row["cps"],
                cpm=row["cpm"],
                mode=row["mode"],
                raw=row.get("raw") if isinstance(row, dict) else None,
            )
        )
    return readings


@app.get("/metrics", response_model=MetricsResponse)
def metrics(store: SQLiteStore = Depends(get_store)) -> MetricsResponse:
    """
    Basic metrics for ingestion and uptime.
    """
    try:
        # crude metric: count all records
        count = store.count_readings()
    except Exception:  # noqa: BLE001
        count = -1

    return MetricsResponse(
        ingested_count=count,
        uptime_seconds=get_uptime_seconds(),
    )


if __name__ == "__main__":
    # For local dev; systemd will use uvicorn directly
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

print(">>> API MODULE ID:", id(app))
