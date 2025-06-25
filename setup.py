"""
Setup script for the AI Calendar Booking Agent.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def create_env_file():
    """Create .env file from template if it doesn't exist."""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        print("📝 Creating .env file from template...")
        with open(env_example, 'r') as src, open(env_file, 'w') as dst:
            dst.write(src.read())
        print("✅ .env file created. Please edit it with your actual API keys.")
    elif env_file.exists():
        print("✅ .env file already exists")
    else:
        print("⚠️  No .env.example file found")

def install_dependencies():
    """Install Python dependencies."""
    print("📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True, text=True)
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print(f"Error output: {e.stderr}")
        sys.exit(1)

def check_credentials():
    """Check if Google Calendar credentials file exists."""
    credentials_file = Path("credentials.json")
    if not credentials_file.exists():
        print("⚠️  Google Calendar credentials.json not found")
        print("📋 To set up Google Calendar integration:")
        print("   1. Go to Google Cloud Console")
        print("   2. Enable Google Calendar API")
        print("   3. Create OAuth 2.0 credentials")
        print("   4. Download credentials.json to project root")
    else:
        print("✅ Google Calendar credentials found")

def main():
    """Main setup function."""
    print("🚀 Setting up AI Calendar Booking Agent...")
    print("=" * 50)
    
    check_python_version()
    create_env_file()
    install_dependencies()
    check_credentials()
    
    print("\n" + "=" * 50)
    print("✅ Setup completed!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your OpenAI API key")
    print("2. Add Google Calendar credentials.json (if not done)")
    print("3. Run the backend: python run_backend.py")
    print("4. Run the frontend: python run_frontend.py")
    print("\n🌐 The app will be available at:")
    print("   - Backend API: http://localhost:8000")
    print("   - Frontend UI: http://localhost:8501")

if __name__ == "__main__":
    main()
