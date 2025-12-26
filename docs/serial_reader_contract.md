# SerialReader Contract and Responsibilities

## Overview

`SerialReader` is responsible for **reading raw serial input** and **delegating parsed records**.
It intentionally does **not** own parsing logic, storage, or API concerns.

This separation ensures:
- Deterministic unit testing
- Clean ingestion orchestration
- No hidden side effects during reads

---

## Responsibilities

### SerialReader **DOES**
- Open and manage the serial connection
- Read raw bytes from the device
- Decode bytes into strings
- Delegate parsed records via `_handle_parsed`

### SerialReader **DOES NOT**
- Persist data
- Push data to APIs
- Retry failed operations
- Perform batching
- Own ingestion control flow

---

## Method Contracts

### `read_line()`

```python
def read_line(self) -> str:
```
## Behavior
- Reads a single line from the serial device
- Decodes bytes to UTF‑8
- Returns a stripped string
- Does not parse
- Does not handle records
- Does not swallow `KeyboardInterrupt`

## Guarantees
- Returns a string (possibly empty)
- Raises KeyboardInterrupt when the serial source stops
---

```python
run()
def run(self):
```
## Behavior
- Continuously reads lines
- Parses each line using parse_geiger_csv
- Delegates valid parsed records via _handle_parsed
- Terminates cleanly on KeyboardInterrupt or StopIteration

## Control Flow
```
read_line → parse → delegate → repeat
```
## Delegation Hook: `_handle_parsed`
```python
self._handle_parsed: Optional[Callable[[dict], None]]
```
- Assigned externally by the ingestion loop
- Patched directly by unit tests
- Must exist on the instance
- Must not be bound in `__init__`
---
## Design Rationale
This contract ensures:
- Unit tests can patch _handle_parsed safely
- Parsing logic remains testable in isolation
- Ingestion orchestration remains flexible
- SerialReader remains reusable and minimal
Any deviation from this contract should be considered a breaking change.

---

## `docs/ingestion_loop_overview.md`

```markdown
# Ingestion Loop Architecture

## Overview

The ingestion loop coordinates data flow between:
- SerialReader
- Parser
- Storage
- Push Client

Each component has a single responsibility and communicates through explicit seams.

---

## Data Flow

```text
SerialReader
    ↓
parse_geiger_csv
    ↓
process_line
    ↓
Storage
    ↓
PushClient
```
---
## Responsibilities by Component
### SerialReader
- Reads raw input
- Delegates parsed records

### Parser
- Converts raw strings into structured dictionaries
- Returns None for malformed input

### Ingestion Loop
- Owns control flow
- Handles retries
- Batches records
- Coordinates storage and push behavior

### Storage
- Persists readings
-     Tracks push state

### Push Client
- Sends readings to the API
- Reports success or failure
---
## Why This Matters

This architecture ensures:
- Unit tests remain fast and deterministic
- Integration tests validate wiring, not logic
- Failures are isolated and recoverable
- Refactors do not cascade across layers
---
## Testing Strategy
| Layer | Test Type |
|-------|-----------|
| Parser | Unit |
| SerialReader | Unit |
| Ingestion Loop | Unit |
| Storage | Unit |
| Full Pipeline | Integration |

Each test validates **one responsibility only**.

---

## `docs/testing_contracts.md`

```markdown
# Testing Contracts and Expectations

## Purpose

This document defines the behavioral contracts relied upon by the test suite.
Breaking these contracts will cause test failures.

---

## SerialReader Test Expectations

### `read_line()`
- Returns decoded strings
- Does not parse
- Does not call `_handle_parsed`
- Propagates `KeyboardInterrupt`

### `run()`
- Calls `_handle_parsed(parsed)` for each valid record
- Skips malformed lines
- Terminates on `KeyboardInterrupt` or `StopIteration`

---

## `_handle_parsed` Contract

- Must exist on the instance
- Must be callable
- Must not be bound during construction
- Must be patchable by unit tests

---

## Parser Contract

```python
parse_geiger_csv(raw: str) -> Optional[dict]
```
- Returns `None` for malformed or partial input
- Returns a dict for valid input
- Never raises on bad data
---
## Ingestion Loop Contract
- Owns retries
- Owns batching
- Owns push failure handling
- Never blocks SerialReader
---
## Why These Contracts Exist
They allow:
- Safe refactoring
- Clear ownership boundaries
- Predictable test behavior
- Confident CI enforcement
Any change to these contracts must be accompanied by test updates.

---
