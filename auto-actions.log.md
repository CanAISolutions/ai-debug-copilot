# Auto Actions Log

This file records significant automated or scripted changes done by the AI assistant.  It acts as a running changelog + progress tracker.

| Date (UTC) | Action |
|------------|--------|
| 2025-07-29 | Added missing Python deps (NumPy, scikit-learn, pytest) to `requirements.txt` |
| 2025-07-29 | Created `run_demo.ps1` for Windows demo; updated README Windows section |
| 2025-07-29 | Added `backend-mvp-test-plan.md` test-plan document |
| 2025-07-29 | Added Vitest skeleton (`vitest.config.ts`, placeholder test) and NPM dev-deps |
| 2025-07-29 | Added multi-stage `Dockerfile` ready for Render deployment |
| 2025-07-29 | Deployed backend to Render; verified with Invoke-WebRequest ping |
| 2025-07-29 | Added `/healthz` endpoint and GitHub Action workflow `remote-health.yml` |
| 2025-07-29 | Created `ROADMAP.md` to track upcoming enhancements |
| 2025-07-29 | Added helper script `run_remote_demo.py` to send payloads to remote backend |
| 2025-07-29 | Added failing-test collector script & updated Vitest config with JSON/HTML reporters |
| 2025-07-29 | Integrated collector into VS Code extension: auto-runs tests, merges failing files, sends enriched error log |
| 2025-07-30 | Added backend FastAPI scenario tests & coverage workflow; updated roadmap with coverage tasks |
| 2025-07-30 | Added utils unit tests and choose_model/decoder coverage |

---

## In-Progress / Next
1. Reach ≥ 80 % backend coverage (current ~60 %)
2. Instrument TS coverage & add extension tests
3. Add coverage gates in GitHub Actions (extension)
