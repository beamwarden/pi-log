import json
import responses
from app.api_client import APIClient


@responses.activate
def test_push_success_calls_api_for_each_row():
    client = APIClient("http://example.com/api", "TOKEN")

    responses.add(
        responses.POST,
        "http://example.com/api/readings",
        json={"status": "ok"},
        status=200,
    )

    rows = [
        {"id": 1, "cps": 10, "cpm": 100, "usv": 0.10, "mode": "SLOW"},
        {"id": 2, "cps": 20, "cpm": 200, "usv": 0.20, "mode": "FAST"},
    ]

    for row in rows:
        client.push_record(row["id"], row)

    assert len(responses.calls) == 2
    assert responses.calls[0].request.url == "http://example.com/api/readings"
    assert responses.calls[1].request.url == "http://example.com/api/readings"


@responses.activate
def test_push_failure_does_not_raise():
    client = APIClient("http://example.com/api", "TOKEN")

    responses.add(
        responses.POST,
        "http://example.com/api/readings",
        status=500,
    )

    row = {"id": 1, "cps": 10, "cpm": 100, "usv": 0.10, "mode": "SLOW"}

    # Should not raise an exception
    client.push_record(row["id"], row)

    assert len(responses.calls) == 1


@responses.activate
def test_payload_structure():
    client = APIClient("http://example.com/api", "TOKEN")

    responses.add(
        responses.POST,
        "http://example.com/api/readings",
        json={"status": "ok"},
        status=200,
    )

    row = {"id": 1, "cps": 5, "cpm": 50, "usv": 0.05, "mode": "INST"}

    client.push_record(row["id"], row)

    sent = json.loads(responses.calls[0].request.body)

    assert sent["id"] == 1
    assert sent["cps"] == 5
    assert sent["mode"] == "INST"
