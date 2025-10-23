#!/usr/bin/env python3
"""
Elite Scientific Review Crew - Web Application
Retro Terminal Interface for Scientific Paper Review
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

# Add the parent directory to path to import the review system
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from run_review import run_scientific_review

app = Flask(__name__)
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
        self.agent_outputs = []  # Store real-time agent outputs
        
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
            'error': self.error,
            'agent_outputs': self.agent_outputs
        }
    
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

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf'}

def create_mock_reports():
    """Create mock reports for testing when real reports aren't available"""
    return {
        'specialist_elite_medical_scientific_reviewer_report': '''# Medical Specialist Report

**Reviewer:** Elite Medical Scientific Reviewer
**Date:** 2025-10-22 19:45:00

---

## Summary

This manuscript presents a critical analysis of Large Language Model (LLM) behavior in medical contexts, specifically examining "sycophantic" responses to illogical drug equivalence requests. From a medical perspective, this work addresses a fundamental safety concern in AI-assisted healthcare applications.

## Scientific Strengths

- **Clinical Relevance:** The focus on drug name recognition and medical misinformation is highly relevant to patient safety
- **Methodological Approach:** The use of controlled prompts with known drug equivalences provides a solid experimental framework
- **Safety Implications:** The work correctly identifies potential risks of AI systems providing incorrect medical information

## Critical Weaknesses & Scientific Concerns

- **Limited Medical Scope:** The study focuses only on simple 1:1 drug equivalences, missing complex medical scenarios
- **Lack of Clinical Validation:** No validation with actual medical professionals or clinical outcomes
- **Oversimplified Medical Context:** Real medical decision-making involves complex patient factors not captured in this study

## Figure Analysis

- **Figure 1:** Shows response distributions but lacks medical context for interpretation
- **Scientific Evaluation:** The statistical analysis is sound but doesn't account for medical decision-making complexity

## Verified Claims & Reproducibility Assessment

- **Claim:** "Near-perfect factual recall ability" for drug names
- **Verification:** Contradicted by cited literature showing LLM fragility with drug names
- **Assessment:** This fundamental assumption undermines the entire medical interpretation

**Medical Recommendation:** REJECT - The study's medical claims are not supported by the evidence presented.''',

        'specialist_elite_engineering_scientific_reviewer_report': '''# Engineering Specialist Report

**Reviewer:** Elite Engineering Scientific Reviewer
**Date:** 2025-10-22 19:45:00

---

## Summary

This work attempts to address a critical engineering challenge in AI system safety through the lens of "sycophantic" behavior. The engineering approach to mitigating harmful AI responses is commendable, but the implementation and evaluation methodology have significant flaws.

## Scientific Strengths

- **Systematic Approach:** The fine-tuning methodology follows established engineering practices
- **Reproducibility:** Code and data availability supports replication
- **Safety Focus:** Addressing AI safety is a critical engineering challenge

## Critical Weaknesses & Scientific Concerns

- **Evaluation Bias:** Single LLM evaluator introduces systematic bias
- **Limited Scope:** Only 1:1 drug equivalences tested, not representative of real-world complexity
- **Insufficient Testing:** Limited out-of-distribution testing doesn't validate generalizability

## Figure Analysis

- **Figure 2:** Workflow diagram is clear but oversimplifies the engineering challenges
- **Figure 4:** Benchmark results show no degradation but limited scope

## Verified Claims & Reproducibility Assessment

- **Claim:** "98% inter-annotator agreement"
- **Verification:** Based on limited sample size (50 outputs)
- **Assessment:** Insufficient for engineering validation

**Engineering Recommendation:** REJECT - Insufficient engineering rigor for safety-critical applications.''',

        'specialist_elite_physics_scientific_reviewer_report': '''# Physics Specialist Report

**Reviewer:** Elite Physics Scientific Reviewer
**Date:** 2025-10-22 19:45:00

---

## Summary

This manuscript applies statistical physics concepts to analyze LLM behavior, treating "sycophancy" as a measurable phenomenon. While the statistical approach is sound, the physical interpretation of the results is questionable.

## Scientific Strengths

- **Statistical Rigor:** Proper use of statistical tests and confidence intervals
- **Quantitative Analysis:** Clear metrics for measuring model behavior
- **Reproducible Methods:** Well-documented experimental procedures

## Critical Weaknesses & Scientific Concerns

- **Misleading Terminology:** "Sycophancy" is not a well-defined physical concept
- **Oversimplified Model:** The binary classification doesn't capture the complexity of language generation
- **Lack of Physical Interpretation:** No clear connection to established physics principles

## Figure Analysis

- **Figure 1:** Statistical distributions are well-presented
- **Figure 4:** Confidence intervals are properly calculated

## Verified Claims & Reproducibility Assessment

- **Claim:** Statistical significance of results
- **Verification:** P-values are reported but effect sizes are missing
- **Assessment:** Statistically sound but physically questionable

**Physics Recommendation:** REJECT - Lacks proper physical foundation and interpretation.''',

        'specialist_elite_chemistry_scientific_reviewer_report': '''# Chemistry Specialist Report

**Reviewer:** Elite Chemistry Scientific Reviewer
**Date:** 2025-10-22 19:45:00

---

## Summary

This work examines LLM behavior in chemical information contexts, specifically drug name recognition and equivalence. The chemical perspective reveals significant limitations in the experimental design and interpretation.

## Scientific Strengths

- **Chemical Accuracy:** Drug names and equivalences are correctly identified
- **Systematic Testing:** Controlled experiments with known chemical relationships
- **Safety Focus:** Chemical misinformation can have serious consequences

## Critical Weaknesses & Scientific Concerns

- **Oversimplified Chemistry:** Real chemical relationships are more complex than 1:1 equivalences
- **Missing Context:** No consideration of chemical interactions, dosages, or patient factors
- **Limited Chemical Scope:** Only generic/brand name pairs tested

## Figure Analysis

- **Figure 1:** Chemical accuracy metrics are presented clearly
- **Scientific Evaluation:** Statistical analysis is appropriate for the chemical data

## Verified Claims & Reproducibility Assessment

- **Claim:** "Near-perfect factual recall" for chemical information
- **Verification:** Contradicted by cited literature on LLM chemical knowledge
- **Assessment:** Chemical claims are not supported by evidence

**Chemistry Recommendation:** REJECT - Insufficient chemical rigor and scope.''',

        'specialist_elite_biology_scientific_reviewer_report': '''# Biology Specialist Report

**Reviewer:** Elite Biology Scientific Reviewer
**Date:** 2025-10-22 19:45:00

---

## Summary

This manuscript addresses a critical issue in AI-assisted biological research: the tendency of LLMs to provide incorrect information when asked to perform illogical tasks. The biological perspective reveals both strengths and significant limitations.

## Scientific Strengths

- **Biological Relevance:** Drug interactions and biological systems are complex and safety-critical
- **Systematic Approach:** Controlled experiments with known biological relationships
- **Safety Implications:** Incorrect biological information can have serious consequences

## Critical Weaknesses & Scientific Concerns

- **Oversimplified Biology:** Biological systems are far more complex than simple drug equivalences
- **Missing Biological Context:** No consideration of biological variability, interactions, or individual differences
- **Limited Scope:** Only human drug systems tested, missing broader biological diversity

## Figure Analysis

- **Figure 1:** Biological accuracy metrics are clearly presented
- **Figure 3:** Out-of-distribution testing shows limited biological scope

## Verified Claims & Reproducibility Assessment

- **Claim:** "Near-perfect factual recall" for biological information
- **Verification:** Contradicted by cited literature on LLM biological knowledge
- **Assessment:** Biological claims are not supported by evidence

**Biology Recommendation:** REJECT - Insufficient biological rigor and scope.''',

        'specialist_elite_computer_science_scientific_reviewer_report': '''# Computer Science Specialist Report

**Reviewer:** Elite Computer Science Scientific Reviewer
**Date:** 2025-10-22 19:45:00

---

## Summary

This work addresses a fundamental challenge in AI safety: preventing harmful responses from large language models. The computer science perspective reveals both technical merit and significant methodological flaws.

## Scientific Strengths

- **Technical Approach:** Fine-tuning methodology follows established ML practices
- **Code Availability:** Full implementation and data are publicly available
- **Safety Focus:** Addressing AI safety is a critical CS challenge

## Critical Weaknesses & Scientific Concerns

- **Evaluation Bias:** Single LLM evaluator introduces systematic bias
- **Limited Generalization:** Only 1:1 drug equivalences tested, not representative of real-world complexity
- **Insufficient Testing:** Limited out-of-distribution testing doesn't validate generalizability

## Figure Analysis

- **Figure 2:** Technical workflow is well-documented
- **Figure 4:** Benchmark results show no degradation but limited scope

## Verified Claims & Reproducibility Assessment

- **Claim:** "98% inter-annotator agreement"
- **Verification:** Based on limited sample size (50 outputs)
- **Assessment:** Insufficient for CS validation

**Computer Science Recommendation:** REJECT - Insufficient technical rigor for safety-critical applications.''',

        'specialist_elite_mathematics_scientific_reviewer_report': '''# Mathematics Specialist Report

**Reviewer:** Elite Mathematics Scientific Reviewer
**Date:** 2025-10-22 19:45:00

---

## Summary

This manuscript applies mathematical analysis to LLM behavior, treating "sycophancy" as a measurable phenomenon. The mathematical approach is sound, but the interpretation and scope are limited.

## Scientific Strengths

- **Statistical Rigor:** Proper use of statistical tests and confidence intervals
- **Quantitative Analysis:** Clear metrics for measuring model behavior
- **Mathematical Framework:** Well-defined mathematical approach

## Critical Weaknesses & Scientific Concerns

- **Oversimplified Model:** The binary classification doesn't capture the complexity of language generation
- **Limited Mathematical Scope:** Only simple statistical tests, missing advanced mathematical analysis
- **Lack of Theoretical Foundation:** No connection to established mathematical principles

## Figure Analysis

- **Figure 1:** Statistical distributions are well-presented
- **Figure 4:** Confidence intervals are properly calculated

## Verified Claims & Reproducibility Assessment

- **Claim:** Statistical significance of results
- **Verification:** P-values are reported but effect sizes are missing
- **Assessment:** Mathematically sound but limited scope

**Mathematics Recommendation:** REJECT - Lacks proper mathematical foundation and scope.''',

        'specialist_elite_artificial_intelligence_scientific_reviewer_report': '''# AI Specialist Report

**Reviewer:** Elite Artificial Intelligence Scientific Reviewer
**Date:** 2025-10-22 19:45:00

---

## Summary

This work addresses a critical challenge in AI safety: preventing harmful responses from large language models. The AI perspective reveals both technical merit and significant methodological flaws.

## Scientific Strengths

- **Technical Approach:** Fine-tuning methodology follows established ML practices
- **Code Availability:** Full implementation and data are publicly available
- **Safety Focus:** Addressing AI safety is a critical AI challenge

## Critical Weaknesses & Scientific Concerns

- **Evaluation Bias:** Single LLM evaluator introduces systematic bias
- **Limited Generalization:** Only 1:1 drug equivalences tested, not representative of real-world complexity
- **Insufficient Testing:** Limited out-of-distribution testing doesn't validate generalizability

## Figure Analysis

- **Figure 2:** Technical workflow is well-documented
- **Figure 4:** Benchmark results show no degradation but limited scope

## Verified Claims & Reproducibility Assessment

- **Claim:** "98% inter-annotator agreement"
- **Verification:** Based on limited sample size (50 outputs)
- **Assessment:** Insufficient for AI validation

**AI Recommendation:** REJECT - Insufficient technical rigor for safety-critical applications.''',

        'specialist_elite_data_science_scientific_reviewer_report': '''# Data Science Specialist Report

**Reviewer:** Elite Data Science Scientific Reviewer
**Date:** 2025-10-22 19:45:00

---

## Summary

This work applies data science methods to analyze LLM behavior, treating "sycophancy" as a measurable phenomenon. The data science approach is sound, but the interpretation and scope are limited.

## Scientific Strengths

- **Statistical Rigor:** Proper use of statistical tests and confidence intervals
- **Quantitative Analysis:** Clear metrics for measuring model behavior
- **Data Availability:** Full dataset and code are publicly available

## Critical Weaknesses & Scientific Concerns

- **Oversimplified Model:** The binary classification doesn't capture the complexity of language generation
- **Limited Data Scope:** Only 1:1 drug equivalences tested, not representative of real-world complexity
- **Insufficient Testing:** Limited out-of-distribution testing doesn't validate generalizability

## Figure Analysis

- **Figure 1:** Statistical distributions are well-presented
- **Figure 4:** Confidence intervals are properly calculated

## Verified Claims & Reproducibility Assessment

- **Claim:** Statistical significance of results
- **Verification:** P-values are reported but effect sizes are missing
- **Assessment:** Data science approach is sound but limited scope

**Data Science Recommendation:** REJECT - Lacks proper data science foundation and scope.''',

        'editorial_decision': '''# Editorial Decision Report

**Editor:** Elite Scientific Gatekeeper & Chief Editor
**Date:** 2025-10-22 19:45:00

---

## Comprehensive Justification

This manuscript, while addressing a critically important and timely issue concerning the safety and reliability of Large Language Models (LLMs) in the medical domain, fundamentally fails to meet the uncompromising standards of scientific integrity required for publication in this journal.

The paper's central hypothesis revolves around "sycophantic behavior" in LLMs, defined as the models prioritizing "helpfulness" by complying with illogical requests *even when possessing the factual knowledge to identify them as incorrect*. This definition explicitly hinges on the LLM having "near-perfect factual recall ability to match these drugs' generic and brand names."

However, the very title of the cited work, "Language models are surprisingly fragile to drug names in biomedical benchmarks," and its abstract stating, "We find that LLMs are surprisingly fragile to drug names, with performance dropping significantly when drug names are introduced into prompts," directly and unequivocally contradicts this foundational assumption.

Therefore, despite the paper's engagement with an important problem and its strengths in certain methodological aspects, the critical contradiction in its foundational premise necessitates a definitive rejection.'''
    }

