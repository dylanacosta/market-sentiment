#!/usr/bin/env python3
"""
Market Sentiment Dashboard Launcher
Simple Python script to launch the dashboard with automatic setup
"""

import os
import sys
import subprocess
import glob
from pathlib import Path

def check_virtual_env():
    """Check if virtual environment is activated."""
    return hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

def install_dependencies():
    """Install required dependencies."""
    print("📦 Installing dependencies...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "-r", "requirements/requirements-core.txt",
            "-r", "requirements/requirements-data.txt", 
            "-r", "requirements/requirements-app.txt"
        ], check=True)
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_data():
    """Check if CSV data exists, scrape if needed."""
    csv_files = glob.glob("share/outputs/*.csv")
    if not csv_files:
        print("📊 No data found. Running initial scrape...")
        try:
            result = subprocess.run([sys.executable, "main.py"], 
                                 capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Initial data scraped successfully!")
                return True
            else:
                print(f"⚠️  Scraping failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error during scraping: {e}")
            return False
    else:
        print(f"✅ Found {len(csv_files)} CSV file(s)")
        return True

def launch_dashboard():
    """Launch the Streamlit dashboard."""
    print("🌐 Launching dashboard...")
    print("Dashboard will open at: http://localhost:8501")
    print("Press Ctrl+C to stop the dashboard")
    print()
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")

def main():
    """Main launcher function."""
    print("🚀 Market Sentiment Dashboard Launcher")
    print("======================================")
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Check if we're in a virtual environment
    if not check_virtual_env():
        print("⚠️  Not in a virtual environment. Attempting to activate...")
        # Try to activate virtual environment
        if os.path.exists("bin/activate"):
            print("🔧 Please run: source bin/activate && python launch.py")
            return
        elif os.path.exists("Scripts/activate.bat"):
            print("🔧 Please run: Scripts\\activate.bat && python launch.py")
            return
    
    # Install dependencies if needed
    try:
        import streamlit, pandas, plotly
        print("✅ Dependencies already installed")
    except ImportError:
        if not install_dependencies():
            return
    
    # Check for data
    if not check_data():
        print("⚠️  No data available, but continuing with dashboard...")
    
    # Launch dashboard
    launch_dashboard()

if __name__ == "__main__":
    main()
