from app.ingestion_loop import IngestionLoop


def test_ingestion_loop_constructs():
    loop = IngestionLoop()

    assert loop.reader is not None
    assert loop.store is not None
    assert loop.poll_interval > 0

    if loop.api_enabled:
        assert loop.api is not None
