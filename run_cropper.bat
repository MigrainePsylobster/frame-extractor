@echo off
echo Starting Video Cropper - RTX 5000 Series Optimized...
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found. Please run setup.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found in virtual environment.
    echo Please run setup.bat to configure the environment.
    pause
    exit /b 1
)

REM Start the video cropper application
echo Launching Video Cropper GUI...
python video_cropper.py

REM Keep window open if there's an error
if %errorlevel% neq 0 (
    echo.
    echo Application exited with error code %errorlevel%
    pause
)
