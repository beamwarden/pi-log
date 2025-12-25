import pytest
from app.api import app, get_store
from app.sqlite_store import SQLiteStore
from fastapi.testclient import TestClient

print(">>> LOADED tests/api/conftest.py")



@pytest.fixture
def temp_db(tmp_path):
    db_path = tmp_path / "test.db"
    db_path.touch()
    store = SQLiteStore(str(db_path))
    store.initialize_db()
    return str(db_path)


@pytest.fixture
def client(temp_db):
    def override_get_store():
        return SQLiteStore(temp_db)

    app.dependency_overrides[get_store] = override_get_store
    return TestClient(app)
