# Paper Review System

A comprehensive AI-powered scientific paper review system that combines automated analysis with an interactive web interface.

## 🎯 Overview

This project provides a complete solution for scientific paper review, featuring:
- **Multi-agent AI system** for comprehensive paper analysis
- **Interactive web application** with retro terminal interface
- **Real-time progress tracking** and agent output monitoring
- **Specialist report generation** across multiple scientific disciplines
- **Editorial decision synthesis** based on expert reviews

## 📁 Project Structure

```
paper_review/
├── scientific_review_crew/           # Core AI agent system
│   ├── src/                          # Agent definitions and tools
│   ├── reports/                      # Generated review reports
│   ├── run_review.py                 # Main execution script
│   └── README.md                     # Detailed documentation
└── scientific_review_webapp/         # Interactive web application
    ├── complete_app.py               # Main Flask application
    ├── templates/terminal.html       # Retro terminal interface
    ├── reports/                      # Webapp-specific reports
    └── README.md                     # Webapp documentation
```

## 🚀 Quick Start

### Option 1: Web Application (Recommended)
```bash
cd scientific_review_webapp
python complete_app.py
# Open http://localhost:5000
```

### Option 2: Command Line Interface
```bash
cd scientific_review_crew
python run_review.py
```

## 🌟 Features

### Multi-Agent Analysis
- **9 Specialist Agents**: Mathematics, Physics, Chemistry, Biology, Engineering, Computer Science, Data Science, Medical, AI
- **Synthesis Agent**: Combines specialist insights
- **Editorial Agent**: Makes final publication decisions

### Interactive Web Interface
- **Retro Terminal Design**: Classic computing aesthetic
- **Real-time Progress**: Live agent output streaming
- **Interactive Reports**: Click to view specialist analyses
- **Drag & Drop Upload**: Easy PDF submission
- **Session Management**: Persistent review sessions

### Advanced Capabilities
- **PDF Processing**: Automatic text extraction and analysis
- **Web Search Integration**: Real-time fact-checking and context
- **Comprehensive Reporting**: Detailed markdown reports for each specialist
- **Editorial Decisions**: Publication recommendations with reasoning

## 🔧 Setup

1. **Install Dependencies**:
   ```bash
   pip install -r scientific_review_crew/requirements.txt
   pip install -r scientific_review_webapp/requirements.txt
   ```

2. **Configure API Keys**:
   - Google Cloud Platform (Gemini API)
   - Serper API (Web Search)
   - Set environment variables or use `.env` file

3. **Run the Application**:
   ```bash
   cd scientific_review_webapp
   python complete_app.py
   ```

## 📊 Output

The system generates comprehensive reports including:
- Individual specialist reviews (9 disciplines)
- Synthesis report combining all insights
- Editorial decision with publication recommendation
- Detailed analysis metrics and confidence scores

## 🎨 Design Philosophy

Built with a **retro computing aesthetic** that pays homage to the early days of scientific computing, while leveraging cutting-edge AI technology for modern research evaluation.

---

**"Journals are big business, not science. We are returning to science!"**
