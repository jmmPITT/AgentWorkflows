#!/usr/bin/env python3
"""
Simple Elite Scientific Review Crew - Web Application
"""

from flask import Flask, render_template_string
import os

app = Flask(__name__)

# HTML template as a string
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Elite Scientific Review Crew - Terminal Interface</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: #000;
            color: #00ff00;
            font-family: 'JetBrains Mono', monospace;
            font-size: 14px;
            line-height: 1.4;
            overflow-x: hidden;
        }
        
        .terminal {
            min-height: 100vh;
            padding: 20px;
            background: linear-gradient(45deg, #000 0%, #001100 50%, #000 100%);
            position: relative;
        }
        
        .terminal::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: 
                radial-gradient(circle at 20% 80%, rgba(0, 255, 0, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(0, 255, 0, 0.1) 0%, transparent 50%);
            pointer-events: none;
            z-index: 1;
        }
        
        .content {
            position: relative;
            z-index: 2;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            border: 2px solid #00ff00;
            padding: 20px;
            background: rgba(0, 255, 0, 0.05);
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
        }
        
        .title {
            font-size: 2.5em;
            font-weight: 700;
            text-shadow: 0 0 10px #00ff00;
            margin-bottom: 10px;
            animation: glow 2s ease-in-out infinite alternate;
        }
        
        @keyframes glow {
            from { text-shadow: 0 0 10px #00ff00; }
            to { text-shadow: 0 0 20px #00ff00, 0 0 30px #00ff00; }
        }
        
        .subtitle {
            font-size: 1.2em;
            color: #00cc00;
            margin-bottom: 5px;
        }
        
        .mission {
            font-size: 0.9em;
            color: #009900;
            font-style: italic;
        }
        
        .main-content {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .section {
            margin-bottom: 30px;
            border: 1px solid #00ff00;
            padding: 20px;
            background: rgba(0, 255, 0, 0.02);
        }
        
        .section-title {
            font-size: 1.5em;
            color: #00ff00;
            margin-bottom: 15px;
            text-shadow: 0 0 5px #00ff00;
        }
        
        .upload-area {
            border: 2px dashed #00ff00;
            padding: 40px;
            text-align: center;
            background: rgba(0, 255, 0, 0.05);
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .upload-area:hover {
            background: rgba(0, 255, 0, 0.1);
            border-color: #00cc00;
        }
        
        .upload-icon {
            font-size: 3em;
            margin-bottom: 15px;
            color: #00ff00;
        }
        
        .upload-text {
            font-size: 1.2em;
            margin-bottom: 10px;
        }
        
        .upload-subtext {
            color: #00cc00;
            font-size: 0.9em;
        }
        
        .btn {
            background: #000;
            color: #00ff00;
            border: 1px solid #00ff00;
            padding: 10px 20px;
            cursor: pointer;
            font-family: 'JetBrains Mono', monospace;
            font-size: 14px;
            transition: all 0.3s ease;
            margin-top: 15px;
        }
        
        .btn:hover {
            background: rgba(0, 255, 0, 0.1);
            box-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
        }
        
        .status {
            text-align: center;
            margin-top: 20px;
            padding: 20px;
            border: 1px solid #00ff00;
            background: rgba(0, 255, 0, 0.05);
        }
        
        .status-title {
            font-size: 1.3em;
            color: #00ff00;
            margin-bottom: 10px;
        }
        
        .status-text {
            color: #00cc00;
            font-style: italic;
        }
        
        .typing {
            overflow: hidden;
            border-right: 2px solid #00ff00;
            white-space: nowrap;
            animation: typing 2s steps(40, end), blink-caret 0.75s step-end infinite;
        }
        
        @keyframes typing {
            from { width: 0 }
            to { width: 100% }
        }
        
        @keyframes blink-caret {
            from, to { border-color: transparent }
            50% { border-color: #00ff00 }
        }
    </style>
</head>
<body>
    <div class="terminal">
        <div class="content">
            <div class="header">
                <div class="title">ELITE SCIENTIFIC REVIEW CREW</div>
                <div class="subtitle">Terminal Interface v1.0</div>
                <div class="mission">"Journals are big business, not science. We are returning to science!"</div>
            </div>
            
            <div class="main-content">
                <!-- Upload Section -->
                <div class="section">
                    <div class="section-title">📄 UPLOAD SCIENTIFIC PAPER</div>
                    <div class="upload-area" onclick="document.getElementById('fileInput').click()">
                        <div class="upload-icon">📁</div>
                        <div class="upload-text">Click to upload or drag & drop PDF file</div>
                        <div class="upload-subtext">Maximum file size: 50MB</div>
                        <input type="file" id="fileInput" accept=".pdf" style="display: none;">
                    </div>
                </div>
                
                <!-- Status Section -->
                <div class="section status">
                    <div class="status-title">🚀 SYSTEM STATUS</div>
                    <div class="status-text">
                        <div class="typing">Web Application Ready for Scientific Review</div>
                        <br><br>
                        ✅ Flask server running<br>
                        ✅ Retro terminal interface loaded<br>
                        ✅ Ready to process scientific papers<br>
                        <br>
                        <strong>Next Steps:</strong><br>
                        1. Upload a PDF scientific paper<br>
                        2. Watch the elite review process<br>
                        3. View detailed specialist reports<br>
                        4. See the final editorial decision
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // File upload handling
        document.getElementById('fileInput').addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                alert('File selected: ' + file.name + '\\n\\nNote: Full review functionality requires backend integration with the scientific review system.');
            }
        });
        
        // Add some terminal-style effects
        console.log('🚀 Elite Scientific Review Crew - Terminal Interface Loaded');
        console.log('🎯 Mission: Restore scientific integrity to academic publishing');
        
        // Simulate terminal boot sequence
        setTimeout(() => {
            console.log('✅ System initialized');
            console.log('✅ AI agents ready');
            console.log('✅ Review protocols loaded');
        }, 1000);
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    """Main terminal interface"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/health')
def health():
    """Health check endpoint"""
    return {'status': 'healthy', 'message': 'Elite Scientific Review Crew is running'}

if __name__ == '__main__':
    print("🚀 Elite Scientific Review Crew - Web Application")
    print("=" * 60)
    print("🌐 Starting retro terminal interface...")
    print("📍 Access at: http://localhost:5000")
    print("🎯 Mission: Restore scientific integrity to academic publishing")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
