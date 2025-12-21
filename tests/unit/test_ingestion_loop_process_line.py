from unittest.mock import patch, MagicMock
from app.ingestion_loop import IngestionLoop


@patch("app.ingestion_loop.parse_geiger_csv")
@patch("app.ingestion_loop.SQLiteStore")
@patch("app.ingestion_loop.APIClient")
def test_process_line_stores_and_pushes(mock_api, mock_store, mock_parse):
    # Mock parser output
    mock_parse.return_value = {"cps": 10, "cpm": 100, "usv": 0.1, "mode": "FAST"}

    # Mock store behavior
    mock_store.return_value.insert_record.return_value = 1

    # Enable API
    mock_api_instance = mock_api.return_value

    loop = IngestionLoop()
    loop.api_enabled = True
    loop.api = mock_api_instance
    loop.store = mock_store.return_value

    loop.process_line("CPS, 10, CPM, 100, uSv/hr, 0.1, FAST")

    mock_parse.assert_called_once()
    loop.store.insert_record.assert_called_once()
    loop.api.push_record.assert_called_once_with(1, mock_parse.return_value)
