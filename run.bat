@echo off
echo Starting UniMarket Application...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt

REM Create uploads directory if it doesn't exist
if not exist "uploads" (
    mkdir uploads
)

echo.
echo Starting Flask application...
echo Visit http://localhost:5000 in your browser
echo Press Ctrl+C to stop the application
echo.

python app.py