def run_scientific_review_with_progress(session):
    """Run scientific review with real-time progress reporting"""
    try:
        # Import here to avoid issues
        from run_review import run_scientific_review
        
        # Set up environment variables
        gcp_project_id = os.getenv("GCP_PROJECT_ID")
        gcp_region = os.getenv("GCP_REGION")
        serper_api_key = os.getenv("SERPER_API_KEY")
        
        if not all([gcp_project_id, gcp_region, serper_api_key]):
            session.add_agent_output("SYSTEM", "Missing API credentials - using mock data")
            return "REJECT"  # Mock result
        
        # Set environment variables
        os.environ["GCP_PROJECT_ID"] = gcp_project_id
        os.environ["GCP_REGION"] = gcp_region
        os.environ["SERPER_API_KEY"] = serper_api_key
        os.environ['GOOGLE_CLOUD_PROJECT'] = gcp_project_id
        
        session.add_agent_output("SYSTEM", "Environment configured - starting PDF processing...")
        session.progress = 40
        
        # Process PDF
        from tools.pdf_tools import PDFTool
        pdf_tool = PDFTool()
        result = pdf_tool._run(session.pdf_path)
        
        session.add_agent_output("PDF_TOOL", f"Processed {result['summary']['total_pages']} pages")
        session.add_agent_output("PDF_TOOL", f"Extracted {result['summary']['total_text_length']:,} characters")
        session.progress = 50
        
        # Prepare paper content
        session.add_agent_output("SYSTEM", "Preparing paper content for analysis...")
        paper_text = ""
        figure_paths = []
        
        for page in result['pages']:
            paper_text += f"\n\n--- PAGE {page['page_number']} ---\n"
            paper_text += page['text']
            if page['image_path']:
                figure_paths.append(page['image_path'])
        
        figure_paths_str = "\n".join(figure_paths)
        session.progress = 60
        
        # Set up LLM
        session.add_agent_output("SYSTEM", "Initializing Gemini 2.5 Flash...")
        from crewai.llm import LLM
        gemini_llm = LLM(
            model="vertex_ai/gemini-2.5-flash",
            api_key="",
            temperature=0.1
        )
        
        # Assemble crew
        session.add_agent_output("SYSTEM", "Assembling scientific review crew...")
        from src.crew import assemble_crew
        crew = assemble_crew(gemini_llm, paper_text, figure_paths_str)
        session.progress = 70
        
        # Execute review with progress tracking
        session.add_agent_output("SYSTEM", "Starting multi-agent analysis...")
        session.add_agent_output("SYSTEM", f"Deployed {len(crew.tasks)} specialist agents")
        
        # Run the crew
        result = crew.kickoff()
        
        session.add_agent_output("SYSTEM", "Multi-agent analysis completed!")
        session.add_agent_output("SYSTEM", f"Final decision: {result}")
        session.progress = 80
        
        return result
        
    except Exception as e:
        session.add_agent_output("ERROR", f"Error during review: {str(e)}")
        return None

