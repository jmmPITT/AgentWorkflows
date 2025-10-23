# Elite Scientific Review Crew - Makefile

.PHONY: help install test clean format lint run setup

# Default target
help:
	@echo "Elite Scientific Review Crew - Available Commands:"
	@echo ""
	@echo "  install    - Install dependencies and setup environment"
	@echo "  test       - Run test suite"
	@echo "  clean      - Clean up generated files"
	@echo "  format     - Format code with black"
	@echo "  lint       - Lint code with flake8"
	@echo "  run        - Run review on research_paper.pdf"
	@echo "  setup      - Complete setup process"
	@echo "  help       - Show this help message"

# Install dependencies
install:
	@echo "Installing dependencies..."
	python install.py

# Run tests
test:
	@echo "Running tests..."
	python -m pytest tests/ -v

# Clean up generated files
clean:
	@echo "Cleaning up..."
	rm -rf __pycache__/
	rm -rf src/__pycache__/
	rm -rf src/tools/__pycache__/
	rm -rf tests/__pycache__/
	rm -rf .pytest_cache/
	rm -rf output/
	rm -rf reports/
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "*.pyd" -delete

# Format code
format:
	@echo "Formatting code..."
	black src/ tests/ *.py

# Lint code
lint:
	@echo "Linting code..."
	flake8 src/ tests/ *.py --max-line-length=127 --ignore=E203,W503

# Run review
run:
	@echo "Running scientific review..."
	python elite_review.py research_paper.pdf

# Complete setup
setup: install
	@echo "Setup complete!"
	@echo "Next steps:"
	@echo "1. Edit .env file with your credentials"
	@echo "2. Run: gcloud auth application-default login"
	@echo "3. Place your PDF file as 'research_paper.pdf'"
	@echo "4. Run: make run"
