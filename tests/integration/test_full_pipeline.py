import os
import tempfile
from unittest.mock import MagicMock, patch
import responses

from app.ingestion_loop import IngestionLoop


def create_temp_db():
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.close()
    return tmp.name


@patch("time.sleep", return_value=None)
@patch("app.serial_reader.serial.Serial")
@responses.activate
def test_full_pipeline(mock_serial, _):
    db_path = create_temp_db()

    # Mock serial port to emit one valid line then stop
    mock_port = MagicMock()
    mock_port.readline.side_effect = [
        b"CPS, 7, CPM, 70, uSv/hr, 0.07, FAST\n",
        KeyboardInterrupt,
    ]
    mock_serial.return_value = mock_port

    # Mock API endpoint
    responses.add(
        responses.POST,
        "http://example.com/api/readings",
        json={"status": "ok"},
        status=200,
    )

    # IngestionLoop uses settings.* so we patch settings to point to our temp DB
    with patch("app.ingestion_loop.settings") as mock_settings:
        mock_settings.serial = {"device": "/dev/ttyUSB0", "baudrate": 9600}
        mock_settings.sqlite = {"path": db_path}
        mock_settings.api = {
            "enabled": True,
            "base_url": "http://example.com/api",
            "token": "TOKEN",
        }
        mock_settings.ingestion = {"poll_interval": 0}

        loop = IngestionLoop()

        # Run the pipeline (should read, parse, store, push, exit)
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass

    os.unlink(db_path)
