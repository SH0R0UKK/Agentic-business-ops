# ============================================================
# Agentic Business Ops - Startup Script
# ============================================================
# This script starts both the backend and frontend servers
# 
# Usage: Right-click on this file and select "Run with PowerShell"
# Or run from terminal: .\run.ps1
# ============================================================

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Agentic Business Ops - Starting Services" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# --- 1. Start Backend ---
Write-Host "[1/2] Starting Backend API on http://localhost:8000..." -ForegroundColor Yellow

$backendScript = @"
cd '$ProjectRoot'
& '$ProjectRoot\venv\Scripts\Activate.ps1'
Write-Host 'Backend server starting...' -ForegroundColor Green
python -m uvicorn backend.api:app --host 0.0.0.0 --port 8000
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendScript

Write-Host "   Backend started in new window" -ForegroundColor Green
Start-Sleep -Seconds 3

# --- 2. Start Frontend ---
Write-Host "[2/2] Starting Frontend on http://localhost:3000..." -ForegroundColor Yellow

$frontendScript = @"
cd '$ProjectRoot\frontend\AI_Co-pilot'
Write-Host 'Frontend server starting...' -ForegroundColor Green
pnpm dev
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendScript

Write-Host "   Frontend started in new window" -ForegroundColor Green

# --- Done ---
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  All services started!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Backend API:  http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs:     http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Frontend:     http://localhost:3000" -ForegroundColor White
Write-Host "  Startup Hub:  http://localhost:3000/startup-hub" -ForegroundColor White
Write-Host ""
Write-Host "  Press any key to open the Startup Hub in your browser..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Start-Process "http://localhost:3000/startup-hub"
