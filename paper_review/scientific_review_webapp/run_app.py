#!/usr/bin/env python3
"""
Simple launcher for the Elite Scientific Review Crew Web App
"""

import sys
import os

# Add the scientific_review_crew directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scientific_review_crew'))

if __name__ == '__main__':
    print("=" * 60)
    print("ELITE SCIENTIFIC REVIEW CREW - WEB APPLICATION")
    print("=" * 60)
    print("Retro Terminal Interface v1.0")
    print("Mission: Restore scientific integrity to academic publishing")
    print("=" * 60)
    print()
    print("Starting server...")
    print("Access at: http://localhost:5000")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")
        import traceback
        traceback.print_exc()
