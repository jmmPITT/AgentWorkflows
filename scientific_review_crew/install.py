#!/usr/bin/env python3
"""
Installation script for Elite Scientific Review Crew
"""

import os
import sys
import subprocess
import platform

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    # Upgrade pip first
    if not run_command(f"{sys.executable} -m pip install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install requirements
    if not run_command(f"{sys.executable} -m pip install -r requirements.txt", "Installing requirements"):
        return False
    
    return True

def setup_environment():
    """Set up environment configuration"""
    print("⚙️ Setting up environment...")
    
    env_example = "env.example"
    env_file = ".env"
    
    if not os.path.exists(env_file):
        if os.path.exists(env_example):
            print(f"📋 Creating {env_file} from {env_example}")
            with open(env_example, 'r') as f:
                content = f.read()
            with open(env_file, 'w') as f:
                f.write(content)
            print(f"✅ {env_file} created. Please edit it with your credentials.")
        else:
            print(f"⚠️ {env_example} not found. Please create {env_file} manually.")
    else:
        print(f"✅ {env_file} already exists")
    
    return True

def check_gcloud_auth():
    """Check Google Cloud authentication"""
    print("🔐 Checking Google Cloud authentication...")
    
    try:
        result = subprocess.run("gcloud auth list", shell=True, capture_output=True, text=True)
        if "No credentialed accounts" in result.stdout:
            print("⚠️ No Google Cloud accounts authenticated")
            print("Run: gcloud auth application-default login")
            return False
        else:
            print("✅ Google Cloud authentication found")
            return True
    except FileNotFoundError:
        print("⚠️ gcloud CLI not found. Please install Google Cloud SDK")
        return False

def main():
    """Main installation process"""
    print("🚀 Elite Scientific Review Crew - Installation Script")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Installation failed at dependency installation")
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        print("❌ Installation failed at environment setup")
        sys.exit(1)
    
    # Check Google Cloud auth
    check_gcloud_auth()
    
    print("\n" + "=" * 60)
    print("🎉 Installation completed!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your credentials")
    print("2. Run: gcloud auth application-default login")
    print("3. Place your PDF file as 'research_paper.pdf'")
    print("4. Run: python run_review.py")
    print("\n📚 For more information, see README.md")

if __name__ == "__main__":
    main()
