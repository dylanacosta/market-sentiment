#!/usr/bin/env python3
"""
Dependency Checker and Installer for Market Sentiment Dashboard
Checks if all required libraries are installed and installs missing ones
"""

import subprocess
import sys
import os
import importlib
from pathlib import Path

# Required packages with their import names and pip names
REQUIRED_PACKAGES = {
    # Core dependencies
    'pandas': 'pandas',
    'numpy': 'numpy',
    'requests': 'requests',
    'python-dotenv': 'dotenv',
    
    # Data processing
    'nltk': 'nltk',
    'vaderSentiment': 'vaderSentiment',
    
    # Web scraping
    'praw': 'praw',
    'prawcore': 'prawcore',
    
    # Dashboard
    'streamlit': 'streamlit',
    'plotly': 'plotly',
    'matplotlib': 'matplotlib',
    
    # Optional but recommended
    'watchdog': 'watchdog',
}

# NLTK data that needs to be downloaded
NLTK_DATA = [
    'punkt',
    'punkt_tab', 
    'stopwords',
    'vader_lexicon'
]

def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} is not supported. Please use Python 3.8+")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def check_package(package_name, import_name):
    """Check if a package is installed and importable."""
    try:
        importlib.import_module(import_name)
        return True
    except ImportError:
        return False

def install_package(package_name):
    """Install a package using pip."""
    try:
        print(f"📦 Installing {package_name}...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", package_name
        ], check=True, capture_output=True)
        print(f"✅ {package_name} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package_name}: {e}")
        return False

def check_nltk_data():
    """Check and download required NLTK data."""
    try:
        import nltk
        print("📚 Checking NLTK data...")
        
        for data_name in NLTK_DATA:
            try:
                nltk.data.find(f'tokenizers/{data_name}' if 'punkt' in data_name else f'corpora/{data_name}' if data_name == 'stopwords' else f'sentiment/{data_name}')
                print(f"✅ {data_name} already downloaded")
            except LookupError:
                print(f"📥 Downloading {data_name}...")
                nltk.download(data_name, quiet=True)
                print(f"✅ {data_name} downloaded")
        
        return True
    except Exception as e:
        print(f"❌ Error with NLTK data: {e}")
        return False

def check_requirements_files():
    """Check if requirements files exist and install from them."""
    requirements_files = [
        "requirements/requirements-core.txt",
        "requirements/requirements-data.txt", 
        "requirements/requirements-app.txt"
    ]
    
    print("📋 Checking requirements files...")
    for req_file in requirements_files:
        if os.path.exists(req_file):
            print(f"✅ Found {req_file}")
            try:
                print(f"📦 Installing from {req_file}...")
                subprocess.run([
                    sys.executable, "-m", "pip", "install", "-r", req_file
                ], check=True, capture_output=True)
                print(f"✅ Installed from {req_file}")
            except subprocess.CalledProcessError as e:
                print(f"⚠️  Warning: Could not install from {req_file}: {e}")
        else:
            print(f"⚠️  Warning: {req_file} not found")

def check_environment_file():
    """Check if .env file exists with Reddit credentials."""
    print("🔐 Checking environment configuration...")
    if os.path.exists('.env'):
        print("✅ .env file found")
        return True
    else:
        print("⚠️  .env file not found")
        print("📝 Creating template .env file...")
        env_template = """# Reddit API Credentials
# Get these from https://www.reddit.com/prefs/apps
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=market-sentiment/0.1 by your_reddit_username
"""
        with open('.env', 'w') as f:
            f.write(env_template)
        print("✅ Template .env file created")
        print("🔧 Please edit .env file with your Reddit API credentials")
        return False

def check_data_directory():
    """Check if data directories exist."""
    print("📁 Checking data directories...")
    directories = ['share/outputs', 'data_pipeline', 'main-pipeline']
    
    for directory in directories:
        if os.path.exists(directory):
            print(f"✅ {directory} exists")
        else:
            print(f"📁 Creating {directory}...")
            os.makedirs(directory, exist_ok=True)
            print(f"✅ {directory} created")

def main():
    """Main dependency checking function."""
    print("🚀 Market Sentiment Dashboard - Dependency Checker")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Check and install requirements files first
    check_requirements_files()
    
    # Check individual packages
    print("\n📦 Checking individual packages...")
    missing_packages = []
    
    for package_name, import_name in REQUIRED_PACKAGES.items():
        if check_package(package_name, import_name):
            print(f"✅ {package_name} is installed")
        else:
            print(f"❌ {package_name} is missing")
            missing_packages.append(package_name)
    
    # Install missing packages
    if missing_packages:
        print(f"\n📥 Installing {len(missing_packages)} missing packages...")
        for package in missing_packages:
            if not install_package(package):
                print(f"❌ Failed to install {package}")
                return False
    else:
        print("✅ All packages are installed")
    
    # Check NLTK data
    print("\n📚 Checking NLTK data...")
    if not check_nltk_data():
        print("⚠️  NLTK data check failed, but continuing...")
    
    # Check environment
    print("\n🔐 Checking environment...")
    env_ok = check_environment_file()
    
    # Check directories
    print("\n📁 Checking directories...")
    check_data_directory()
    
    # Final summary
    print("\n" + "=" * 60)
    print("📊 DEPENDENCY CHECK SUMMARY")
    print("=" * 60)
    
    if missing_packages:
        print("❌ Some packages were missing and have been installed")
    else:
        print("✅ All packages are available")
    
    if not env_ok:
        print("⚠️  Please configure your .env file with Reddit API credentials")
        print("   Get credentials from: https://www.reddit.com/prefs/apps")
    else:
        print("✅ Environment configuration looks good")
    
    print("\n🎉 Dependency check complete!")
    print("🚀 You can now run: python launch.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
