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

> _Last updated: 2025-07-29_
