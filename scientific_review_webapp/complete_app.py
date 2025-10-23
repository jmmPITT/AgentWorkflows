from flask import Flask, render_template, request, jsonify, send_file
import os
import sys
import threading
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Try to import the review system
try:
    from run_review import run_scientific_review
    REVIEW_AVAILABLE = True
except ImportError:
    REVIEW_AVAILABLE = False

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['REPORTS_FOLDER'] = 'reports'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

os.makedirs('uploads', exist_ok=True)
os.makedirs('reports', exist_ok=True)

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
        self.agent_outputs = []  # Store real-time agent outputs
    
    def add_agent_output(self, agent_name, output):
        """Add agent output to the session"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.agent_outputs.append({
            'timestamp': timestamp,
            'agent': agent_name,
            'output': output
        })
        # Keep only last 100 outputs to prevent memory issues
        if len(self.agent_outputs) > 100:
            self.agent_outputs = self.agent_outputs[-100:]

def run_review_background(session):
    global current_session
    try:
        # Set UTF-8 encoding to handle emoji characters
        import os
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        
        session.status = "processing"
        session.current_step = "Initializing Elite Review Crew..."
        session.progress = 10
        session.add_agent_output("SYSTEM", "Starting scientific review process...")
        
        if not REVIEW_AVAILABLE:
            session.add_agent_output("ERROR", "Scientific review system not available")
            raise Exception("Scientific review system not available")
        
        # Clear existing reports directory in webapp
        session.add_agent_output("SYSTEM", "Clearing existing reports...")
        webapp_reports_path = 'reports'
        if os.path.exists(webapp_reports_path):
            import shutil
            shutil.rmtree(webapp_reports_path)
            os.makedirs(webapp_reports_path, exist_ok=True)
            session.add_agent_output("SYSTEM", "Webapp reports directory cleared")
        
        # Check for environment variables
        gcp_project_id = os.getenv("GCP_PROJECT_ID")
        gcp_region = os.getenv("GCP_REGION")
        serper_api_key = os.getenv("SERPER_API_KEY")
        
        if not all([gcp_project_id, gcp_region, serper_api_key]):
            session.add_agent_output("ERROR", "Missing API credentials!")
            session.add_agent_output("ERROR", f"GCP_PROJECT_ID: {gcp_project_id}")
            session.add_agent_output("ERROR", f"GCP_REGION: {gcp_region}")
            session.add_agent_output("ERROR", f"SERPER_API_KEY: {serper_api_key}")
            raise Exception("Missing required API credentials - cannot run multi-agent crew")
        else:
            session.add_agent_output("SYSTEM", "API credentials found - running full multi-agent analysis...")
            session.add_agent_output("SYSTEM", "This may take several minutes...")
            
            # Run the actual review with progress tracking
            try:
                session.add_agent_output("SYSTEM", "Starting PDF processing...")
                from tools.pdf_tools import PDFTool
                pdf_tool = PDFTool()
                pdf_result = pdf_tool._run(session.pdf_path)
                session.add_agent_output("PDF_TOOL", f"Processed {pdf_result['summary']['total_pages']} pages")
                session.add_agent_output("PDF_TOOL", f"Extracted {pdf_result['summary']['total_text_length']:,} characters")
                
                session.add_agent_output("SYSTEM", "Preparing paper content...")
                paper_text = ""
                figure_paths = []
                for page in pdf_result['pages']:
                    paper_text += f"\n\n--- PAGE {page['page_number']} ---\n"
                    paper_text += page['text']
                    if page['image_path']:
                        figure_paths.append(page['image_path'])
                figure_paths_str = "\n".join(figure_paths)
                
                session.add_agent_output("SYSTEM", "Initializing Gemini 2.5 Flash...")
                from crewai.llm import LLM
                gemini_llm = LLM(
                    model="vertex_ai/gemini-2.5-flash",
                    api_key="",
                    temperature=0.1
                )
                
                session.add_agent_output("SYSTEM", "Assembling scientific review crew...")
                from src.crew import assemble_crew
                crew = assemble_crew(gemini_llm, paper_text, figure_paths_str)
                session.add_agent_output("SYSTEM", f"Deployed {len(crew.tasks)} specialist agents")
                
                # Execute crew with progress tracking
                session.add_agent_output("SYSTEM", "Starting multi-agent crew execution...")
                session.add_agent_output("SYSTEM", "This will take several minutes...")
                
                # Add individual agent status messages
                for i, task in enumerate(crew.tasks):
                    agent_name = task.agent.role if hasattr(task, 'agent') and task.agent else f"Agent {i+1}"
                    session.add_agent_output("CREW", f"Deployed {agent_name} - Ready for analysis")
                
                session.add_agent_output("SYSTEM", "All agents deployed - starting analysis...")
                session.add_agent_output("SYSTEM", "Processing in progress... (this may take 5-10 minutes)")
                
                # Add some progress updates during execution
                import time
                session.add_agent_output("SYSTEM", "Agents are analyzing the paper...")
                time.sleep(2)  # Brief pause to show progress
                
                # Run the crew
                result = crew.kickoff()
                
                # Add completion messages
                session.add_agent_output("SYSTEM", "Individual agent analysis completed!")
                session.add_agent_output("SYSTEM", "Synthesizing results...")
                time.sleep(1)
                
                session.add_agent_output("SYSTEM", "Multi-agent analysis completed!")
                session.add_agent_output("SYSTEM", "Generating final decision...")
                
                # Convert result to string for JSON serialization
                result_str = str(result) if result else "No result generated"
                session.add_agent_output("SYSTEM", f"Final decision: {result_str}")
                session.result = result_str
                
                # Save reports to the webapp reports directory
                session.add_agent_output("SYSTEM", "Saving reports to webapp directory...")
                from run_review import save_reports_to_files
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                pdf_name = os.path.splitext(os.path.basename(session.pdf_path))[0]
                webapp_reports_dir = f"reports/{pdf_name}_{timestamp}"
                save_reports_to_files(crew, result_str, session.pdf_path, webapp_reports_dir)
                session.add_agent_output("SYSTEM", f"Reports saved to: {webapp_reports_dir}")
                
            except Exception as e:
                session.add_agent_output("ERROR", f"CRITICAL ERROR during crew execution: {str(e)}")
                session.add_agent_output("ERROR", f"Error type: {type(e).__name__}")
                import traceback
                session.add_agent_output("ERROR", f"Traceback: {traceback.format_exc()}")
                raise e  # Re-raise the error so it's not hidden
        
        session.progress = 90
        session.current_step = "Generating final reports..."
        session.add_agent_output("SYSTEM", "Loading generated reports...")
        
        # Load reports from the webapp reports directory
        session.add_agent_output("SYSTEM", "Loading generated reports...")
        if os.path.exists('reports'):
            # Find the most recent reports directory
            reports_dirs = [d for d in os.listdir('reports') if os.path.isdir(os.path.join('reports', d))]
            if reports_dirs:
                # Sort by name (which includes timestamp) to get the most recent
                reports_dirs.sort(reverse=True)
                latest_reports_dir = os.path.join('reports', reports_dirs[0])
                session.add_agent_output("SYSTEM", f"Loading reports from: {latest_reports_dir}")
                
                session.reports = {}
                for filename in os.listdir(latest_reports_dir):
                    if filename.endswith('.md'):
                        report_name = filename.replace('.md', '')
                        try:
                            with open(os.path.join(latest_reports_dir, filename), 'r', encoding='utf-8') as f:
                                session.reports[report_name] = f.read()
                            session.add_agent_output("SYSTEM", f"Loaded report: {report_name}")
                        except Exception as e:
                            session.add_agent_output("ERROR", f"Failed to load {report_name}: {str(e)}")
                session.add_agent_output("SYSTEM", f"Loaded {len(session.reports)} reports from files")
            else:
                session.add_agent_output("ERROR", "No reports directories found in webapp reports folder")
        else:
            session.add_agent_output("ERROR", "Webapp reports directory does not exist")
        
        # If we still don't have reports, this is a failure
        if not session.reports:
            session.add_agent_output("ERROR", "NO REPORTS GENERATED - CREW FAILED!")
            session.add_agent_output("ERROR", "This indicates the multi-agent crew did not produce any output")
            raise Exception("No reports generated by multi-agent crew - complete failure")
        
        session.status = "completed"
        session.progress = 100
        session.current_step = "Review completed successfully!"
        session.add_agent_output("SYSTEM", "All tasks completed - review ready for viewing!")
        session.end_time = datetime.now()
        
    except Exception as e:
        session.status = "error"
        session.error = str(e)
        session.current_step = f"Error: {str(e)}"
        session.add_agent_output("ERROR", f"Review failed: {str(e)}")
        session.end_time = datetime.now()

@app.route('/')
def index():
    return render_template('terminal.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    global current_session
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and file.filename.lower().endswith('.pdf'):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join('uploads', filename)
        file.save(filepath)
        
        session_id = str(uuid.uuid4())
        current_session = ReviewSession(session_id, filepath)
        
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
    global current_session
    print(f"DEBUG: current_session = {current_session}")
    
    # If no current session, try to find a completed session
    if current_session is None:
        # Look for the most recent completed session
        if os.path.exists('reports'):
            reports_dirs = [d for d in os.listdir('reports') if os.path.isdir(os.path.join('reports', d))]
            if reports_dirs:
                # Sort by name (which includes timestamp) to get the most recent
                reports_dirs.sort(reverse=True)
                latest_reports_dir = os.path.join('reports', reports_dirs[0])
                
                # Create a mock completed session
                session_id = "recovered_session"
                current_session = ReviewSession(session_id, "recovered")
                current_session.status = "completed"
                current_session.progress = 100
                current_session.current_step = "Review completed successfully!"
                current_session.result = "Review completed - check reports"
                
                # Load reports from the latest directory
                current_session.reports = {}
                for filename in os.listdir(latest_reports_dir):
                    if filename.endswith('.md'):
                        report_name = filename.replace('.md', '')
                        try:
                            with open(os.path.join(latest_reports_dir, filename), 'r', encoding='utf-8') as f:
                                current_session.reports[report_name] = f.read()
                        except Exception as e:
                            print(f"Error loading {report_name}: {e}")
                
                print(f"DEBUG: Recovered session with {len(current_session.reports)} reports")
    
    if current_session is None:
        return jsonify({'error': 'No active session'}), 404
        
    return jsonify({
        'session_id': current_session.session_id,
        'status': current_session.status,
        'progress': current_session.progress,
        'current_step': current_session.current_step,
        'start_time': current_session.start_time.isoformat(),
        'end_time': current_session.end_time.isoformat() if current_session.end_time else None,
        'result': current_session.result,
        'reports': current_session.reports,
        'error': current_session.error,
        'agent_outputs': current_session.agent_outputs
    })

@app.route('/reports')
def list_reports():
    global current_session
    if current_session is None or current_session.status != "completed":
        return jsonify({'error': 'No completed review available'}), 404
    
    # Separate specialist reports from other reports
    specialist_reports = []
    other_reports = []
    
    for report_name in current_session.reports.keys():
        if 'specialist_elite_' in report_name and 'scientific_reviewer_report' in report_name:
            specialist_reports.append(report_name)
        else:
            other_reports.append(report_name)
    
    return jsonify({
        'specialist_reports': specialist_reports,
        'other_reports': other_reports,
        'reports': list(current_session.reports.keys()),
        'result': current_session.result
    })

@app.route('/report/<report_name>')
def get_report(report_name):
    global current_session
    if current_session is None or current_session.status != "completed":
        return jsonify({'error': 'No completed review available'}), 404
    if report_name not in current_session.reports:
        return jsonify({'error': 'Report not found'}), 404
    return jsonify({
        'name': report_name,
        'content': current_session.reports[report_name]
    })

@app.route('/reset')
def reset_session():
    global current_session
    current_session = None
    return jsonify({'success': True})

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'review_system_available': REVIEW_AVAILABLE,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print(" Elite Scientific Review Crew - Complete Web Application")
    print("=" * 70)
    print(" Starting retro terminal interface with full backend...")
    print(" Access at: http://localhost:5000")
    print(" Mission: Restore scientific integrity to academic publishing")
    print(f" Review system available: {REVIEW_AVAILABLE}")
    print("=" * 70)
    app.run(debug=True, host='0.0.0.0', port=5000)