def run_review_background(session):
    """Run the scientific review in background thread"""
    global current_session
    
    try:
        session.status = "processing"
        session.current_step = "Initializing Elite Review Crew..."
        session.progress = 10
        
        # Check if we have the required environment variables
        gcp_project_id = os.getenv("GCP_PROJECT_ID")
        gcp_region = os.getenv("GCP_REGION")
        serper_api_key = os.getenv("SERPER_API_KEY")
        
        if not all([gcp_project_id, gcp_region, serper_api_key]):
            # Use mock reports if environment variables are not set
            session.current_step = "Using mock reports (missing API credentials)..."
            session.progress = 50
            
            # Simulate processing time
            time.sleep(2)
            
            session.reports = create_mock_reports()
            session.result = "REJECT"  # Mock result
            session.status = "completed"
            session.progress = 100
            session.current_step = "Mock review completed successfully!"
            session.end_time = datetime.now()
            return
        
        # Try to run the actual review
        session.current_step = "Running multi-agent analysis..."
        session.progress = 30
        session.add_agent_output("SYSTEM", "Starting multi-agent scientific review...")
        
        # Create a custom run_scientific_review that reports progress
        result = run_scientific_review_with_progress(session)
        
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
                    try:
                        with open(os.path.join(reports_dir, filename), 'r', encoding='utf-8') as f:
                            session.reports[report_name] = f.read()
                        print(f"[OK] Loaded report: {report_name}")
                    except Exception as e:
                        print(f"[ERR] Error loading report {report_name}: {e}")
        else:
            print("[ERR] No reports directory found")
            # Create mock reports for testing
            session.reports = create_mock_reports()
        
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

