from unittest.mock import patch
from app.health import health_check


def test_health_check_returns_ok():
    result = health_check()
    assert result["status"] == "ok"
