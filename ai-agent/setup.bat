@echo off
REM Setup script for Multi-Agent AI Coding System (Windows)

echo ==================================================
echo Multi-Agent AI Coding System - Setup
echo ==================================================
echo.

REM Check Python version
echo Checking Python version...
python --version
if %errorlevel% neq 0 (
    echo Python not found! Please install Python 3.8+
    exit /b 1
)

REM Install dependencies
echo.
echo Installing dependencies...
pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo [32mDependencies installed successfully[0m
) else (
    echo [31mFailed to install dependencies[0m
    exit /b 1
)

REM Check for .env file
echo.
if exist .env (
    echo [32m.env file found[0m
) else (
    echo [33m.env file not found[0m
    echo Creating .env from template...
    copy .env.example .env
    echo Please edit .env with your AWS credentials
)

REM Run system tests
echo.
echo Running system tests...
python test_system.py

if %errorlevel% equ 0 (
    echo.
    echo ==================================================
    echo [32mSetup Complete![0m
    echo ==================================================
    echo.
    echo Next steps:
    echo 1. Edit .env with your AWS credentials (if not done^)
    echo 2. Run: python main.py
    echo 3. Start chatting with the AI agents!
    echo.
    echo Documentation:
    echo   - README.md - Full documentation
    echo   - QUICKSTART.md - Quick start guide
    echo   - ARCHITECTURE.md - Technical details
    echo.
) else (
    echo.
    echo [33mSome tests failed. Please check the output above.[0m
    echo You may need to set AWS credentials.
)

pause
