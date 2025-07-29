# Backend MVP Test Plan

## Scope
Validate the FastAPI `/diagnose` endpoint, vector-store side effects, and metrics logging. Ensure correct behaviour with and without an `OPENAI_API_KEY` present.

## Test Matrix
| Case | Description | Expected Result |
|------|-------------|-----------------|
| 1 | Happy path (small error log, 2 files) | HTTP 200, JSON schema valid, confidence >0, metrics row created |
| 2 | Large payload (>500 chars, >3 files) | Model selection = `gpt-4o`, still HTTP 200 |
| 3 | Empty `files` array | HTTP 200, graceful handling, `patches` possibly empty |
| 4 | Malformed error log (no file refs) | Context extraction returns empty, still returns JSON |
| 5 | API key present but OpenAI unreachable | Falls back to `simulate_response`, HTTP 200 |
| 6 | Invalid model response (simulate tamper) | Endpoint returns 500 |

## Edge-Cases
* Non-UTF-8 file content.
* Duplicate filenames with different paths.
* `parse_error_log` picks multiple references on the same line.

## Logging & Metrics
* Verify `metrics.db` contains new row with `duration_ms`, token counts, confidence.
* Log call duration within ±50 ms of stopwatch measurement.

## Out-of-Scope
VS Code extension front-end, TaskMaster integration, UI rendering.

---

*Updated: $(Get-Date -Format _yyyy-MM-dd_HH:mm)*