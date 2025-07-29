# Requires PowerShell 5+
param(
    [string]$Port = "8000"
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$DemoDir = Join-Path $Root "demo_repo"

Write-Host "Starting FastAPI backend on port $Port..." -ForegroundColor Cyan
# Launch backend as background job
Start-Job -ScriptBlock { param($root,$p)
    Set-Location $root
    python -m uvicorn app.main:app --host 127.0.0.1 --port $p
} -ArgumentList $Root,$Port | Out-Null

Start-Sleep -Seconds 2

Write-Host "Running failing tests to capture error log..." -ForegroundColor Cyan
Set-Location $DemoDir
python -m unittest discover -s tests 2>&1 | Tee-Object -FilePath error.log | Out-Null

# Build JSON payload via embedded Python
Write-Host "Building diagnostic payload..." -ForegroundColor Cyan
$py = @'
import base64, gzip, json, os, pathlib, sys
repo = pathlib.Path(os.getenv("DEMO_REPO", "."))
files = []
for rel in ["src/auth/user.py", "src/auth/login.py"]:
    raw = (repo / rel).read_bytes()
    files.append({
        "filename": rel,
        "content": base64.b64encode(gzip.compress(raw)).decode(),
    })
error_log = (repo / "error.log").read_text()
payload = {"files": files, "error_log": error_log, "summary": "Attempting to fix circular import in demo"}
with open("payload.json", "w") as fh:
    json.dump(payload, fh)
'@
python - << $py

# Send diagnose request
Write-Host "Calling /diagnose endpoint..." -ForegroundColor Cyan
Invoke-RestMethod -Method Post -ContentType "application/json" -InFile "payload.json" -Uri "http://127.0.0.1:$Port/diagnose" -OutFile "response.json"

# Extract patch via embedded Python
$pyPatch = @'
import json, pathlib, sys
resp = json.load(open("response.json"))
patches = resp.get("patches") or []
if patches:
    pathlib.Path("patch.diff").write_text("\n\n".join(patches))
    print("Patch saved to patch.diff")
else:
    print("No patch returned")
'@
python - << $pyPatch

# Apply patch (very minimal, uses python logic from Bash script)
if (Test-Path "patch.diff" -PathType Leaf) {
    Write-Host "Applying patch..." -ForegroundColor Cyan
    $pyApply = Get-Content -Raw run_demo.sh | Select-String -Pattern "minimal patch application in Python" -Context 0,200 | ForEach-Object { $_.Line }
    if (-not $pyApply) {
        Write-Warning "Could not locate patch application logic; skipping auto-apply."
    }
}

Write-Host "Re-running tests after patch..." -ForegroundColor Cyan
python -m unittest discover -s tests

Write-Host "Demo complete." -ForegroundColor Green

# Cleanup backend job
Get-Job | Stop-Job | Remove-Job -Force