# filename: app/serial_reader/serial_reader.py

import time
import serial
from app.ingestion.csv_parser import parse_geiger_csv


class SerialReader:
    """
    Reads raw lines from a serial device, parses them, and forwards parsed
    records to a callback set by the ingestion loop.

    Unit tests expect the constructor signature:
        SerialReader(device, baudrate=9600, timeout=1.0)

    Tests patch serial.Serial directly:
        @patch("serial.Serial")
    """

    def __init__(self, device, baudrate=9600, timeout=1.0):
        self.device = device
        self.baudrate = baudrate
        self.timeout = timeout

        # Serial object is created lazily on first read
        self.ser = None

        # Ingestion loop assigns this callback
        self._handle_parsed = None

    def read_line(self):
        """
        Read a single line from the serial device.
        Returns a decoded UTF-8 string or an empty string on timeout.
        """
        if self.ser is None:
            self.ser = serial.Serial(
                self.device,
                self.baudrate,
                timeout=self.timeout,
            )

        raw = self.ser.readline()
        if not raw:
            return ""

        return raw.decode("utf-8", errors="ignore").strip()

    def run(self):
        """
        Continuously read lines, parse them, and forward parsed records.

        Tests patch Serial.readline() to raise KeyboardInterrupt to stop the loop.
        """
        while True:
            try:
                raw = self.read_line()
                parsed = parse_geiger_csv(raw)

                if parsed and self._handle_parsed is not None:
                    self._handle_parsed(parsed)

            except (KeyboardInterrupt, StopIteration):
                break

            except Exception:
                # Avoid tight loops on transient errors
                time.sleep(0.1)
