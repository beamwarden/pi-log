# pi-log/app/logging.py
"""
Modern logging subsystem for pi-log.

Features:
- Console logs (INFO+), human-readable, for systemd/journalctl.
- Structured JSON logs (DEBUG+), rotated, durable.
- Config-driven log directory and log level.
- Deterministic, future-maintainer-friendly design.
"""

import json
import logging
import logging.handlers
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Union

# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _level_from_string(level_str: str) -> int:
    try:
        return getattr(logging, level_str.upper())
    except Exception:
        return logging.INFO


# ----------------------------------------------------------------------
# JSON Formatter
# ----------------------------------------------------------------------


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname.lower(),
            "logger": record.name,
            "msg": record.getMessage(),
        }

        # Include structured extras if present
        for key, value in record.__dict__.items():
            if key not in (
                "args",
                "asctime",
                "created",
                "exc_info",
                "exc_text",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "msg",
                "name",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "stack_info",
                "thread",
                "threadName",
            ):
                payload[key] = value

        return json.dumps(payload)


# ----------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------


def setup_logging(config: Optional[Union[dict, object]] = None) -> None:
    """
    Initialize logging for pi-log.

    Parameters:
        config: SettingsNamespace or dict with:
            config.logging.log_dir
            config.logging.level
    """

    # ------------------------------------------------------------------
    # Resolve config
    # ------------------------------------------------------------------
    log_dir = "/opt/pi-log/logs"
    log_level = "INFO"

    if config and hasattr(config, "logging"):
        log_dir = getattr(config.logging, "log_dir", log_dir)
        log_level = getattr(config.logging, "level", log_level)

    log_dir = Path(log_dir)
    _ensure_dir(log_dir)

    level = _level_from_string(log_level)

    # ------------------------------------------------------------------
    # Root logger
    # ------------------------------------------------------------------
    root = logging.getLogger()
    root.setLevel(level)

    # Clear any existing handlers (important for tests + reloads)
    for h in list(root.handlers):
        root.removeHandler(h)

    # ------------------------------------------------------------------
    # Console Handler (INFO+)
    # ------------------------------------------------------------------
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%SZ",
        )
    )
    root.addHandler(console)

    # ------------------------------------------------------------------
    # JSON File Handler (DEBUG+)
    # ------------------------------------------------------------------
    json_path = log_dir / "pi-log.jsonl"
    file_handler = logging.handlers.RotatingFileHandler(
        json_path,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(JSONFormatter())
    root.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
