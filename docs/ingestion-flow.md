# Ingestion Flow

## Overview

The ingestion pipeline reads MightyOhm Geiger counter CSV lines from a USB
serial device, parses them, stores them in SQLite, records metrics, and
optionally pushes them to an upstream API or push client.

## Serial Format

Example:
```
CPS, 1, CPM, 21, uSv/hr, 0.11, SLOW
```

Fields:
- CPS → counts per second
- CPM → counts per minute
- uSv/hr → microsieverts per hour
- Mode → SLOW, FAST, INST

## Parser

`parse_geiger_csv()` extracts:
- cps (int)
- cpm (int)
- usv (float)
- mode (normalized)
- raw (original line)

Malformed lines return `None`.

## IngestionLoop

Responsibilities:
- Read raw lines
- Parse via `parse_geiger_csv`
- Insert into SQLite
- Record metrics
- Push to API (optional)
- Push to LogExp (optional)
- Provide `run_once()` and `run_forever()`

## SerialReader

- Reads raw lines
- Calls `_handle_parsed()` when parsing is delegated
---
# 📘 Ingestion Loop Architecture (Maintainer Guide)
## Overview

The ingestion loop is responsible for:

*    Reading raw lines from the MightyOhm Geiger Counter
*    Parsing them into structured reading
*    Storing them in SQLite
*    Forwarding them to the API layer
*    Applying retry logic and backoff
*    Respecting ingestion mode settings (FAST, SLOW, INST)

## Constructor
```python
class IngestionLoop:
    def __init__(
        self,
        serial_reader: SerialReader,
        parser: Parser,
        store: SQLiteStore,
        api_client: APIClient,
        settings: Settings,
    ):
        ...
```
All five components are injected, making the loop fully testable and overrideable.

## Settings
The ingestion loop uses a `Pydantic` Settings model:
```python
class Settings(BaseModel):
    ingestion_mode: str = "FAST"
    batch_size: int = 10
    retry_limit: int = 3
    retry_backoff_seconds: float = 0.5
```

## Dependency Injection
The ingestion loop is constructed via FastAPI-style DI:
```python
def get_settings() -> Settings:
    return Settings()
```
Tests override this dependency to simulate different ingestion modes.

## Testability
All ingestion loop tests use dependency overrides:
```python
app.dependency_overrides[get_settings] = lambda: Settings(ingestion_mode="SLOW")
```
This ensures:
*    deterministic behavior
*    reproducible timing
*    no reliance on global state
*    no reliance on real serial devices
*    no reliance on real API endpoints

## Runtime Behavior

Systemd launches the ingestion loop via:
```bash
ExecStart=/usr/bin/python3 -m app.ingestion_loop
```
The loop runs forever, respecting:
*    ingestion mode
*    retry logic
*    batch size
*    backoff timing
