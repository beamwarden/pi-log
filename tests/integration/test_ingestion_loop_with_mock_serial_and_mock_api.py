import responses
from unittest.mock import patch, MagicMock
from app.ingestion_loop import IngestionLoop


@patch("time.sleep", return_value=None)
@patch("app.ingestion_loop.SerialReader")
@patch("app.ingestion_loop.SQLiteStore")
@responses.activate
def test_ingestion_loop_full_pipeline(mock_store, mock_reader, _):
    # Mock serial input
    mock_reader_instance = mock_reader.return_value
    mock_reader_instance.read_line.side_effect = [
        "CPS, 9, CPM, 90, uSv/hr, 0.09, FAST",
        KeyboardInterrupt,
    ]

    # Mock DB
    mock_store_instance = mock_store.return_value
    mock_store_instance.insert_record.return_value = 1

    # Mock API
    responses.add(
        responses.POST,
        "http://example.com/api/readings",
        json={"status": "ok"},
        status=200,
    )

    loop = IngestionLoop()
    loop.api_enabled = True
    loop.api.base_url = "http://example.com/api"

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    mock_store_instance.insert_record.assert_called_once()
