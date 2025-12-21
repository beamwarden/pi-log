from pathlib import Path
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


class Settings:
    def __init__(self, path: Path):
        with path.open("rb") as f:
            self._data = tomllib.load(f)

    @property
    def serial(self):
        return self._data["serial"]

    @property
    def sqlite(self):
        return self._data["sqlite"]

    @property
    def api(self):
        return self._data["api"]

    @property
    def ingestion(self):
        return self._data["ingestion"]

# Default config path for Pi + local dev override
config_path = Path("/opt/pi-log/config/settings.toml")
if not config_path.exists():
    # fallback for local development
    config_path = Path("config/settings.toml")

settings = Settings(config_path)
