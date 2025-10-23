# Elite Scientific Review Crew

A revolutionary AI-powered scientific review system that restores integrity to academic publishing by employing uncompromising standards for scientific rigor, reproducibility, and intellectual honesty.

## 🎯 Mission

**"Journals are big business, not science. We are returning to science!"**

This system represents a paradigm shift from commercial publishing interests back to genuine scientific advancement. Our elite reviewers evaluate papers based on uncompromising scientific standards, rejecting the current culture of publishing for clicks, citations, or trendy topics.

## ✨ Features

### 🌐 **NEW: Interactive Web Application**
- **Retro Terminal Interface**: Beautiful old-school computing aesthetic with green-on-black display
- **Real-time Progress Tracking**: Live updates from all specialist agents during analysis
- **Interactive Specialist Reports**: Click any specialist button to view detailed reports in pop-out windows
- **Drag & Drop Upload**: Easy PDF upload with visual feedback
- **Session Management**: Automatic session recovery and persistent state
- **Responsive Design**: Works on desktop and mobile devices

### 🔬 Elite Scientific Reviewers
- **9 Specialist Domains**: Medical, Engineering, Physics, Chemistry, Biology, Computer Science, Mathematics, Artificial Intelligence, Data Science
- **Uncompromising Standards**: Focus on methodological rigor, reproducibility, statistical soundness, and intellectual honesty
- **Zero Tolerance**: For p-hacking, selective reporting, or research designed for commercial appeal
- **Parallel Processing**: All specialist reviews run simultaneously for efficiency

### 📊 Comprehensive Analysis
- **Multimodal Review**: Analyzes both text content and figures/images
- **Web Verification**: Automatically verifies key claims using web search
- **Figure Analysis**: Critical evaluation of all figures, graphs, and visualizations
- **Reproducibility Assessment**: Evaluates potential for independent replication

### 🤖 AI-Powered Intelligence
- **Gemini 2.5 Flash**: Latest Google AI model for superior reasoning
- **Parallel Execution**: Multiple reviewers work simultaneously
- **Intelligent Synthesis**: Compiler agent weaves together diverse perspectives
- **Final Gatekeeping**: Elite editor makes publication decisions based on scientific merit

### 📝 Detailed Reporting
- **Individual Specialist Reports**: Each domain expert provides detailed analysis
- **Comprehensive Synthesis**: Unified assessment highlighting consensus and disagreement
- **Editorial Decision**: Clear publish/reject decision with detailed justification
- **Interactive Report Viewer**: Click specialist buttons to view full reports in modal windows
- **Markdown Output**: All reports saved as professional markdown files

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google Cloud Platform account with Vertex AI enabled
- Serper API key for web search verification

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/elite-scientific-review-crew.git
cd elite-scientific-review-crew
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up Google Cloud authentication**
```bash
gcloud auth application-default login
```

5. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your credentials
```

### Usage

#### 🌐 **Web Application (Recommended)**

1. **Start the web application**
```bash
cd scientific_review_webapp
python complete_app.py
```

2. **Open your browser** and go to `http://localhost:5000`

3. **Upload your PDF** using the drag & drop interface

4. **Watch real-time progress** as specialist agents analyze your paper

5. **View results** with interactive specialist report buttons

#### 💻 **Command Line Interface**

1. **Place your research paper PDF** in the project directory as `research_paper.pdf`

2. **Run the review**
```bash
python run_review.py
```

3. **View results** in the `reports/` directory with timestamped folders

## 📁 Project Structure

