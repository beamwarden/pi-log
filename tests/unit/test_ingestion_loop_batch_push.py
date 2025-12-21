from unittest.mock import patch, MagicMock
from app.ingestion_loop import IngestionLoop


@patch("app.ingestion_loop.parse_geiger_csv")
@patch("app.ingestion_loop.SQLiteStore")
@patch("app.ingestion_loop.APIClient")
def test_ingestion_loop_pushes_multiple_records(mock_api, mock_store, mock_parse):
    # Mock parser output for multiple lines
    mock_parse.side_effect = [
        {"cps": 1},
        {"cps": 2},
        {"cps": 3},
    ]

    # Mock DB insert IDs
    mock_store.return_value.insert_record.side_effect = [1, 2, 3]

    loop = IngestionLoop()
    loop.api_enabled = True
    loop.api = mock_api.return_value
    loop.store = mock_store.return_value

    # Process multiple lines
    loop.process_line("line1")
    loop.process_line("line2")
    loop.process_line("line3")

    # DB insert called 3 times
    assert mock_store.return_value.insert_record.call_count == 3

    # Push called 3 times
    assert mock_api.return_value.push_record.call_count == 3
