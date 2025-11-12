@echo off
REM Windows one-command bootstrapper: runs PowerShell setup with policy bypass
setlocal

REM Resolve repo root (directory of this script)
set SCRIPT_DIR=%~dp0

REM Run PowerShell setup with no profile and bypassed execution policy
powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%scripts\setup.ps1" %*

endlocal

