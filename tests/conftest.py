import sys
import os
import pytest
from unittest.mock import MagicMock, patch


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)


@pytest.fixture(autouse=True)
def mock_serial():
    with patch("app.serial_reader.serial.Serial", return_value=MagicMock()):
        yield
