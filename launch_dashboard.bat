@echo off
REM Market Sentiment Dashboard Launcher for Windows
REM This script activates the virtual environment and launches the Streamlit dashboard

echo 🚀 Starting Market Sentiment Dashboard...
echo ========================================

REM Get the directory where this script is located
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "Scripts" (
    echo ❌ Virtual environment not found!
    echo Please run: python -m venv . ^&^& Scripts\activate ^&^& pip install -r requirements\requirements-core.txt -r requirements\requirements-data.txt -r requirements\requirements-app.txt
    pause
    exit /b 1
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call Scripts\activate.bat

REM Check if required packages are installed
echo 📦 Checking dependencies...
python -c "import streamlit, pandas, plotly" 2>nul
if errorlevel 1 (
    echo ❌ Missing dependencies! Installing...
    pip install -r requirements\requirements-core.txt -r requirements\requirements-data.txt -r requirements\requirements-app.txt
)

REM Check if CSV data exists
if not exist "share\outputs" (
    echo 📊 No data found. Running initial scrape...
    python main.py
    if errorlevel 1 (
        echo ⚠️  Scraping failed, but continuing with dashboard...
    ) else (
        echo ✅ Initial data scraped successfully!
    )
) else (
    dir /b share\outputs\*.csv >nul 2>&1
    if errorlevel 1 (
        echo 📊 No CSV files found. Running initial scrape...
        python main.py
        if errorlevel 1 (
            echo ⚠️  Scraping failed, but continuing with dashboard...
        ) else (
            echo ✅ Initial data scraped successfully!
        )
    )
)

REM Launch Streamlit dashboard
echo 🌐 Launching dashboard...
echo Dashboard will open at: http://localhost:8501
echo Press Ctrl+C to stop the dashboard
echo.

streamlit run app.py
