import os
import tempfile
import responses

from app.sqlite_store import SQLiteStore
from app.api_client import APIClient


def create_temp_db():
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.close()
    return tmp.name


@responses.activate
def test_storage_to_push_to_storage():
    # Create temporary SQLite database
    db_path = create_temp_db()
    store = SQLiteStore(db_path)

    # Insert a reading
    store.insert_record({"cps": 9, "cpm": 90, "usv": 0.09, "mode": "FAST"})

    rows = store.get_unpushed_readings()
    assert len(rows) == 1

    # Mock API endpoint
    responses.add(
        responses.POST,
        "http://example.com/api/readings",
        json={"status": "ok"},
        status=200,
    )

    client = APIClient("http://example.com/api", "TOKEN")

    # Push each row individually (new API behavior)
    pushed_ids = []
    for row in rows:
        client.push_record(row["id"], row)
        pushed_ids.append(row["id"])

    # Mark rows as pushed
    store.mark_readings_pushed(pushed_ids)

    # Confirm DB is empty
    remaining = store.get_unpushed_readings()
    os.unlink(db_path)

    assert len(remaining) == 0
