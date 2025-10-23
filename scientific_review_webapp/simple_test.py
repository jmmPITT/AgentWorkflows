#!/usr/bin/env python3
"""
Simple test to check if the app works
"""

from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test</title>
        <style>
            body { background: #000; color: #00ff00; font-family: monospace; }
        </style>
    </head>
    <body>
        <h1>Elite Scientific Review Crew - Test</h1>
        <p>If you can see this, the app is working!</p>
        <div id="editorialReport" style="display: none; border: 1px solid #00ff00; padding: 20px; margin: 20px 0;">
            <div id="editorialContent">This is a test editorial report</div>
        </div>
        <button onclick="document.getElementById('editorialReport').style.display='block'">Show Editorial Report</button>
    </body>
    </html>
    '''

if __name__ == '__main__':
    print("Starting simple test app...")
    print("Access at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
