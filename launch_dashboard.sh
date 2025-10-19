#!/bin/bash

# Market Sentiment Dashboard Launcher
# This script activates the virtual environment and launches the Streamlit dashboard

echo "🚀 Starting Market Sentiment Dashboard..."
echo "========================================"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "bin" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python -m venv . && source bin/activate && pip install -r requirements/requirements-core.txt -r requirements/requirements-data.txt -r requirements/requirements-app.txt"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source bin/activate

# Check if required packages are installed
echo "📦 Checking dependencies..."
python -c "import streamlit, pandas, plotly" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Missing dependencies! Installing..."
    pip install -r requirements/requirements-core.txt -r requirements/requirements-data.txt -r requirements/requirements-app.txt
fi

# Check if CSV data exists
if [ ! -d "share/outputs" ] || [ -z "$(ls -A share/outputs/*.csv 2>/dev/null)" ]; then
    echo "📊 No data found. Running initial scrape..."
    python main.py
    if [ $? -eq 0 ]; then
        echo "✅ Initial data scraped successfully!"
    else
        echo "⚠️  Scraping failed, but continuing with dashboard..."
    fi
fi

# Launch Streamlit dashboard
echo "🌐 Launching dashboard..."
echo "Dashboard will open at: http://localhost:8501 (or 8502 if 8501 is busy)"
echo "Press Ctrl+C to stop the dashboard"
echo ""

# Try port 8501 first, fallback to 8502
streamlit run app.py --server.port 8501 || streamlit run app.py --server.port 8502
