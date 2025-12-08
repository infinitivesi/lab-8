# Start dev server using venv python without needing to execute Activate.ps1
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$venvPython = Join-Path $scriptDir "venv\Scripts\python.exe"
if (Test-Path $venvPython) {
    & $venvPython (Join-Path $scriptDir "app.py") @args
} else {
    Write-Error "venv python not found. Create the venv first: python -m venv venv"
    exit 1
}
