from unittest.mock import patch, MagicMock
from app.ingestion_loop import IngestionLoop


@patch("app.ingestion_loop.parse_geiger_csv")
@patch("app.ingestion_loop.SQLiteStore")
@patch("app.ingestion_loop.APIClient")
def test_ingestion_loop_handles_push_failure(mock_api, mock_store, mock_parse):
    # Mock parser output
    mock_parse.return_value = {"cps": 10}

    # Mock DB insert
    mock_store.return_value.insert_record.return_value = 1

    # Mock API failure
    mock_api_instance = mock_api.return_value
    mock_api_instance.push_record.side_effect = Exception("network error")

    loop = IngestionLoop()
    loop.api_enabled = True
    loop.api = mock_api_instance
    loop.store = mock_store.return_value

    # Should not raise even though push fails
    loop.process_line("CPS, 10, CPM, 100, uSv/hr, 0.1, FAST")

    mock_api_instance.push_record.assert_called_once()
