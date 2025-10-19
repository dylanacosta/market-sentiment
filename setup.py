#!/usr/bin/env python3
"""
Market Sentiment Dashboard - Setup Script
Run this first to set up everything needed for the dashboard
"""

import os
import sys
import subprocess
from pathlib import Path

def create_virtual_env():
    """Create virtual environment if it doesn't exist."""
    print("🔧 Setting up virtual environment...")
    
    if os.path.exists("bin") or os.path.exists("Scripts"):
        print("✅ Virtual environment already exists")
        return True
    
    try:
        subprocess.run([sys.executable, "-m", "venv", "."], check=True)
        print("✅ Virtual environment created")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False

def activate_and_install():
    """Activate virtual environment and install dependencies."""
    print("📦 Installing dependencies...")
    
    # Determine activation script based on OS
    if os.name == 'nt':  # Windows
        activate_script = "Scripts\\activate.bat"
        pip_cmd = "Scripts\\pip"
    else:  # Unix-like (macOS, Linux)
        activate_script = "bin/activate"
        pip_cmd = "bin/pip"
    
    try:
        # Install dependencies using the comprehensive checker
        result = subprocess.run([sys.executable, "check_dependencies.py"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ All dependencies installed successfully!")
            return True
        else:
            print(f"❌ Dependency installation failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def create_directories():
    """Create necessary directories."""
    print("📁 Creating directories...")
    directories = [
        "share/outputs",
        "data_pipeline/scrapers", 
        "data_pipeline/processors",
        "data_pipeline/storage",
        "main-pipeline"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created {directory}")

def create_env_template():
    """Create .env template if it doesn't exist."""
    if os.path.exists('.env'):
        print("✅ .env file already exists")
        return True
    
    print("📝 Creating .env template...")
    env_content = """# Reddit API Credentials
# Get these from https://www.reddit.com/prefs/apps
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=market-sentiment/0.1 by your_reddit_username
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ .env template created")
    print("🔧 Please edit .env file with your Reddit API credentials")
    return True

def main():
    """Main setup function."""
    print("🚀 Market Sentiment Dashboard - Setup")
    print("=" * 50)
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Step 1: Create virtual environment
    if not create_virtual_env():
        print("❌ Setup failed at virtual environment creation")
        return False
    
    # Step 2: Create directories
    create_directories()
    
    # Step 3: Install dependencies
    if not activate_and_install():
        print("❌ Setup failed at dependency installation")
        return False
    
    # Step 4: Create .env template
    create_env_template()
    
    # Final instructions
    print("\n" + "=" * 50)
    print("🎉 SETUP COMPLETE!")
    print("=" * 50)
    print("📋 Next steps:")
    print("1. Edit .env file with your Reddit API credentials")
    print("2. Run: python launch.py")
    print("3. Or run: ./launch_dashboard.sh (macOS/Linux)")
    print("4. Or run: launch_dashboard.bat (Windows)")
    print("\n🔗 Get Reddit API credentials from: https://www.reddit.com/prefs/apps")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
