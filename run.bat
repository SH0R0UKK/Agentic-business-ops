@echo off
REM ============================================================
REM Agentic Business Ops - Startup Script (Windows Batch)
REM ============================================================
REM Double-click this file to start both backend and frontend
REM ============================================================

echo ============================================================
echo   Agentic Business Ops - Starting Services
echo ============================================================
echo.

REM Get the directory where this script is located
set PROJECT_ROOT=%~dp0

echo [1/2] Starting Backend API on http://localhost:8000...
start "Backend API" cmd /k "cd /d %PROJECT_ROOT% && call venv\Scripts\activate.bat && python -m uvicorn backend.api:app --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak > nul

echo [2/2] Starting Frontend on http://localhost:3000...
start "Frontend" cmd /k "cd /d %PROJECT_ROOT%frontend\AI_Co-pilot && pnpm dev"

echo.
echo ============================================================
echo   All services started!
echo ============================================================
echo.
echo   Backend API:  http://localhost:8000
echo   API Docs:     http://localhost:8000/docs
echo   Frontend:     http://localhost:3000
echo   Startup Hub:  http://localhost:3000/startup-hub
echo.
echo   Press any key to open the Startup Hub in your browser...
pause > nul

start http://localhost:3000/startup-hub
