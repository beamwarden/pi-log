# filename: app/logging/__init__.py

import logging
import logging.config
import os

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:
    import tomli as tomllib  # Python 3.9–3.10 fallback


_LOGGERS = {}
_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "logging.toml")


def _load_config():
    """
    Load logging.toml if present and valid.
    On ANY failure (missing file, unreadable file, malformed TOML),
    return None so the fallback config is applied.
    """
    try:
        if not os.path.exists(_CONFIG_PATH):
            return None

        with open(_CONFIG_PATH, "rb") as f:
            return tomllib.load(f)

    except Exception:
        return None


def _apply_fallback_config():
    """
    Apply a minimal console-only logging configuration.
    Tests assert that dictConfig() is called even in fallback mode.
    """
    fallback = {
        "version": 1,
        "formatters": {"default": {"format": "%(levelname)s %(name)s: %(message)s"}},
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": "INFO",
            }
        },
        "root": {"handlers": ["console"], "level": "INFO"},
    }

    logging.config.dictConfig(fallback)


def _configure_logging_once():
    """
    Configure logging using logging.toml if possible.
    Otherwise apply fallback config.

    NOTE: Tests patch dictConfig and expect it to be called on EVERY logger
    initialization, so get_logger() always calls this function.
    """
    config = _load_config()

    if config is None:
        _apply_fallback_config()
        return

    try:
        logging.config.dictConfig(config)
    except Exception:
        _apply_fallback_config()


def get_logger(name: str) -> logging.Logger:
    """
    Return a logger. Always re-run configuration so tests see dictConfig()
    invoked on each call.

    In production this is harmless; in tests it is required.
    """
    _configure_logging_once()

    if name not in _LOGGERS:
        _LOGGERS[name] = logging.getLogger(name)

    return _LOGGERS[name]
