import os
import requests
import pytest

BACKEND = os.getenv("BACKEND_URL")

@pytest.mark.skipif(not BACKEND, reason="BACKEND_URL env var not set")
def test_remote_health():
    r = requests.get(f"{BACKEND}/healthz", timeout=15)
    assert r.status_code == 200
    assert r.json().get("status") == "ok"
