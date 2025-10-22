#!/usr/bin/env python3
"""
Elite Scientific Review Crew - Main Entry Point

This is the main entry point for the Elite Scientific Review Crew system.
It provides a command-line interface for running scientific reviews.
"""

import argparse
import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from run_review import run_scientific_review

def main():
    """Main entry point for the Elite Scientific Review Crew"""
    parser = argparse.ArgumentParser(
        description="Elite Scientific Review Crew - AI-powered scientific review system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python elite_review.py research_paper.pdf
  python elite_review.py --help
  python elite_review.py --version
        """
    )
    
    parser.add_argument(
        "pdf_path",
        nargs="?",
        default="research_paper.pdf",
        help="Path to the PDF file to review (default: research_paper.pdf)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="Elite Scientific Review Crew 1.0.0"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Check if PDF file exists
    if not os.path.exists(args.pdf_path):
        print(f"❌ Error: PDF file not found: {args.pdf_path}")
        print("Please ensure the PDF file exists and try again.")
        sys.exit(1)
    
    # Check if .env file exists
    if not os.path.exists(".env"):
        print("⚠️ Warning: .env file not found")
        print("Please create .env file with your credentials (see env.example)")
        print("Continuing with environment variables...")
    
    print("🚀 Elite Scientific Review Crew")
    print("=" * 50)
    print(f"📄 Reviewing: {args.pdf_path}")
    print(f"🔧 Verbose mode: {'ON' if args.verbose else 'OFF'}")
    print("=" * 50)
    
    try:
        # Run the scientific review
        result = run_scientific_review(args.pdf_path)
        
        if result:
            print("\n🎉 Review completed successfully!")
            print(f"📊 Final Decision: {result}")
        else:
            print("\n❌ Review failed. Check the logs for details.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Review interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
