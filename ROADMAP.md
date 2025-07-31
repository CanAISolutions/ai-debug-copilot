# AI Debugging Copilot – Roadmap & Task Tracker

This document tracks upcoming work items (no external Taskmaster system required).  Each task has a short description, acceptance criteria, and status.

Legend:
`[ ]` = not started  `[~]` = in-progress  `[x]` = done

---

## 1. Auto-run project tests & capture failures (Extension)
*Status: [ ]*

### Description
Detect the project’s JavaScript/TypeScript test runner (Vitest, Jest, etc.), run the suite, capture JSON results, and isolate failing specs.

### Acceptance Criteria
- Reads `package.json` and infers the proper test command.
- Runs test command with JSON reporter to `vitest.json`/`jest.json`.
- Parses reporter output and builds an array of failing test cases with stack traces.
- Only sends failing test files & error logs to backend in the `files` array of the `/diagnose` request.
- Works on Windows, macOS, Linux.

---

## 2. Send failing files + stack-trace to backend
*Status: [ ]*

### Description
Extend existing file-collection logic to include:
1. Failing spec files.
2. Source files referenced in the stack trace.
3. The raw stack trace in `error_log`.

### Acceptance Criteria
- Compression/encoding identical to current approach.
- Payload validated against backend’s `DiagnoseRequest` schema.
- Manual test proves backend returns a higher-quality root cause given the extra context.

---

## 3. WebView "Cursor-style" Follow-Up Panel (Extension)
*Status: [ ]*

### Description
After `/diagnose` responds, open a panel summarising root cause, patches, confidence, and next steps.

### Acceptance Criteria
- Panel shows sections: *What Happened*, *Proposed Fix*, *Next Steps*.
- Renders unified diff with syntax highlighting.
- "Apply patch" button writes changes to workspace files.
- Works even when only `follow_up` is returned (no patches).

---

## 4. Prometheus `/metrics` endpoint (Backend – Optional)
*Status: [ ]*

### Description
Expose FastAPI route that returns Prometheus-formatted counters/gauges so Render can scrape or we can pushgateway.

### Acceptance Criteria
- Endpoint `/metrics` disabled by default via env flag `ENABLE_METRICS`.
- Counters: total_requests, total_failures, avg_duration_ms, avg_confidence.
- No third-party cost; uses `prometheus_client` (BSD-licensed).

---

## 5. Improve backend test coverage to ≥ 80 %
*Status: [ ]*

### Description
Add FastAPI `TestClient` scenario tests for `/healthz` and `/diagnose` (happy-path, large payload, model-fallback) plus edge-case unit tests in utils.

### Acceptance Criteria
- Coverage report shows ≥ 80 % for `app/` package.
- CI fails if coverage drops below threshold (`--cov-fail-under=80`).

---

## 6. Instrument TS coverage & add extension tests
*Status: [ ]*

### Description
Switch Vitest to Istanbul coverage plugin, create unit tests for new failure-collector & payload builder logic.

### Acceptance Criteria
- V8/Istanbul report shows ≥ 60 % for `src/`.
- CI prints coverage summary; threshold ratchets upward over time.

---

## 7. Add coverage gates in GitHub Actions
*Status: [ ]*

### Description
Extend existing backend + extension workflows to enforce the coverage thresholds defined above.

### Acceptance Criteria
- `pytest --cov --cov-fail-under` gate.
- `vitest --coverage` gate with Istanbul.
- Workflow status red on drop.

---

> _Last updated: 2025-07-30_
