#!/usr/bin/env python3
"""
Complete Scientific Review Crew System
Integrates PDF processing with multi-agent analysis
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from tools.pdf_tools import PDFTool
from src.crew import assemble_crew
from crewai.llm import LLM
from datetime import datetime

def save_reports_to_files(crew, final_result, pdf_path):
    """Save all reports to markdown files"""
    # Create reports directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    reports_dir = f"reports/{pdf_name}_{timestamp}"
    os.makedirs(reports_dir, exist_ok=True)
    
    # Save individual specialist reports
    for i, task in enumerate(crew.tasks[:-2]):  # Exclude synthesis and editorial tasks
        if hasattr(task, 'agent') and task.agent:
            domain = task.agent.role.replace("Expert ", "").replace(" Researcher", "")
            filename = f"{reports_dir}/specialist_{domain.lower().replace(' ', '_')}_report.md"
            
            # Get the task output
            if hasattr(task, 'output') and task.output:
                output_content = str(task.output) if task.output else ""
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"# {domain} Specialist Report\n\n")
                    f.write(f"**Reviewer:** {task.agent.role}\n")
                    f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write("---\n\n")
                    f.write(output_content)
                print(f"✅ Saved {domain} report: {filename}")
    
    # Save synthesis report
    synthesis_task = crew.tasks[-2]
    if hasattr(synthesis_task, 'output') and synthesis_task.output:
        synthesis_filename = f"{reports_dir}/synthesis_report.md"
        output_content = str(synthesis_task.output) if synthesis_task.output else ""
        with open(synthesis_filename, 'w', encoding='utf-8') as f:
            f.write("# Comprehensive Synthesis Report\n\n")
            f.write(f"**Compiler:** {synthesis_task.agent.role}\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            f.write(output_content)
        print(f"✅ Saved synthesis report: {synthesis_filename}")
    
    # Save editorial decision report
    editorial_task = crew.tasks[-1]
    if hasattr(editorial_task, 'output') and editorial_task.output:
        editorial_filename = f"{reports_dir}/editorial_decision.md"
        output_content = str(editorial_task.output) if editorial_task.output else ""
        with open(editorial_filename, 'w', encoding='utf-8') as f:
            f.write("# Editorial Decision Report\n\n")
            f.write(f"**Editor:** {editorial_task.agent.role}\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            f.write(output_content)
        print(f"✅ Saved editorial decision: {editorial_filename}")
    
    # Save final result summary
    summary_filename = f"{reports_dir}/review_summary.md"
    with open(summary_filename, 'w', encoding='utf-8') as f:
        f.write("# Scientific Review Summary\n\n")
        f.write(f"**Paper:** {pdf_path}\n")
        f.write(f"**Review Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Total Specialists:** {len(crew.tasks) - 2}\n\n")
        f.write("---\n\n")
        f.write("## Final Result\n\n")
        f.write(f"**Decision:** {final_result}\n\n")
        f.write("## Reports Generated\n\n")
        f.write("- Individual specialist reports (9 domains)\n")
        f.write("- Comprehensive synthesis report\n")
        f.write("- Editorial decision report\n")
        f.write("- This summary report\n")
    print(f"✅ Saved review summary: {summary_filename}")
    
    print(f"\n📁 All reports saved to: {reports_dir}")

def run_scientific_review(pdf_path: str):
    """Run the complete scientific review process"""
    print("=== Scientific Review Crew System ===")
    
    # Set environment variables directly
    os.environ["GCP_PROJECT_ID"] = "gothic-depth-474113-r1"
    os.environ["GCP_REGION"] = "us-central1"
    os.environ["SERPER_API_KEY"] = "a1e99f7a12e9e667b6927ec0006a469348815191"
    os.environ['GOOGLE_CLOUD_PROJECT'] = "gothic-depth-474113-r1"
    
    # Set up Gemini 2.5 Flash
    print("🔧 Setting up Gemini 2.5 Flash...")
    gemini_llm = LLM(
        model="vertex_ai/gemini-2.5-flash",
        api_key="",
        temperature=0.1
    )
    
    # Process the PDF
    print(f"📄 Processing PDF: {pdf_path}")
    pdf_tool = PDFTool()
    result = pdf_tool._run(pdf_path)
    
    print(f"✅ Processed {result['summary']['total_pages']} pages")
    print(f"✅ Extracted {result['summary']['total_text_length']:,} characters of text")
    
    # Prepare the paper content
    print("📝 Preparing paper content...")
    paper_text = ""
    figure_paths = []
    
    for page in result['pages']:
        paper_text += f"\n\n--- PAGE {page['page_number']} ---\n"
        paper_text += page['text']
        if page['image_path']:
            figure_paths.append(page['image_path'])
    
    figure_paths_str = "\n".join(figure_paths)
    
    # Assemble the crew
    print("👥 Assembling scientific review crew...")
    crew = assemble_crew(gemini_llm, paper_text, figure_paths_str)
    
    # Execute the review
    print("🚀 Starting scientific review...")
    print("=" * 60)
    
    try:
        result = crew.kickoff()
        print("=" * 60)
        print("✅ Scientific review completed!")
        
        # Save all reports to files
        print("💾 Saving reports to files...")
        save_reports_to_files(crew, result, pdf_path)
        
        print(f"\n📊 Final Result: {result}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error during review: {str(e)}")
        return None

if __name__ == "__main__":
    # Run the review on the research paper
    pdf_path = "research_paper.pdf"
    if os.path.exists(pdf_path):
        result = run_scientific_review(pdf_path)
        if result:
            print("\n🎉 Review completed successfully!")
        else:
            print("\n❌ Review failed!")
    else:
        print(f"❌ PDF file not found: {pdf_path}")
