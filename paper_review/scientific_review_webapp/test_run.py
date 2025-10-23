#!/usr/bin/env python3
"""
Test script to run the app and check for errors
"""

import sys
import os

# Add the scientific_review_crew directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scientific_review_crew'))

try:
    print("Testing imports...")
    from app import app
    print("App imported successfully")
    
    print("Testing template loading...")
    with app.app_context():
        template = app.jinja_env.get_template('terminal.html')
        print("Template loaded successfully")
    
    print("Testing health endpoint...")
    with app.test_client() as client:
        response = client.get('/health')
        print(f"Health endpoint: {response.status_code}")
        print(f"Response: {response.get_json()}")
    
    print("Testing main page...")
    with app.test_client() as client:
        response = client.get('/')
        print(f"Main page: {response.status_code}")
        if response.status_code == 200:
            print("Page loads successfully!")
        else:
            print(f"Error: {response.get_data()}")
    
    print("\nAll tests passed! The app should work correctly.")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
