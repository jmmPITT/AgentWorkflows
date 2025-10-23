# Agent Workflows Repository

A collection of advanced AI agent workflows demonstrating multi-agent systems, data analysis, and intelligent automation.

## 🤖 Projects

### 1. Paper Review System
A comprehensive AI-powered scientific paper review system that combines automated analysis with an interactive web interface. Features multi-agent analysis across 9 scientific disciplines with real-time progress tracking and interactive reporting.

### 2. Transaction History Analysis
An intelligent financial analysis system that processes transaction data and generates comprehensive business insights using AI agents. Provides automated data processing, visualization, and business intelligence generation.

## 📁 Repository Structure

```
AgentWorkflows/
├── paper_review/                     # Scientific Paper Review System
│   ├── scientific_review_crew/       # Core AI agent system
│   ├── scientific_review_webapp/     # Interactive web application
│   └── README.md                     # Paper review documentation
└── TransactionHistoryAnalysis/       # Financial Analysis System
    ├── app.py                        # Main application
    ├── app_agents.py                 # Agent definitions
    ├── example_outputs/              # Sample analysis results
    └── README.md                     # Transaction analysis documentation
```

## 🚀 Quick Start

### Paper Review System
```bash
cd paper_review/scientific_review_webapp
python complete_app.py
# Open http://localhost:5000
```

### Transaction History Analysis
```bash
cd TransactionHistoryAnalysis
python app.py
# Follow the prompts for data analysis
```

## 🌟 Key Features

### Paper Review System
- **9 Specialist AI Agents**: Mathematics, Physics, Chemistry, Biology, Engineering, Computer Science, Data Science, Medical, AI
- **Interactive Web Interface**: Retro terminal design with real-time progress
- **Comprehensive Analysis**: PDF processing, web search integration, detailed reporting
- **Editorial Decision Making**: Publication recommendations with reasoning

### Transaction History Analysis
- **Financial AI Agents**: Specialized agents for different financial aspects
- **Automated Visualization**: Chart and graph generation
- **Business Intelligence**: Natural language reports and insights
- **Data Processing**: Transaction categorization and trend analysis

## 🔧 Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/jmmPITT/AgentWorkflows.git
   cd AgentWorkflows
   ```

2. **Install Dependencies**:
   ```bash
   # For Paper Review System
   pip install -r paper_review/scientific_review_crew/requirements.txt
   pip install -r paper_review/scientific_review_webapp/requirements.txt
   
   # For Transaction Analysis
   pip install -r TransactionHistoryAnalysis/requirements.txt
   ```

3. **Configure API Keys**:
   - Google Cloud Platform (Gemini API)
   - Serper API (Web Search)
   - Set environment variables or use `.env` files

## 📊 Output Examples

### Paper Review System
- Individual specialist reviews (9 disciplines)
- Synthesis report combining all insights
- Editorial decision with publication recommendation
- Real-time agent progress tracking

### Transaction History Analysis
- Financial trend visualizations
- Business intelligence reports
- Cash flow analysis charts
- Transaction categorization insights

## 🎯 Mission

**"Demonstrating the power of AI agents in real-world applications"**

This repository showcases advanced multi-agent systems solving complex problems across scientific research and financial analysis domains.

## 📚 Documentation

Each project contains detailed documentation:
- **Paper Review**: `paper_review/README.md`
- **Transaction Analysis**: `TransactionHistoryAnalysis/README.md`

## 🤝 Contributing

This repository demonstrates professional AI agent workflows suitable for:
- Job interviews and portfolio demonstrations
- Learning multi-agent system design
- Understanding AI application development
- Business intelligence and research automation

---

**Built with ❤️ for the AI community**
