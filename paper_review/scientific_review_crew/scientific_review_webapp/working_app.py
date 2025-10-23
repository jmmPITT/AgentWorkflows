#!/usr/bin/env python3
"""
Working version of the Elite Scientific Review Crew Web App
"""

import os
import sys
import json
import time
import threading
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from werkzeug.utils import secure_filename
import uuid

# Add the scientific_review_crew directory to path to import the review system
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scientific_review_crew'))

# Import the review system
try:
    from run_review import run_scientific_review
    REVIEW_SYSTEM_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import review system: {e}")
    REVIEW_SYSTEM_AVAILABLE = False

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'elite-scientific-review-2025'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['REPORTS_FOLDER'] = 'reports'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Ensure upload and reports directories exist
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
        
    def to_dict(self):
        # Convert result to string if it's a CrewOutput object
        result_str = str(self.result) if self.result else None
        
        return {
            'session_id': self.session_id,
            'status': self.status,
            'progress': self.progress,
            'current_step': self.current_step,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'result': result_str,
            'reports': self.reports,
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
        
        if REVIEW_SYSTEM_AVAILABLE:
            # Update the main review function to work with our session
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
                for filename in os.listdir(reports_dir):
                    if filename.endswith('.md'):
                        report_name = filename.replace('.md', '')
                        with open(os.path.join(reports_dir, filename), 'r', encoding='utf-8') as f:
                            session.reports[report_name] = f.read()
            
            session.result = result
        else:
            # Mock review for testing
            session.progress = 50
            session.current_step = "Running mock review..."
            time.sleep(2)
            
            session.result = "REJECT"
            session.reports = {
                'editorial_decision': '''# Editorial Decision Report

**Editor:** Elite Scientific Gatekeeper & Chief Editor
**Date:** 2025-10-22 19:45:00

---

## Comprehensive Justification

This manuscript, while addressing a critically important and timely issue concerning the safety and reliability of Large Language Models (LLMs) in the medical domain, fundamentally fails to meet the uncompromising standards of scientific integrity required for publication in this journal.

The paper's central hypothesis revolves around "sycophantic behavior" in LLMs, defined as the models prioritizing "helpfulness" by complying with illogical requests *even when possessing the factual knowledge to identify them as incorrect*. This definition explicitly hinges on the LLM having "near-perfect factual recall ability to match these drugs' generic and brand names."

However, the very title of the cited work, "Language models are surprisingly fragile to drug names in biomedical benchmarks," and its abstract stating, "We find that LLMs are surprisingly fragile to drug names, with performance dropping significantly when drug names are introduced into prompts," directly and unequivocally contradicts this foundational assumption.

This is not a minor oversight; it is a critical flaw that invalidates the very definition of "sycophancy" as presented in this study. If LLMs are indeed "fragile" to drug names, as the authors' own cited work demonstrates, then their failure to identify an illogical request regarding drug equivalences cannot be definitively attributed to a deliberate "sycophantic" choice to ignore known facts.

Therefore, despite the paper's engagement with an important problem and its strengths in certain methodological aspects, the critical contradiction in its foundational premise necessitates a definitive rejection.'''
            }
        
        session.status = "completed"
        session.progress = 100
        session.current_step = "Review completed successfully!"
        session.end_time = datetime.now()
        
    except Exception as e:
        session.status = "error"
        session.error = str(e)
        session.current_step = f"Error: {str(e)}"
        session.end_time = datetime.now()

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
    
    # Separate specialist reports from other reports
    specialist_reports = []
    other_reports = []
    
    for report_name in current_session.reports.keys():
        if report_name.startswith('specialist_'):
            specialist_reports.append(report_name)
        else:
            other_reports.append(report_name)
    
    # Convert result to string if it's a CrewOutput object
    result_str = str(current_session.result) if current_session.result else None
    
    return jsonify({
        'specialist_reports': specialist_reports,
        'other_reports': other_reports,
        'all_reports': list(current_session.reports.keys()),
        'result': result_str
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

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Elite Scientific Review Crew',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 Elite Scientific Review Crew - Web Application")
    print("=" * 60)
    print("🌐 Starting retro terminal interface...")
    print("📍 Access at: http://localhost:5000")
    print("🎯 Mission: Restore scientific integrity to academic publishing")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
