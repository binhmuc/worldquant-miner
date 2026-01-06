@echo off
REM ============================================================================
REM WorldQuant Alpha Mining - Local Setup Script (Windows)
REM ============================================================================
REM This script sets up the environment for running locally without Docker
REM ============================================================================

setlocal enabledelayedexpansion

echo ============================================================================
echo WorldQuant Alpha Mining - Local Setup
echo ============================================================================
echo.

REM Check if Python is installed
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)
echo [OK] Python is installed
python --version

REM Check if pip is available
echo.
echo [2/6] Checking pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip is not installed
    echo Installing pip...
    python -m ensurepip --default-pip
)
echo [OK] pip is available

REM Create virtual environment
echo.
echo [3/6] Creating virtual environment...
if exist "venv\" (
    echo Virtual environment already exists
    choice /C YN /M "Do you want to recreate it"
    if errorlevel 2 goto skip_venv
    echo Removing old virtual environment...
    rmdir /s /q venv
)

python -m venv venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment created

:skip_venv

REM Activate virtual environment
echo.
echo [4/6] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment activated

REM Install dependencies
echo.
echo [5/6] Installing Python dependencies...
echo This may take a few minutes...
echo.
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed successfully

REM Create necessary directories
echo.
echo [6/6] Creating directories...
if not exist "results\" mkdir results
if not exist "logs\" mkdir logs
echo [OK] Directories created

REM Check Ollama
echo.
echo ============================================================================
echo Checking Ollama Installation
echo ============================================================================
echo.

REM Check if Ollama is installed
where ollama >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Ollama command not found in PATH
    echo.
    echo Please install Ollama from:
    echo https://ollama.com/download
    echo.
    echo After installation, restart this script.
    pause
    exit /b 1
) else (
    echo [OK] Ollama is installed
    ollama --version
)

REM Check if Ollama is running
echo.
echo Checking if Ollama is running...
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Ollama service is not running
    echo.
    echo Starting Ollama service...
    start "Ollama Service" ollama serve
    timeout /t 3 /nobreak >nul

    curl -s http://localhost:11434/api/tags >nul 2>&1
    if errorlevel 1 (
        echo [WARNING] Could not connect to Ollama
        echo.
        echo Please manually start Ollama:
        echo   1. Open Command Prompt as Administrator
        echo   2. Run: ollama serve
        echo.
    ) else (
        echo [OK] Ollama is now running
    )
) else (
    echo [OK] Ollama is running on http://localhost:11434
)

REM Check for models
echo.
echo Checking installed Ollama models...
ollama list
echo.

REM Check for cookie.txt
echo.
echo ============================================================================
echo Checking Authentication
echo ============================================================================
echo.

if not exist "cookie.txt" (
    echo [WARNING] cookie.txt not found
    echo.
    echo You need to create cookie.txt with your WorldQuant Brain cookies.
    echo.
    echo Quick Guide:
    echo   1. Open https://platform.worldquantbrain.com in your browser
    echo   2. Login to your account
    echo   3. Press F12 to open Developer Tools
    echo   4. Go to Application ^> Cookies ^> https://platform.worldquantbrain.com
    echo   5. Copy all cookies in format: key1=value1; key2=value2; ...
    echo   6. Paste into cookie.txt file in this directory
    echo.
    echo See COOKIE_AUTH.md for detailed instructions.
    echo.

    choice /C YN /M "Do you want to open COOKIE_AUTH.md now"
    if not errorlevel 2 (
        if exist "COOKIE_AUTH.md" (
            start COOKIE_AUTH.md
        ) else (
            echo COOKIE_AUTH.md not found
        )
    )
) else (
    echo [OK] cookie.txt found
    echo.
    echo Testing cookie file...
    for /f "delims=" %%i in (cookie.txt) do set cookie_content=%%i
    if "!cookie_content!"=="" (
        echo [ERROR] cookie.txt is empty
        echo Please add your cookie string to cookie.txt
    ) else (
        echo [OK] cookie.txt contains data ^(length: !cookie_content:~0,50!...^)
    )
)

REM Final summary
echo.
echo ============================================================================
echo Setup Complete!
echo ============================================================================
echo.
echo Next steps:
echo.
echo   1. Make sure cookie.txt contains your WorldQuant Brain cookies
echo      - See COOKIE_AUTH.md for instructions
echo.
echo   2. Ensure Ollama is running with models installed:
echo      - Run: ollama list
echo      - Install models: ollama pull deepseek-r1:8b
echo.
echo   3. Run the application:
echo      - Run: run_local.bat
echo      - Or directly: python alpha_orchestrator.py
echo.
echo ============================================================================
echo.

REM Offer to install models
choice /C YN /M "Do you want to install recommended Ollama models now"
if not errorlevel 2 (
    echo.
    echo Installing recommended models for RTX A4000 (16GB VRAM)...
    echo This will download several GB of data. It may take a while.
    echo.

    choice /C YN /M "Install deepseek-r1:8b (5.2GB)"
    if not errorlevel 2 ollama pull deepseek-r1:8b

    choice /C YN /M "Install deepseek-r1:7b (4.7GB)"
    if not errorlevel 2 ollama pull deepseek-r1:7b

    choice /C YN /M "Install qwen2.5-coder:7b (4.7GB)"
    if not errorlevel 2 ollama pull qwen2.5-coder:7b

    choice /C YN /M "Install llama3.2:3b (2.0GB)"
    if not errorlevel 2 ollama pull llama3.2:3b

    choice /C YN /M "Install gemma2:2b (1.6GB)"
    if not errorlevel 2 ollama pull gemma2:2b

    echo.
    echo [OK] Models installed
    echo.
    echo View installed models:
    ollama list
)

echo.
echo Setup is complete! You can now run: run_local.bat
echo.
pause

endlocal
