# Elite Scientific Review Crew - Web Application

A retro 1980s AI movie-styled web interface for the Elite Scientific Review Crew system. This application provides a terminal-style interface for uploading scientific papers and receiving comprehensive multi-agent reviews.

## 🎯 Mission

"Journals are big business, not science. We are returning to science!"

This system uses an elite crew of AI specialists to conduct rigorous, uncompromising scientific reviews that prioritize scientific integrity over commercial appeal.

## 🚀 Features

- **Retro Terminal Interface**: Authentic 1980s AI movie aesthetic with green text on black background
- **PDF Upload**: Drag & drop or click to upload scientific papers (up to 50MB)
- **Multi-Agent Review**: 9 specialist reviewers across different scientific domains
- **Real-time Progress**: Live progress tracking with terminal-style status updates
- **Comprehensive Reports**: Individual specialist reports, synthesis, and editorial decision
- **Interactive Report Viewing**: Click on any report to view detailed analysis in a modal
- **Matrix Background Effect**: Animated falling characters for authentic retro feel
- **Scan Lines**: CRT monitor-style scan lines for immersive experience

## 🛠️ Installation

### Prerequisites

1. Python 3.8 or higher
2. Google Cloud Platform account with Vertex AI enabled
3. Serper API key for web search functionality

### Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   Create a `.env` file in the `scientific_review_crew` directory:
   ```env
   GCP_PROJECT_ID=your-gcp-project-id
   GCP_REGION=us-central1
   SERPER_API_KEY=your-serper-api-key
   ```

3. **Set up Google Cloud Authentication**
   ```bash
   gcloud auth application-default login
   ```

## 🎮 Usage

### Quick Start

1. **Launch the Application**
   ```bash
   python start_app.py
   ```
   
   Or directly:
   ```bash
   python app.py
   ```

2. **Access the Interface**
   Open your browser and navigate to: `http://localhost:5000`

3. **Upload a Paper**
   - Click the upload area or drag & drop a PDF file
   - Wait for the elite review crew to process your paper
   - Monitor progress with the terminal-style progress bar

4. **View Results**
   - See the editorial decision (PUBLISH/REJECT)
   - Click on specialist reports to view detailed analysis
   - Access synthesis and editorial decision reports

### Interface Elements

- **Upload Area**: Green dashed border for file upload
- **Progress Bar**: Terminal-style progress indicator
- **Report Cards**: Clickable cards for each specialist report
- **Modal Viewer**: Full-screen report viewing with terminal styling
- **Matrix Effect**: Animated falling characters in background
- **Scan Lines**: CRT monitor effect overlay

## 🎨 Design Philosophy

The interface is designed to evoke the aesthetic of 1980s AI movies like:
- **WarGames** (1983)
- **Tron** (1982)
- **The Terminator** (1984)
- **Blade Runner** (1982)

### Visual Elements

- **Color Scheme**: Black background with bright green text (#00ff00)
- **Typography**: JetBrains Mono monospace font
- **Effects**: Glowing text, scan lines, matrix rain
- **Animations**: Smooth transitions and terminal-style typing effects
- **Layout**: Terminal-inspired with bordered sections

## 🔧 Technical Details

### Architecture

- **Backend**: Flask web application
- **AI Engine**: CrewAI with multiple specialist agents
- **LLM**: Google Vertex AI Gemini 2.5 Flash
- **PDF Processing**: PyMuPDF for text and image extraction
- **Web Search**: Serper API for claim verification

### Specialist Agents

1. **Medical Expert**: Clinical and medical research analysis
2. **Engineering Expert**: Engineering and technical review
3. **Physics Expert**: Physics and theoretical analysis
4. **Chemistry Expert**: Chemical and materials science review
5. **Biology Expert**: Biological and life sciences analysis
6. **Computer Science Expert**: CS and software engineering review
7. **Mathematics Expert**: Mathematical rigor and proof analysis
8. **AI Expert**: Artificial intelligence and machine learning review
9. **Data Science Expert**: Statistical analysis and data integrity

### Review Process

1. **PDF Processing**: Extract text and images from uploaded paper
2. **Parallel Analysis**: All 9 specialists review simultaneously
3. **Synthesis**: Compile specialist reports into comprehensive assessment
4. **Editorial Decision**: Final PUBLISH/REJECT decision with justification
5. **Report Generation**: Save all reports as markdown files

## 📁 File Structure

```
scientific_review_webapp/
├── app.py                 # Main Flask application
├── start_app.py          # Application launcher with checks
├── requirements.txt      # Python dependencies
├── templates/
│   └── terminal.html     # Retro terminal interface
├── uploads/              # Temporary file storage
└── reports/              # Generated review reports
```

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure the `scientific_review_crew` directory is in the correct location
   - Check that all dependencies are installed

2. **Environment Variables**
   - Verify `.env` file exists in `scientific_review_crew` directory
   - Check that all required variables are set

3. **Google Cloud Authentication**
   - Run `gcloud auth application-default login`
   - Ensure your GCP project has Vertex AI enabled

4. **File Upload Issues**
   - Check file size (max 50MB)
   - Ensure file is a valid PDF

### Debug Mode

Run with debug mode for detailed error information:
```bash
python app.py
```

## 🎯 Future Enhancements

- [ ] User authentication and session management
- [ ] Batch processing for multiple papers
- [ ] Export reports in various formats
- [ ] Advanced filtering and search
- [ ] Real-time collaboration features
- [ ] Mobile-responsive design
- [ ] Additional retro effects and animations

## 📄 License

This project is part of the Elite Scientific Review Crew system. See the main project for licensing information.

## 🤝 Contributing

Contributions are welcome! Please ensure any changes maintain the retro aesthetic and scientific rigor of the review process.

---

**Remember**: This system is designed to restore scientific integrity to academic publishing. Every review is conducted with uncompromising standards and zero tolerance for commercial interests over scientific merit.