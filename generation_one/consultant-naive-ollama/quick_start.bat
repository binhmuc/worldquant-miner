@echo off
REM ============================================================================
REM Quick Start Script - WorldQuant Alpha Mining
REM ============================================================================
REM This is the fastest way to get started. Run this first!
REM ============================================================================

echo.
echo ========================================
echo  WorldQuant Alpha Mining
echo  Quick Start
echo ========================================
echo.

REM Check if already set up
if exist "venv\" (
    if exist "cookie.txt" (
        echo Setup detected! Starting application...
        echo.
        call run_local.bat
        exit /b 0
    )
)

REM First time setup
echo This appears to be your first time running the application.
echo Let's get you set up!
echo.
pause

REM Run setup
echo.
echo Running setup...
echo.
call setup_local.bat

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next: Run the application
echo.
pause

REM Run the application
call run_local.bat
