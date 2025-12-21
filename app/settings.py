from app.config_loader import CONFIG

# Tests expect these module-level dicts to exist.
# They also patch them directly in many cases.
serial = CONFIG.get("serial", {})
sqlite = CONFIG.get("sqlite", {})
api = CONFIG.get("api", {})
ingestion = CONFIG.get("ingestion", {})
