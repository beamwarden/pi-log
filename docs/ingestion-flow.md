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