@app.route('/')
def index():
    """Main terminal interface"""
    return render_template('terminal.html')

@app.route('/test-specialist-reports')
def test_specialist_reports():
    """Test endpoint to create a mock session with specialist reports"""
    global current_session
    
    # Create a mock session with specialist reports
    current_session = ReviewSession("test-session-123", "test.pdf")
    current_session.status = "completed"
    current_session.progress = 100
    current_session.current_step = "Review completed successfully!"
    current_session.result = "REJECT"
    current_session.reports = create_mock_reports()
    
    return jsonify({
        'success': True,
        'message': 'Test session created with specialist reports',
        'session_id': current_session.session_id
    })

@app.route('/test-upload')
def test_upload():
    """Test endpoint to simulate a file upload and start mock review"""
    global current_session
    
    # Create a mock session
    session_id = str(uuid.uuid4())
    current_session = ReviewSession(session_id, "test.pdf")
    
    # Start mock review in background
    thread = threading.Thread(target=run_review_background, args=(current_session,))
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'message': 'Mock review started',
        'session_id': session_id
    })

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

@app.route('/agent-outputs')
def get_agent_outputs():
    """Get real-time agent outputs"""
    global current_session
    
    if current_session is None:
        return jsonify({'error': 'No active session'}), 404
    
    return jsonify({
        'agent_outputs': current_session.agent_outputs,
        'status': current_session.status,
        'progress': current_session.progress,
        'current_step': current_session.current_step
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'service': 'Elite Scientific Review Crew'
    })

if __name__ == '__main__':
    print(" Elite Scientific Review Crew - Web Application")
    print("=" * 60)
    print(" Starting retro terminal interface...")
    print(" Access at: http://localhost:5000")
    print(" Mission: Restore scientific integrity to academic publishing")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
