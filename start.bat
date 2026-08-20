@echo off

if not exist venv (
    echo [ERROR] Virtual environment not found. Run setup.bat first.
    pause
    exit /b
)

if not exist .env (
    echo [ERROR] .env file not found.
    pause
    exit /b
)

echo ========================================
echo   Second Brain - Starting...
echo   Browser will open at localhost:8501
echo ========================================

call venv\Scripts\activate.bat
streamlit run app.py --server.port 8501

pause
