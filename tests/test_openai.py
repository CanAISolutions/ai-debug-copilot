import importlib, os
from unittest import mock

import app.main as m


def test_call_openai_fallback_env(monkeypatch):
    # Ensure OPENAI_API_KEY not set
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    resp = m.call_openai("gpt-4o-mini", "dummy prompt")
    assert resp["agent_block"].startswith("Simulated")


def test_call_openai_fallback_request(monkeypatch):
    # Provide fake key so path uses requests, but mock requests.post to raise
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    with mock.patch("app.main.requests.post", side_effect=Exception("network")):
        resp = m.call_openai("gpt-4o-mini", "dummy prompt that triggers fallback")
    assert resp["agent_block"].startswith("Simulated")


def test_choose_model_many_files_long_log():
    files = [m.FilePayload(filename=f"f{i}.py", content="") for i in range(4)]
    long_log = "error" * 200  # >500 chars
    assert m.choose_model(long_log, files) == "gpt-4o"
