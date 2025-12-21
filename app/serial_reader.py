import serial
from app.logging import get_logger

log = get_logger(__name__)


def parse_geiger_csv(line):
    """
    Parse a Geiger CSV line like:
      b"CPS, 7, CPM, 70, uSv/hr, 0.07, FAST\\n"

    Into a dict:
      {"cps": 7, "cpm": 70, "usv": 0.07, "mode": "FAST"}

    Tests patch this function at the module level, so it must exist here.
    """
    if isinstance(line, bytes):
        line = line.decode("utf-8", errors="ignore").strip()

    parts = [p.strip() for p in line.split(",")]
    if len(parts) < 8:
        return None

    try:
        return {
            "cps": int(parts[1]),
            "cpm": int(parts[3]),
            "usv": float(parts[5]),
            "mode": parts[7],
        }
    except (ValueError, IndexError):
        return None


class SerialReader:
    """
    Reads lines from a serial device and parses them.

    Tests expect:
      - SerialReader(device, baudrate=9600)
      - read_line() calls serial.Serial(...).readline()
      - run() reads exactly one line
      - run() calls parse_geiger_csv
      - run() calls _handle_parsed(record) only if record is not None
    """

    def __init__(self, device: str, baudrate: int = 9600):
        self.device = device
        self.baudrate = baudrate
        self.ser = None

    def _ensure_open(self):
        if self.ser is None:
            self.ser = serial.Serial(self.device, self.baudrate)

    def _handle_parsed(self, record: dict):
        """
        Tests patch this method to assert call counts.
        Default implementation does nothing.
        """
        return None

    def read_line(self):
        self._ensure_open()
        return self.ser.readline()

    def run(self):
        """
        Continuously read lines until KeyboardInterrupt.
        For each line:
          - parse
          - if valid, call _handle_parsed
        """
        while True:
            try:
                raw = self.read_line()
            except KeyboardInterrupt:
                break

            record = parse_geiger_csv(raw)
            if record:
                self._handle_parsed(record)

        return None

