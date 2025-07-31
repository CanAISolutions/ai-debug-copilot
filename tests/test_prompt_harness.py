import json
from pathlib import Path
from app.prompt_builder import build_prompt
from app.main import simulate_response

FIXTURE_DIR = Path(__file__).parent / "prompt_fixtures"

def load_fixtures():
    for fp in FIXTURE_DIR.glob("*.json"):
        data = json.loads(fp.read_text(encoding="utf-8"))
        yield data

def score(result: dict, expected_keywords: list[str]) -> bool:
    root = result.get("root_cause", "").lower()
    return all(k in root for k in expected_keywords)

def test_fixtures_accuracy():
        fixtures = list(load_fixtures())
    failures: list[str] = []
    for fx in fixtures:
        prompt = build_prompt(fx["error_log"], fx["summary"], None, None)
        resp = simulate_response(prompt)
        if not score(resp, fx["expected_keywords"]):
            failures.append(fx["name"])
    assert not failures, f"Fixtures failed: {', '.join(failures)}"
