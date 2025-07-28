#!/bin/bash
set -euo pipefail

# Run the AI Debugging Copilot demo on the sample repository.
#
# This script performs the following steps:
#   1. Starts the FastAPI backend in the background.
#   2. Installs the demo repository requirements (pytest).
#   3. Runs the failing tests to capture the error log.
#   4. Builds a JSON payload with compressed file contents and the error log.
#   5. Sends the payload to the /diagnose endpoint and retrieves a patch.
#   6. Applies the patch to the repo.
#   7. Reruns tests to verify the fix.
#   8. Shuts down the backend server.

# Determine repo root
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
DEMO_DIR="$ROOT_DIR/demo_repo"

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
DEMO_DIR="$ROOT_DIR/demo_repo"

echo "Starting backend server..."
echo "Starting backend server..."
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 &
SERVER_PID=$!

# Ensure we stop the server on exit
trap 'echo "Stopping backend server..."; kill $SERVER_PID' EXIT

sleep 2  # give the server a moment to start

cd "$DEMO_DIR"

# Run tests expecting a failure and capture the error log
echo "Running failing tests..."
# Use unittest to run the demo tests; failures are expected due to circular import
python -m unittest discover -s tests 2>&1 | tee /tmp/error.log || true

# Build JSON payload using Python: compress files and include error log
echo "Building diagnostic payload..."
python - <<'PY'
import base64, gzip, json, sys, os, pathlib

repo_dir = os.environ.get('DEMO_REPO', '.')
files = []
for rel_path in ['src/auth/user.py', 'src/auth/login.py']:
    abs_path = os.path.join(repo_dir, rel_path)
    with open(abs_path, 'rb') as f:
        content = f.read()
    encoded = base64.b64encode(gzip.compress(content)).decode()
    files.append({'filename': rel_path, 'content': encoded})
with open('/tmp/error.log', 'r') as f:
    error_log = f.read()
payload = {
    'files': files,
    'error_log': error_log,
    'summary': 'Attempting to fix circular import in demo'
}
with open('/tmp/payload.json', 'w') as out:
    json.dump(payload, out)
PY

# Send the payload to the diagnose endpoint and save the response
echo "Calling /diagnose endpoint..."
curl -s -X POST -H "Content-Type: application/json" --data @/tmp/payload.json http://127.0.0.1:8000/diagnose -o /tmp/response.json

# Extract patch
echo "Extracting patch from response..."
python - <<'PY'
import json, sys, os
resp = json.load(open('/tmp/response.json'))
patches = resp.get('patches') or []
if patches:
    with open('/tmp/patch.diff', 'w') as f:
        f.write("\n\n".join(patches))
    print("Patch saved to /tmp/patch.diff")
else:
    print("No patch returned.")
PY


# Apply the patch if it exists. Instead of relying on the external `patch` utility
# (which may not be available in restricted environments), we implement a
# minimal patch application in Python. This script supports simple unified
# diffs where each hunk contains only additions and deletions (no context
# lines). It removes any line prefaced with '-' from the target file and
# inserts lines prefaced with '+' at the same location.
if [ -s /tmp/patch.diff ]; then
    echo "Applying patch via Python..."
    python - <<'PY'
import os
import sys

patch_path = '/tmp/patch.diff'
if not os.path.exists(patch_path) or os.path.getsize(patch_path) == 0:
    sys.exit(0)
with open(patch_path, 'r') as pf:
    diff_content = pf.read().split('--- a/')
for chunk in diff_content[1:]:
    lines = chunk.splitlines()
    # Determine target file from +++ line
    target = None
    for ln in lines:
        if ln.startswith('+++ b/'):
            target = ln[6:]
            break
    if not target:
        continue
    # Collect removed and added lines
    remove_lines = []
    add_lines = []
    for ln in lines:
        if ln.startswith('@@'):
            continue
        if ln.startswith('-') and not ln.startswith('---'):
            remove_lines.append(ln[1:])
        elif ln.startswith('+') and not ln.startswith('+++'):
            add_lines.append(ln[1:])
    # Read file content
    if not os.path.exists(target):
        # Try removing a possible prefix like 'b/' or similar
        alt_target = target.lstrip('b/')
        if os.path.exists(alt_target):
            target = alt_target
        else:
            print(f"[WARN] Target file {target} not found, skipping.")
            continue
    with open(target, 'r') as f:
        content = f.readlines()
    # Find indices of lines to remove
    indices = []
    for r in remove_lines:
        for idx, line in enumerate(content):
            # Remove lines that exactly match the removal line or start with it (allowing trailing comments)
            stripped = line.rstrip('\n')
            if stripped == r or stripped.startswith(r + ' '):
                indices.append(idx)
                break
    if indices:
        index = indices[0]
        for idx in sorted(indices, reverse=True):
            content.pop(idx)
        # Insert added lines at the position of the first removed line
        for offset, add_line in enumerate(add_lines):
            content.insert(index + offset, add_line + '\n')
        with open(target, 'w') as f:
            f.writelines(content)
        print(f"Applied patch to {target}")
    else:
        print(f"[WARN] No matching lines to remove in {target}, skipping.")
PY
else
    echo "No patch to apply."
fi

echo "Re-running tests after applying patch..."
python -m unittest discover -s tests

echo "Demo complete."