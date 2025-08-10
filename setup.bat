@echo off
echo Setting up Frame Extractor...
echo Creating virtual environment...

if exist "venv" (
    echo Virtual environment already exists. Removing old one...
    rmdir /s /q venv
)

python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo Setup complete!
echo Run 'run.bat' to start the application.
pause
