@echo off
REM Start dev server using venv python without activating PowerShell scripts
set "VENV=%~dp0venv\Scripts\python.exe"
if exist "%VENV%" (
  "%VENV%" "%~dp0app.py" %*
) else (
  echo venv python not found. Create venv first: python -m venv venv
  exit /b 1
)
