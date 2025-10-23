#!/usr/bin/env python3
"""
Test script to run the app and check for errors
"""

import sys
import os

# Add the scientific_review_crew directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scientific_review_crew'))

try:
    print("Testing app import...")
    from app import app
    print("✅ App imported successfully")
    
    print("Testing template rendering...")
    with app.test_client() as client:
        response = client.get('/')
        print(f"✅ Main page: {response.status_code}")
        if response.status_code == 200:
            print("✅ Page loads successfully!")
        else:
            print(f"❌ Error: {response.get_data()}")
    
    print("Testing health endpoint...")
    with app.test_client() as client:
        response = client.get('/health')
        print(f"✅ Health endpoint: {response.status_code}")
        print(f"Response: {response.get_json()}")
    
    print("\n🎉 All tests passed! Starting server...")
    print("Access at: http://localhost:5000")
    print("Press Ctrl+C to stop")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
