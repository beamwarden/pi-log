import logging
import logging.config
import os
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:
    import tomli as tomllib  # Python 3.9 fallback


# Tests expect these names to exist at module level
__all__ = ["get_logger", "os", "logging"]


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_LOG_CONFIG = BASE_DIR / "logging.toml"
DEFAULT_LOG_DIR = (BASE_DIR / ".." / "logs").resolve()


def _load_logging_config(path: Path):
    """
    Return parsed TOML dict or None on any error.
    Tests simulate:
      - missing file
      - unreadable file
      - malformed TOML
    """
    if not path.exists():
        return None

    try:
        with path.open("rb") as f:
            return tomllib.load(f)
    except Exception:
        return None


def _ensure_log_directory(path: Path):
    """
    Ensure the log directory exists.

    Tests patch:
      - app.logging.os.path.exists
      - app.logging.os.makedirs
    """
    dir_path = path if not path.suffix else path.parent

    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)


def get_logger(name: str):
    """
    Configure logging from TOML if possible, else fall back to basicConfig.

    Required behavior:
      - If TOML exists and loads → dictConfig
      - If dictConfig fails → fallback
      - If TOML missing/malformed/unreadable → fallback
      - Fallback must:
          * ensure log directory exists
          * call logging.basicConfig exactly once
    """
    config = _load_logging_config(DEFAULT_LOG_CONFIG)

    if config:
        try:
            logging.config.dictConfig(config)
        except Exception:
            # Fall through to fallback
            pass

    # If no handlers configured, fallback to basicConfig
    if not logging.getLogger().handlers:
        _ensure_log_directory(DEFAULT_LOG_DIR)
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )

    return logging.getLogger(name)
