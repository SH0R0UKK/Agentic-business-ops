@echo off
echo ========================================
echo Starting Agentic Business Ops API Server
echo ========================================
echo.
echo Server will run on: http://localhost:8000
echo API Docs will be at: http://localhost:8000/docs
echo.
echo Press CTRL+C to stop the server
echo ========================================
echo.

cd /d "%~dp0.."
python -m uvicorn backend.api:app --host 127.0.0.1 --port 8000 --reload

pause
