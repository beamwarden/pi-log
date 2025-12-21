import os
import sqlite3
import tempfile
from app.sqlite_store import SQLiteStore


def create_temp_db():
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.close()
    return tmp.name


def test_initialize_db_creates_schema():
    db_path = create_temp_db()
    store = SQLiteStore(db_path)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='readings'")
    result = cur.fetchone()

    conn.close()
    os.unlink(db_path)

    assert result is not None


def test_insert_and_select_unpushed():
    db_path = create_temp_db()
    store = SQLiteStore(db_path)

    reading = {
        "cps": 10,
        "cpm": 100,
        "usv": 0.10,
        "mode": "SLOW",
    }

    store.insert_record(reading)
    rows = store.get_unpushed_readings()

    os.unlink(db_path)

    assert len(rows) == 1
    row = rows[0]
    assert row["cps"] == 10
    assert row["cpm"] == 100
    assert abs(row["usv"] - 0.10) < 1e-6
    assert row["mode"] == "SLOW"
    assert row["pushed"] == 0


def test_mark_readings_pushed():
    db_path = create_temp_db()
    store = SQLiteStore(db_path)

    reading = {
        "cps": 5,
        "cpm": 50,
        "usv": 0.05,
        "mode": "FAST",
    }

    store.insert_record(reading)
    rows = store.get_unpushed_readings()
    ids = [row["id"] for row in rows]

    store.mark_readings_pushed(ids)

    rows_after = store.get_unpushed_readings()

    os.unlink(db_path)

    assert len(rows_after) == 0
