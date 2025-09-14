#!/bin/bash
echo "Starting UniMarket Application..."
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Create uploads directory if it doesn't exist
if [ ! -d "uploads" ]; then
    mkdir uploads
fi

echo
echo "Starting Flask application..."
echo "Visit http://localhost:5000 in your browser"
echo "Press Ctrl+C to stop the application"
echo

python app.py
