@echo off
echo Starting Frame Extractor...

if not exist "venv" (
    echo Virtual environment not found. Please run setup.bat first.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
python main.py

pause
