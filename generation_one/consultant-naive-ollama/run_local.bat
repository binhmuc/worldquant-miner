@echo off
REM ============================================================================
REM WorldQuant Alpha Mining - Local Execution Script (Windows)
REM ============================================================================
REM This script runs the alpha mining system locally without Docker
REM Prerequisites:
REM   - Ollama installed and running (http://localhost:11434)
REM   - Python 3.8+ installed
REM   - cookie.txt file with your WorldQuant Brain cookies
REM ============================================================================

setlocal enabledelayedexpansion

echo ============================================================================
echo WorldQuant Alpha Mining - Local Execution
echo ============================================================================
echo.

REM Set color output if available
color 0A

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python is installed
python --version

REM Check if Ollama is running
echo.
echo Checking Ollama service...
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Ollama is not running on http://localhost:11434
    echo.
    echo Please start Ollama first:
    echo   1. Open Command Prompt as Administrator
    echo   2. Run: ollama serve
    echo   3. Or start Ollama from Start Menu
    echo.
    choice /C YN /M "Do you want to continue anyway"
    if errorlevel 2 exit /b 1
) else (
    echo [OK] Ollama is running on http://localhost:11434
)

REM Check if cookie.txt exists
echo.
echo Checking authentication...
if not exist "cookie.txt" (
    echo [WARNING] cookie.txt not found
    echo.
    echo Please create cookie.txt with your WorldQuant Brain cookies.
    echo See COOKIE_AUTH.md for instructions.
    echo.
    choice /C YN /M "Do you want to continue anyway (you will be prompted)"
    if errorlevel 2 exit /b 1
) else (
    echo [OK] cookie.txt found
)

REM Check if virtual environment exists
echo.
echo Checking Python environment...
if not exist "venv\" (
    echo [INFO] Virtual environment not found. Creating one...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)

REM Check if requirements are installed
echo.
echo Checking Python dependencies...
python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing Python dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
    echo [OK] Dependencies installed
) else (
    echo [OK] Dependencies already installed
)

REM Create necessary directories
echo.
echo Creating directories...
if not exist "results\" mkdir results
if not exist "logs\" mkdir logs
echo [OK] Directories ready

REM Display menu
:menu
echo.
echo ============================================================================
echo Select what to run:
echo ============================================================================
echo.
echo   1. Alpha Orchestrator (Main service - continuous mode)
echo   2. Alpha Orchestrator (Single batch mode)
echo   3. Machine Miner (Traditional mining)
echo   4. Web Dashboard (Port 5000)
echo   5. Health Check
echo   6. Alpha Expression Miner
echo   7. Run All Services (in separate windows)
echo   8. Install/Update Ollama Models
echo   9. Exit
echo.
set /p choice="Enter your choice (1-9): "

if "%choice%"=="1" goto orchestrator_continuous
if "%choice%"=="2" goto orchestrator_single
if "%choice%"=="3" goto machine_miner
if "%choice%"=="4" goto dashboard
if "%choice%"=="5" goto health_check
if "%choice%"=="6" goto expression_miner
if "%choice%"=="7" goto all_services
if "%choice%"=="8" goto install_models
if "%choice%"=="9" goto end
echo Invalid choice. Please try again.
goto menu

:orchestrator_continuous
echo.
echo ============================================================================
echo Starting Alpha Orchestrator (Continuous Mode)
echo ============================================================================
echo.
echo This will run continuous alpha generation and testing
echo Press Ctrl+C to stop
echo.
echo Logs: logs/alpha_orchestrator.log
echo Results: results/
echo.
python alpha_orchestrator.py --mode continuous --batch-size 2 --max-concurrent 2
goto end

:orchestrator_single
echo.
echo ============================================================================
echo Starting Alpha Orchestrator (Single Batch Mode)
echo ============================================================================
echo.
set /p batch_size="Enter batch size (default 10): "
if "%batch_size%"=="" set batch_size=10
echo.
echo Running single batch of %batch_size% alphas...
echo.
python alpha_orchestrator.py --mode single --batch-size %batch_size%
echo.
echo Batch complete!
pause
goto menu

