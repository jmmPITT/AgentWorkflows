#!/usr/bin/env python3
"""
Elite Scientific Review Crew - Web Application Launcher
Retro Terminal Interface for Scientific Paper Review
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if required packages are installed"""
    try:
        import flask
        import crewai
        print("✅ Core dependencies found")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists in the scientific_review_crew directory"""
    env_path = Path(__file__).parent.parent / "scientific_review_crew" / ".env"
    if env_path.exists():
        print("✅ Environment configuration found")
        return True
    else:
        print("❌ Missing .env file")
        print("Please create a .env file in the scientific_review_crew directory with:")
        print("GCP_PROJECT_ID=your-gcp-project-id")
        print("GCP_REGION=us-central1")
        print("SERPER_API_KEY=your-serper-api-key")
        return False

def main():
    """Main launcher function"""
    print("🚀 Elite Scientific Review Crew - Web Application Launcher")
    print("=" * 60)
    
    # Check requirements
    if not check_requirements():
        return
    
    # Check environment file
    if not check_env_file():
        return
    
    print("🌐 Starting retro terminal interface...")
    print("📍 Access at: http://localhost:5000")
    print("🎯 Mission: Restore scientific integrity to academic publishing")
    print("=" * 60)
    print("Press Ctrl+C to stop the server")
    print()
    
    # Start the Flask app
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    main()