```
scientific_review_crew/
├── scientific_review_webapp/    # 🌐 NEW: Interactive Web Application
│   ├── complete_app.py         # Main Flask web application
│   ├── run_review.py           # Crew execution with web integration
│   ├── templates/
│   │   └── terminal.html       # Retro terminal interface
│   ├── reports/                # Webapp-specific reports directory
│   └── uploads/                # PDF upload storage
├── src/
│   ├── agents.py               # Elite reviewer agent definitions
│   ├── tasks.py                # Review task configurations
│   ├── crew.py                 # Crew assembly and execution
│   └── tools/
│       ├── pdf_tools.py        # PDF processing and page extraction
│       └── search_tools.py     # Web search verification
├── reports/                    # Generated review reports
│   └── research_paper_*/       # Timestamped review sessions
├── output/                     # PDF processing outputs
│   └── pages/                  # Extracted page images
├── main.py                     # LLM configuration
├── run_review.py               # Command-line execution script
├── requirements.txt            # Python dependencies
├── .env.example               # Environment configuration template
└── README.md                  # This file
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
GCP_PROJECT_ID=your-gcp-project-id
GCP_REGION=us-central1
SERPER_API_KEY=your-serper-api-key
```

### LLM Configuration
The system uses Google's Gemini 2.5 Flash model with configurable temperature:
- **Temperature 0.1**: More consistent, deterministic reviews
- **Temperature 0.3**: More diverse perspectives (recommended)
- **Temperature 0.5+**: Higher creativity and variability

## 📊 Example Output

The system generates comprehensive reports including:

- **Specialist Reports**: Individual domain expert analyses
- **Synthesis Report**: Unified assessment from all reviewers
- **Editorial Decision**: Final publish/reject decision with justification
- **Review Summary**: Overview of the entire review process

See the `reports/` directory for example outputs from real scientific papers.

## 🌐 Web Application Features

### 🎨 **Retro Terminal Interface**
- **Authentic 80s Computing**: Green phosphor display with scanlines and monospace fonts
- **Interactive Elements**: Hover effects, button animations, and visual feedback
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Accessibility**: High contrast and clear typography for readability

### 📊 **Real-time Progress Tracking**
- **Live Agent Updates**: See each specialist agent's progress in real-time
- **Status Messages**: Detailed logging of PDF processing, crew deployment, and analysis
- **Progress Indicators**: Visual feedback during long-running operations
- **Error Handling**: Clear error messages and recovery suggestions

### 🔍 **Interactive Report Viewer**
- **Specialist Report Buttons**: Click any specialist to view their detailed analysis
- **Modal Windows**: Full-screen report viewing with proper formatting
- **Markdown Rendering**: Professional formatting with headers, lists, and emphasis
- **Easy Navigation**: Simple close buttons and keyboard shortcuts

### 💾 **Session Management**
- **Automatic Recovery**: Sessions persist across webapp restarts
- **File Upload**: Drag & drop PDF upload with validation
- **Report Storage**: All reports saved in organized, timestamped directories
- **State Persistence**: Review progress maintained even if browser is closed

## 🎯 Review Criteria

Our elite reviewers evaluate papers based on:

1. **Methodological Rigor**: Experimental design, controls, sample sizes
2. **Reproducibility**: Statistical soundness, data availability, code sharing
3. **Genuine Novelty**: Real intellectual contribution vs. superficial innovation
4. **Logical Consistency**: Theoretical grounding, internal coherence
5. **Appropriate Scope**: Realistic claims, appropriate methodology
6. **Ethical Standards**: Conflicts of interest, research ethics
7. **Scientific Integrity**: No p-hacking, selective reporting, or data manipulation

## 🤝 Contributing

We welcome contributions to improve scientific review standards:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **CrewAI**: Multi-agent framework for AI collaboration
- **Google Vertex AI**: Advanced language model capabilities
- **PyMuPDF**: PDF processing and image extraction
- **Serper API**: Web search verification

## 📞 Support

For questions, issues, or suggestions:
- Open an issue on GitHub
- Contact the maintainers
- Join our scientific integrity community

---

**Remember**: We are not just reviewing papers; we are restoring the noble purpose of scientific publishing and rebuilding public trust in science through uncompromising standards of excellence.

*"The goal is not to publish more papers, but to publish better science."*
