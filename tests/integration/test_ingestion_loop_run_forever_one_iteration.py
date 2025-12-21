from unittest.mock import patch, MagicMock
from app.ingestion_loop import IngestionLoop


@patch("time.sleep", return_value=None)
@patch("app.ingestion_loop.SerialReader")
def test_run_forever_one_iteration(mock_reader, _):
    mock_reader_instance = mock_reader.return_value
    mock_reader_instance.read_line.side_effect = [
        "CPS, 5, CPM, 50, uSv/hr, 0.05, SLOW",
        KeyboardInterrupt,
    ]

    loop = IngestionLoop()

    with patch.object(loop, "process_line") as mock_process:
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass

    mock_process.assert_called_once_with("CPS, 5, CPM, 50, uSv/hr, 0.05, SLOW")
