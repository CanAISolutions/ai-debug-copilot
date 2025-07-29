# AI Debugging Copilot Proof‑of‑Concept

<!-- Badges -->
![Build Status](https://github.com/your-account/your-repo/actions/workflows/ci.yml/badge.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

This repository contains a prototype for an “AI Debugging Copilot”
demonstrating how a VS Code extension can gather context about a failing
test, submit it to an AI model via a FastAPI backend, receive a JSON
diagnosis and patch, and apply the patch to fix the bug.

## Project structure

- `app/` – FastAPI backend with `/diagnose` endpoint and utilities for
  context extraction, vector retrieval, metric logging, and prompt
  management.
- `src/` – VS Code extension source code. When activated, the
  `Debug with AI Copilot` command collects modified files, an error log and
  recent changes from the user, then posts the data to the backend and
  displays the AI’s response in a WebView.
- `demo_repo/` – A minimal Python project with a circular import bug and
  corresponding tests. It is used to demonstrate the end‑to‑end
  workflow.
- `run_demo.sh` – Shell script that runs the demo: it starts the backend,
  installs the demo’s dependencies, runs the failing tests, sends the
  error log and files to the backend, applies the returned patch, and
  reruns the tests to verify the fix.

## Running the demo

The following steps illustrate how to execute the demo on a Unix‑like
system. Ensure you have Python and `pip` installed. Within the project
root, run:

```bash
chmod +x run_demo.sh
./run_demo.sh
```

The script will:

1. Launch the FastAPI backend on `localhost:8000`.
2. Execute the tests in `demo_repo/tests`. They will initially fail due to a
   circular import.
3. Capture the error log and package the affected files into a JSON
   payload which is sent to the `/diagnose` endpoint.
4. Receive a proposed patch from the AI (simulated) and apply it to the
   repository.
5. Rerun the tests. They should pass after the patch is applied.
6. Shut down the backend server.

## Running the demo on Windows (PowerShell)

If you are on Windows, use the provided `run_demo.ps1` script:

```powershell
# From the project root
powershell -ExecutionPolicy Bypass -File .\run_demo.ps1 -Port 8000
```

The script performs the same steps as `run_demo.sh`:
1. Launches the FastAPI backend on `localhost:8000` in a background job.
2. Executes failing unit tests in `demo_repo` to generate `error.log`.
3. Builds the payload (`payload.json`) and calls the `/diagnose` endpoint.
4. Saves any returned patch to `patch.diff` and attempts to apply it.
5. Reruns the tests to verify the fix.
6. Stops the backend.

Ensure you have installed the Python dependencies first:

```powershell
python -m pip install -r requirements.txt
```

If you do not have execution-policy permissions, you can copy-paste the commands inside `run_demo.ps1` into an interactive shell.

## Caveats

This proof‑of‑concept uses a simulated AI response when no OpenAI API key
is provided. The simulation includes simple heuristics to detect circular
imports and propose an appropriate fix, but does not represent real model
capabilities. To use real models, set the `OPENAI_API_KEY` environment
variable before launching the backend.

## Pre‑commit hooks

To keep the codebase clean and consistent, this repository includes a
[pre‑commit](https://pre-commit.com/) configuration. The hooks run
formatters and linters on staged files before each commit. The tools used are:

- **Black** for Python code formatting.
- **isort** for sorting Python imports.
- **Ruff** for Python linting and automatic fixes.
- **Prettier** for formatting TypeScript and HTML files.

To install and enable the hooks locally:

```bash
pip install pre-commit
pre-commit install
# Optionally run on all files to check the current state
pre-commit run --all-files
```

In addition, a GitHub Actions workflow will run the pre‑commit hooks on
every pull request and push to `main`.