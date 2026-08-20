@echo off
echo ========================================
echo   Second Brain API - Starting...
echo ========================================
echo.

if not exist venv (
    echo [ERROR] Virtual environment not found. Run setup.bat first.
    pause
    exit /b
)

call venv\Scripts\activate.bat
uvicorn api:app --host 0.0.0.0 --port 8000

pause
