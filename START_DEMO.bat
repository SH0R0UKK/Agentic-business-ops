@echo off
echo ========================================
echo AGENTIC BUSINESS OPS - FULL STACK DEMO
echo ========================================
echo.
echo Starting Backend API and Frontend UI...
echo.

cd /d "%~dp0"

:: Start Backend API in new window
echo [1/2] Starting Backend API Server...
start "Backend API - Port 8000" cmd /k "python -m uvicorn backend.api:app --host 127.0.0.1 --port 8000"
timeout /t 5 /nobreak >nul

:: Start Streamlit UI in new window
echo [2/2] Starting Professional Streamlit UI...
start "Streamlit UI - Port 8501" cmd /k "python -m streamlit run streamlit_professional_ui.py"
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo ✅ SYSTEM STARTED!
echo ========================================
echo.
echo Backend API: http://localhost:8000
echo API Docs:    http://localhost:8000/docs
echo Frontend UI: http://localhost:8501
echo.
echo Press any key to open the UI in your browser...
pause >nul

start http://localhost:8501

echo.
echo Close this window or press CTRL+C to stop all servers.
pause
