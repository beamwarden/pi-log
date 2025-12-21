from app.config import settings


def test_config_has_required_sections():
    assert "serial" in settings._data
    assert "sqlite" in settings._data
    assert "api" in settings._data
    assert "ingestion" in settings._data


def test_config_serial_section():
    serial = settings.serial
    assert "device" in serial
    assert "baudrate" in serial


def test_config_sqlite_section():
    sqlite_cfg = settings.sqlite
    assert "path" in sqlite_cfg


def test_config_api_section():
    api = settings.api
    assert "enabled" in api
    assert "base_url" in api
    assert "token" in api


def test_config_ingestion_section():
    ingestion = settings.ingestion
    assert "poll_interval" in ingestion
