@echo off
setlocal
start "Yuzme AI Backend" powershell.exe -NoExit -ExecutionPolicy Bypass -File "%~dp0start_all.ps1"
endlocal