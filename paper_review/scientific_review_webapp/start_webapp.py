#!/usr/bin/env python3
"""
Elite Scientific Review Crew - Web Application Starter
Complete Flask backend with scientific review integration
"""

import os
import sys
import subprocess
import time

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import flask
        print("✅ Flask is installed")
    except ImportError:
        print("❌ Flask not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "flask", "werkzeug"])
        print("✅ Flask installed successfully")
    
    # Check if parent review system is available
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if not os.path.exists(os.path.join(parent_dir, "run_review.py")):
        print("❌ Parent review system not found!")
        print("Please ensure the scientific_review_crew directory is in the parent folder")
        return False
    
    print("✅ Parent review system found")
    return True

def main():
    """Main launcher function"""
    print("🚀 Elite Scientific Review Crew - Complete Web Application")
    print("=" * 70)
    print("🌐 Starting retro terminal interface with full backend...")
    print("🎯 Mission: Restore scientific integrity to academic publishing")
    print("=" * 70)
    
    if not check_dependencies():
        print("❌ Dependency check failed. Please fix the issues above.")
        return
    
    print("\n🔧 Starting Flask web server...")
    print("📍 Access at: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 70)
    
    # Import and run the Flask app
    from flask_app import app
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()

