#!/usr/bin/env python3
"""
Test script for the Elite Scientific Review Crew Web Application
"""

import requests
import time
import os

def test_webapp():
    """Test the web application"""
    print("🧪 Testing Elite Scientific Review Crew Web Application")
    print("=" * 60)
    
    # Wait a moment for the server to start
    print("⏳ Waiting for server to start...")
    time.sleep(3)
    
    try:
        # Test main page
        print("📄 Testing main page...")
        response = requests.get("http://localhost:5000", timeout=10)
        if response.status_code == 200:
            print("✅ Main page loaded successfully")
            print(f"📊 Response size: {len(response.text)} characters")
        else:
            print(f"❌ Main page failed with status: {response.status_code}")
            return False
            
        # Test status endpoint
        print("📊 Testing status endpoint...")
        response = requests.get("http://localhost:5000/status", timeout=10)
        if response.status_code == 404:
            print("✅ Status endpoint working (no active session)")
        else:
            print(f"⚠️ Status endpoint returned: {response.status_code}")
            
        print("\n🎉 Web application is running successfully!")
        print("📍 Access at: http://localhost:5000")
        print("🎯 Ready for scientific paper reviews!")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to web application")
        print("💡 Make sure the server is running on port 5000")
        return False
    except Exception as e:
        print(f"❌ Error testing web application: {e}")
        return False

if __name__ == "__main__":
    test_webapp()
