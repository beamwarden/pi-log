import os
import tempfile
from unittest.mock import MagicMock, patch

from app.serial_reader import SerialReader
from app.csv_parser import parse_geiger_csv
from app.sqlite_store import SQLiteStore


def create_temp_db():
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.close()
    return tmp.name


@patch("app.serial_reader.serial.Serial")
def test_serial_to_parser_to_storage(mock_serial):
    # Mock the serial port to return one valid line, then stop
    mock_port = MagicMock()
    mock_port.readline.side_effect = [
        b"CPS, 9, CPM, 90, uSv/hr, 0.09, FAST\n",
        KeyboardInterrupt,  # stop the reader loop
    ]
    mock_serial.return_value = mock_port

    # Create temporary SQLite database
    db_path = create_temp_db()
    store = SQLiteStore(db_path)

    # We patch SerialReader so that instead of inserting internally,
    # we manually parse + store inside the test.
    def fake_handler():
        raw = mock_port.readline().decode("utf-8").strip()
        parsed = parse_geiger_csv(raw)
        if parsed:
            store.insert_record(parsed)

    # Patch SerialReader.run to call our fake handler once
    with patch.object(SerialReader, "run", side_effect=fake_handler):
        reader = SerialReader("/dev/ttyUSB0")
        reader.run()

    # Validate DB contents
    rows = store.get_unpushed_readings()
    os.unlink(db_path)

    assert len(rows) == 1
    assert rows[0]["cps"] == 9
    assert rows[0]["cpm"] == 90
    assert abs(rows[0]["usv"] - 0.09) < 1e-6
    assert rows[0]["mode"] == "FAST"
