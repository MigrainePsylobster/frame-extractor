@echo off
echo Testing GPU compatibility...

if not exist "venv" (
    echo Virtual environment not found. Please run setup.bat first.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
python test_gpu.py

echo.
echo GPU test completed.
pause
