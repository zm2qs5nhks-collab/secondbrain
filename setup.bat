@echo off
echo ========================================
echo   Second Brain - Environment Setup
echo ========================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 goto :auto_install

for /f "tokens=2" %%a in ('python --version 2^>^&1') do set PYVER=%%a
echo Found Python %PYVER%

for /f "tokens=1,2 delims=." %%a in ("%PYVER%") do set PYMAJ=%%a & set PYMIN=%%b
if %PYMAJ% gtr 3 goto :version_high
if %PYMAJ% equ 3 if %PYMIN% gtr 12 goto :version_high
goto :install

:version_high
echo [WARNING] Python %PYVER% is too new, some packages may not be compatible.
echo Auto-installing Python 3.10.11 instead...
goto :download

:auto_install
echo Python not found. Auto-installing Python 3.10.11...

:download
echo Downloading installer...
set PYTHON_URL=https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe
set INSTALLER=%TEMP%\python-3.10.11-amd64.exe

curl -fsSL -o "%INSTALLER%" "%PYTHON_URL%"
if %errorlevel% neq 0 (
    echo [ERROR] Download failed. Please install Python manually:
    echo   1. Visit https://www.python.org/downloads/
    echo   2. Download and install Python 3.10.11
    echo   3. Re-run this script
    start https://www.python.org/downloads/release/python-31011/
    pause
    exit /b
)

echo Installing Python 3.10.11 (this may take a minute)...
"%INSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 TargetDir=%LOCALAPPDATA%\Programs\Python\Python310
set "PATH=%LOCALAPPDATA%\Programs\Python\Python310;%LOCALAPPDATA%\Programs\Python\Python310\Scripts;%PATH%"
python --version
echo Python installation complete.
echo.

:install
if not exist venv (
    echo [1/3] Creating virtual environment...
    python -m venv venv
) else (
    echo [1/3] Virtual environment already exists, skipping
)

call venv\Scripts\activate.bat

echo [2/3] Installing dependencies (first time takes a few minutes)...
pip install -r requirements.txt -q

echo [3/3] Checking config file...
if not exist .env (
    copy .env.example .env >nul
    echo   Created .env file, please edit it with your API Key
) else (
    echo   .env file already exists
)

echo.
echo ========================================
echo   Setup complete!
echo ========================================
echo.
echo Next steps:
echo   1. Double-click start.bat to launch
echo.
pause
