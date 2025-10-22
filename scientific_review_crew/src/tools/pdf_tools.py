import fitz  # PyMuPDF
import os
from crewai.tools.base_tool import BaseTool
from typing import List, Dict, Any

class PDFTool(BaseTool):
    name: str = "Page-Based PDF Processor"
    description: str = (
        "Processes research papers by extracting complete pages as images with corresponding text. "
        "Optimized for AI analysis - provides high-quality page images and text for vision-language models. "
        "No image fragmentation - just complete pages that AI can understand."
    )

    def _run(self, pdf_path: str) -> Dict[str, Any]:
        if not os.path.exists(pdf_path):
            return {"pages": [], "error": f"File not found: {pdf_path}"}
        
        doc = fitz.open(pdf_path)
        pages_data = []
        
        # Create output directory
        pages_dir = "output/pages"
        os.makedirs(pages_dir, exist_ok=True)
        
        try:
            for page_num, page in enumerate(doc):
                # Extract text from the page
                page_text = page.get_text()
                
                # Create high-quality page image
                page_image_path = self._create_page_image(page, page_num, pages_dir)
                
                # Create page data structure
                page_data = {
                    "page_number": page_num + 1,
                    "text": page_text,
                    "image_path": page_image_path,
                    "text_length": len(page_text),
                    "has_content": len(page_text.strip()) > 0
                }
                
                pages_data.append(page_data)
        
        finally:
            doc.close()
        
        return {
            "pages": pages_data,
            "summary": {
                "total_pages": len(pages_data),
                "pages_with_content": len([p for p in pages_data if p["has_content"]]),
                "total_text_length": sum(p["text_length"] for p in pages_data)
            }
        }
    
    def _create_page_image(self, page, page_num: int, output_dir: str) -> str:
        """Create a high-quality page image for vision model input"""
        try:
            # Use high resolution for better quality (3x zoom)
            mat = fitz.Matrix(3.0, 3.0)
            pix = page.get_pixmap(matrix=mat)
            filename = f"page_{page_num+1}.png"
            image_path = os.path.join(output_dir, filename)
            pix.save(image_path)
            return image_path
        except Exception as e:
            print(f"Error creating page image for page {page_num + 1}: {e}")
            return None