:machine_miner
echo.
echo ============================================================================
echo Starting Machine Miner
echo ============================================================================
echo.
set /p region="Enter region (default USA): "
if "%region%"=="" set region=USA
set /p universe="Enter universe (default TOP3000): "
if "%universe%"=="" set universe=TOP3000
echo.
echo Mining alphas for %region% / %universe%...
echo Press Ctrl+C to stop
echo.
python machine_miner.py --credentials cookie.txt --region %region% --universe %universe%
goto end

:dashboard
echo.
echo ============================================================================
echo Starting Web Dashboard
echo ============================================================================
echo.
echo Dashboard will be available at: http://localhost:5000
echo Press Ctrl+C to stop
echo.
start http://localhost:5000
python web_dashboard.py
goto end

:health_check
echo.
echo ============================================================================
echo Running Health Check
echo ============================================================================
echo.
python health_check.py
echo.
pause
goto menu

:expression_miner
echo.
echo ============================================================================
echo Starting Alpha Expression Miner
echo ============================================================================
echo.
set /p interval="Enter mining interval in hours (default 6): "
if "%interval%"=="" set interval=6
echo.
echo Mining expressions every %interval% hours...
echo Press Ctrl+C to stop
echo.
python alpha_expression_miner_continuous.py --credentials cookie.txt --mining-interval %interval%
goto end

:all_services
echo.
echo ============================================================================
echo Starting All Services
echo ============================================================================
echo.
echo Opening separate windows for each service...
echo.

REM Start Alpha Orchestrator
start "Alpha Orchestrator" cmd /k "call venv\Scripts\activate.bat && python alpha_orchestrator.py --mode continuous --batch-size 2 --max-concurrent 2"

REM Wait a bit
timeout /t 2 /nobreak >nul

REM Start Machine Miner
start "Machine Miner" cmd /k "call venv\Scripts\activate.bat && python machine_miner.py --credentials cookie.txt --region USA --universe TOP3000"

REM Wait a bit
timeout /t 2 /nobreak >nul

REM Start Web Dashboard
start "Web Dashboard" cmd /k "call venv\Scripts\activate.bat && python web_dashboard.py"

REM Wait a bit
timeout /t 2 /nobreak >nul

REM Open browser
timeout /t 5 /nobreak >nul
start http://localhost:5000

echo.
echo [OK] All services started in separate windows
echo.
echo Services running:
echo   - Alpha Orchestrator (continuous mode)
echo   - Machine Miner (USA/TOP3000)
echo   - Web Dashboard (http://localhost:5000)
echo.
echo Close each window to stop that service.
echo.
pause
goto menu

:install_models
echo.
echo ============================================================================
echo Install/Update Ollama Models
echo ============================================================================
echo.
echo Recommended models for RTX A4000 (16GB VRAM):
echo.
echo   1. deepseek-r1:8b (5.2GB) - Best reasoning model
echo   2. deepseek-r1:7b (4.7GB) - Good reasoning model
echo   3. qwen2.5-coder:7b (4.7GB) - Code-focused
echo   4. llama3.2:3b (2.0GB) - Lightweight
echo   5. gemma2:2b (1.6GB) - Very lightweight
echo   6. Install all recommended models
echo   7. Back to main menu
echo.
set /p model_choice="Enter your choice (1-7): "

if "%model_choice%"=="1" (
    ollama pull deepseek-r1:8b
    pause
    goto install_models
)
if "%model_choice%"=="2" (
    ollama pull deepseek-r1:7b
    pause
    goto install_models
)
if "%model_choice%"=="3" (
    ollama pull qwen2.5-coder:7b
    pause
    goto install_models
)
if "%model_choice%"=="4" (
    ollama pull llama3.2:3b
    pause
    goto install_models
)
if "%model_choice%"=="5" (
    ollama pull gemma2:2b
    pause
    goto install_models
)
if "%model_choice%"=="6" (
    echo Installing all recommended models...
    ollama pull deepseek-r1:8b
    ollama pull deepseek-r1:7b
    ollama pull qwen2.5-coder:7b
    ollama pull llama3.2:3b
    ollama pull gemma2:2b
    echo [OK] All models installed
    pause
    goto install_models
)
if "%model_choice%"=="7" goto menu
echo Invalid choice
goto install_models

:end
echo.
echo ============================================================================
echo Exiting...
echo ============================================================================
endlocal
