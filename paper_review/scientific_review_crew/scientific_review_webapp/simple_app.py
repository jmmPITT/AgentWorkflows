from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Elite Scientific Review Crew</title>
    <style>
        body { background: #000; color: #00ff00; font-family: monospace; padding: 20px; }
        .header { text-align: center; border: 2px solid #00ff00; padding: 20px; margin-bottom: 20px; }
        .title { font-size: 2em; text-shadow: 0 0 10px #00ff00; }
        .upload { border: 2px dashed #00ff00; padding: 40px; text-align: center; margin: 20px 0; }
        .btn { background: #000; color: #00ff00; border: 1px solid #00ff00; padding: 10px 20px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="header">
        <div class="title">ELITE SCIENTIFIC REVIEW CREW</div>
        <div>Terminal Interface v1.0</div>
        <div style="font-style: italic; color: #00cc00;">"Journals are big business, not science. We are returning to science!"</div>
    </div>
    
    <div class="upload">
        <h3> UPLOAD SCIENTIFIC PAPER</h3>
        <p>Click to upload or drag & drop PDF file</p>
        <p style="color: #00cc00;">Maximum file size: 50MB</p>
        <input type="file" id="fileInput" accept=".pdf" style="display: none;">
        <button class="btn" onclick="document.getElementById('fileInput').click()">SELECT FILE</button>
    </div>
    
    <div style="text-align: center; margin-top: 20px;">
        <p style="color: #00cc00;"> Web Application Ready!</p>
        <p>Upload a PDF to begin the elite scientific review process.</p>
    </div>
    
    <script>
        document.getElementById('fileInput').addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                alert('File selected: ' + file.name + '\\n\\nNote: Full review functionality requires backend integration.');
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    print(" Elite Scientific Review Crew - Web Application")
    print("=" * 60)
    print(" Starting retro terminal interface...")
    print(" Access at: http://localhost:5000")
    print(" Mission: Restore scientific integrity to academic publishing")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
