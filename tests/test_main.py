import base64, gzip, json, pathlib
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_healthz():
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_diagnose_simulation_empty():
    payload = {"files": [], "error_log": "", "summary": "ping"}
    resp = client.post("/diagnose", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    # Mandatory keys
    for key in ["root_cause", "confidence", "patches", "follow_up", "agent_block"]:
        assert key in body
    # In simulation mode we expect the deterministic diff patch
    assert any("Hello, AI Debugging Copilot" in p for p in body["patches"])


def test_diagnose_with_file():
    # Create a temporary file with simple content and encode it
    code = b"print('hello from test')\n"
    compressed = gzip.compress(code)
    encoded = base64.b64encode(compressed).decode()
    payload = {
        "files": [{"filename": "hello.py", "content": encoded}],
        "error_log": "Traceback (most recent call last): ValueError: demo",
        "summary": "simple demo",
    }
    resp = client.post("/diagnose", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data["confidence"], float)
