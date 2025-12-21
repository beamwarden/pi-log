import time

from app.serial_reader import SerialReader, parse_geiger_csv
from app.sqlite_store import SQLiteStore
from app.api_client import APIClient
from app.logging import get_logger
from app.metrics import record_ingestion
from app import settings

log = get_logger(__name__)


class IngestionLoop:
    """
    Orchestrates the ingestion pipeline:
      - read raw line
      - parse CSV
      - store in SQLite
      - record metrics
      - optionally push to API
    """

    def __init__(self):
        # Serial reader
        self.reader = SerialReader(
            settings.serial.get("device", "/dev/null"),
            settings.serial.get("baudrate", 9600),
        )

        # SQLite store
        self.store = SQLiteStore(settings.sqlite.get("path", ":memory:"))

        # API client
        api_cfg = settings.api
        self.api_enabled = api_cfg.get("enabled", False)
        self.api = APIClient(
            api_cfg.get("base_url", ""),
            api_cfg.get("token", ""),
        )

        # Loop timing
        self.poll_interval = settings.ingestion.get("poll_interval", 1)

    def process_line(self, raw):
        """
        Parse, store, record metrics, and optionally push a single raw line.
        Returns True if processed, False if malformed.
        """
        record = parse_geiger_csv(raw)
        if not record:
            return False

        # Store record
        record_id = self.store.insert_record(record)

        # Metrics hook
        record_ingestion(record)

        # Optional API push
        if self.api_enabled:
            try:
                self.api.push_record(record_id, record)
                self.store.mark_readings_pushed([record_id])
            except Exception as exc:
                log.exception(f"Push failed: {exc}")

        return True

    def run_once(self):
        """
        Execute a single ingestion iteration.
        Returns True if work was done, False if the loop should exit.
        """
        try:
            raw = self.reader.read_line()
        except (KeyboardInterrupt, StopIteration):
            return False

        if not raw:
            return False

        self.process_line(raw)
        return True

    def run_forever(self):
        """
        Production loop. Tests do not call this directly.
        """
        while self.run_once():
            time.sleep(self.poll_interval)
