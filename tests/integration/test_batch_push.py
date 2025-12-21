from unittest.mock import patch
from app.ingestion_loop import IngestionLoop


@patch("app.ingestion_loop.parse_geiger_csv")
@patch("app.ingestion_loop.SQLiteStore")
@patch("app.ingestion_loop.APIClient")
def test_batch_push_sequential(mock_api, mock_store, mock_parse):
    # Parser returns different readings each time
    mock_parse.side_effect = [
        {"cps": 1},
        {"cps": 2},
        {"cps": 3},
    ]

    # DB insert returns IDs 1, 2, 3
    mock_store.return_value.insert_record.side_effect = [1, 2, 3]

    loop = IngestionLoop()
    loop.api_enabled = True
    loop.api = mock_api.return_value
    loop.store = mock_store.return_value

    loop.process_line("line1")
    loop.process_line("line2")
    loop.process_line("line3")

    assert mock_store.return_value.insert_record.call_count == 3
    assert mock_api.return_value.push_record.call_count == 3
