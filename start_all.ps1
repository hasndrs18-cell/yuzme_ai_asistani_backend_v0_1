$ErrorActionPreference = "Stop"

$projectRoot = $PSScriptRoot
$backendCommand = "Set-Location -LiteralPath '$projectRoot'; .venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000"
$frontendRoot = Join-Path $projectRoot "frontend"
$frontendCommand = "Set-Location -LiteralPath '$frontendRoot'; npm.cmd run dev"

Start-Process powershell.exe -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command", $backendCommand
)

Start-Process powershell.exe -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command", $frontendCommand
)

Write-Host "Backend: http://localhost:8000"
Write-Host "Frontend: http://localhost:3000"