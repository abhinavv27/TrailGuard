Write-Host "Starting TrailGuard AI..." -ForegroundColor Cyan
Write-Host "Terminal 1: Backend on :8000"
Write-Host "Terminal 2: Frontend on :3000"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path

# Start backend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\services\api'; uvicorn app.main:app --reload --port 8000"
Start-Sleep 2
# Start frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\apps\web'; npm run dev"

Write-Host "Both servers starting..." -ForegroundColor Green
