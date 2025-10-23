#!/usr/bin/env python3
"""
Elite Scientific Review Crew - Complete Flask Web Application
Full backend integration with scientific review system
"""

import os
import sys
import json
import time
import threading
import uuid
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from werkzeug.utils import secure_filename
import traceback

# Add the parent directory to path to import the review system
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import the scientific review system
try:
    from run_review import run_scientific_review
    REVIEW_SYSTEM_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import scientific review system: {e}")
    REVIEW_SYSTEM_AVAILABLE = False

app = Flask(__name__)
app.config['SECRET_KEY'] = 'elite-scientific-review-2025'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['REPORTS_FOLDER'] = 'reports'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['REPORTS_FOLDER'], exist_ok=True)

# Global variable to store current review session
current_session = None

class ReviewSession:
    def __init__(self, session_id, pdf_path):
        self.session_id = session_id
        self.pdf_path = pdf_path
        self.status = "uploaded"
        self.progress = 0
        self.current_step = ""
        self.start_time = datetime.now()
        self.end_time = None
        self.result = None
        self.reports = {}
        self.error = None
        self.specialist_reports = {}
        self.synthesis_report = None
        self.editorial_decision = None
        
    def to_dict(self):
        return {
            'session_id': self.session_id,
            'status': self.status,
            'progress': self.progress,
            'current_step': self.current_step,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'result': self.result,
            'reports': self.reports,
            'specialist_reports': self.specialist_reports,
            'synthesis_report': self.synthesis_report,
            'editorial_decision': self.editorial_decision,
            'error': self.error
        }

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf'}

def run_review_background(session):
    """Run the scientific review in background thread"""
    global current_session
    
    try:
        session.status = "processing"
        session.current_step = "Initializing Elite Review Crew..."
        session.progress = 10
        
        if not REVIEW_SYSTEM_AVAILABLE:
            raise Exception("Scientific review system not available. Please ensure run_review.py is accessible.")
        
        # Run the scientific review
        result = run_scientific_review(session.pdf_path)
        
        session.progress = 90
        session.current_step = "Generating final reports..."
        
        # Find the latest reports directory
        reports_dir = None
        for item in os.listdir(app.config['REPORTS_FOLDER']):
            if item.startswith('research_paper_') and os.path.isdir(os.path.join(app.config['REPORTS_FOLDER'], item)):
                reports_dir = os.path.join(app.config['REPORTS_FOLDER'], item)
        
        if reports_dir:
            # Load all reports
            session.reports = {}
            session.specialist_reports = {}
            
            for filename in os.listdir(reports_dir):
                if filename.endswith('.md'):
                    report_name = filename.replace('.md', '')
                    file_path = os.path.join(reports_dir, filename)
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        session.reports[report_name] = content
                        
                        # Categorize reports
                        if 'specialist_' in report_name:
                            session.specialist_reports[report_name] = content
                        elif 'synthesis' in report_name:
                            session.synthesis_report = content
                        elif 'editorial' in report_name:
                            session.editorial_decision = content
        
        session.result = result
        session.status = "completed"
        session.progress = 100
        session.current_step = "Review completed successfully!"
        session.end_time = datetime.now()
        
    except Exception as e:
        session.status = "error"
        session.error = str(e)
        session.current_step = f"Error: {str(e)}"
        session.end_time = datetime.now()
        print(f"Error in review process: {e}")
        traceback.print_exc()

@app.route('/')
def index():
    """Main terminal interface"""
    return render_template('terminal.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle PDF file upload"""
    global current_session
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add timestamp to make filename unique
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Create new review session
        session_id = str(uuid.uuid4())
        current_session = ReviewSession(session_id, filepath)
        
        # Start review in background thread
        thread = threading.Thread(target=run_review_background, args=(current_session,))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'filename': filename
        })
    
    return jsonify({'error': 'Invalid file type. Please upload a PDF file.'}), 400

@app.route('/status')
def get_status():
    """Get current review status"""
    global current_session
    
    if current_session is None:
        return jsonify({'error': 'No active session'}), 404
    
    return jsonify(current_session.to_dict())

@app.route('/reports')
def list_reports():
    """List available reports"""
    global current_session
    
    if current_session is None or current_session.status != "completed":
        return jsonify({'error': 'No completed review available'}), 404
    
    return jsonify({
        'specialist_reports': list(current_session.specialist_reports.keys()),
        'synthesis_report': 'synthesis_report' if current_session.synthesis_report else None,
        'editorial_decision': 'editorial_decision' if current_session.editorial_decision else None,
        'result': current_session.result
    })

@app.route('/report/<report_name>')
def get_report(report_name):
    """Get specific report content"""
    global current_session
    
    if current_session is None or current_session.status != "completed":
        return jsonify({'error': 'No completed review available'}), 404
    
    if report_name not in current_session.reports:
        return jsonify({'error': 'Report not found'}), 404
    
    return jsonify({
        'name': report_name,
        'content': current_session.reports[report_name]
    })

@app.route('/download/<report_name>')
def download_report(report_name):
    """Download report as markdown file"""
    global current_session
    
    if current_session is None or current_session.status != "completed":
        return jsonify({'error': 'No completed review available'}), 404
    
    if report_name not in current_session.reports:
        return jsonify({'error': 'Report not found'}), 404
    
    # Create temporary file
    temp_filename = f"{report_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
    
    with open(temp_path, 'w', encoding='utf-8') as f:
        f.write(current_session.reports[report_name])
    
    return send_file(temp_path, as_attachment=True, download_name=temp_filename)

@app.route('/reset')
def reset_session():
    """Reset current session"""
    global current_session
    current_session = None
    return jsonify({'success': True})

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'review_system_available': REVIEW_SYSTEM_AVAILABLE,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 Elite Scientific Review Crew - Complete Web Application")
    print("=" * 70)
    print("🌐 Starting retro terminal interface with full backend...")
    print("📍 Access at: http://localhost:5000")
    print("🎯 Mission: Restore scientific integrity to academic publishing")
    print(f"🔧 Review system available: {REVIEW_SYSTEM_AVAILABLE}")
    print("=" * 70)
    
    app.run(debug=True, host='0.0.0.0', port=5000)

