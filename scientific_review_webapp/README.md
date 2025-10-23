# 🌐 Elite Scientific Review Web Application

Interactive web interface for the Elite Scientific Review Crew system, featuring a retro terminal aesthetic and real-time multi-agent progress tracking.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google Cloud Platform account with Vertex AI enabled
- Serper API key for web search verification

### Installation

1. **Navigate to webapp directory**
```bash
cd scientific_review_webapp
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

4. **Set up environment variables**
```bash
# Copy the .env file from parent directory
cp ../.env .
# Or create your own with:
# GCP_PROJECT_ID=your-gcp-project-id
# GCP_REGION=us-central1
# SERPER_API_KEY=your-serper-api-key
```

5. **Start the web application**
```bash
python complete_app.py
```

6. **Open your browser** and go to `http://localhost:5000`

## 🎨 Features

### Retro Terminal Interface
- **Authentic 80s Computing**: Green phosphor display with scanlines
- **Monospace Typography**: JetBrains Mono font for authentic terminal feel
- **Interactive Elements**: Hover effects and button animations
- **Responsive Design**: Works on desktop and mobile

### Real-time Progress Tracking
- **Live Agent Updates**: See specialist agents working in real-time
- **Status Messages**: Detailed logging of all operations
- **Progress Indicators**: Visual feedback during analysis
- **Error Handling**: Clear error messages and recovery

### Interactive Report Viewer
- **Specialist Buttons**: Click any specialist to view their report
- **Modal Windows**: Full-screen report viewing
- **Markdown Rendering**: Professional formatting
- **Easy Navigation**: Simple close buttons

### Session Management
- **Automatic Recovery**: Sessions persist across restarts
- **File Upload**: Drag & drop PDF upload
- **Report Storage**: Organized, timestamped directories
- **State Persistence**: Progress maintained across browser sessions

## 📁 Webapp Structure

```
scientific_review_webapp/
├── complete_app.py          # Main Flask application
├── run_review.py            # Crew execution with web integration
├── requirements.txt         # Python dependencies
├── templates/
│   └── terminal.html        # Retro terminal interface
├── reports/                 # Generated review reports
├── uploads/                 # PDF upload storage
└── README.md               # This file
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file with:
```bash
GCP_PROJECT_ID=your-gcp-project-id
GCP_REGION=us-central1
SERPER_API_KEY=your-serper-api-key
```

### Flask Configuration
The webapp runs on:
- **Host**: localhost
- **Port**: 5000
- **Debug Mode**: Enabled (auto-reload on file changes)

## 🎯 Usage

1. **Upload PDF**: Drag & drop your research paper
2. **Watch Progress**: See real-time agent updates
3. **View Results**: Click specialist buttons to read reports
4. **Download Reports**: All reports saved to `reports/` directory

## 🐛 Troubleshooting

### Common Issues

**"Scientific review system not available"**
- Check that all environment variables are set
- Verify Google Cloud authentication: `gcloud auth application-default login`
- Ensure Serper API key is valid

**"No active session" errors**
- The webapp automatically recovers completed sessions
- If issues persist, restart the webapp
- Check that reports exist in the `reports/` directory

**PDF upload fails**
- Ensure file is a valid PDF
- Check file size (max 50MB)
- Verify uploads directory exists and is writable

### Debug Mode
The webapp runs in debug mode by default. Check the terminal for detailed error messages and logs.

## 🔄 API Endpoints

- `GET /` - Main interface
- `POST /upload` - PDF upload
- `GET /status` - Session status
- `GET /reports` - List available reports
- `GET /report/<name>` - Get specific report
- `GET /reset` - Reset session

## 🎉 Success!

You now have a fully functional web application for scientific review! The retro terminal interface provides an engaging way to interact with the multi-agent review system.

---

*"Journals are big business, not science. We are returning to science!"*
