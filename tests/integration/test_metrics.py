from unittest.mock import patch
from app.ingestion_loop import IngestionLoop


@patch("app.metrics.record_ingestion")
@patch("app.ingestion_loop.parse_geiger_csv")
@patch("app.ingestion_loop.SQLiteStore")
def test_metrics_recorded(mock_store, mock_parse, mock_record):
    mock_parse.return_value = {"cps": 10}
    mock_store.return_value.insert_record.return_value = 1

    loop = IngestionLoop()
    loop.store = mock_store.return_value

    loop.process_line("CPS, 10, CPM, 100, uSv/hr, 0.1, FAST")

    mock_record.assert_called_once()
