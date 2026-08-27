"""
High-Resolution PDF to PIL Image conversion service for real-time GUI preview.
Uses PyMuPDF for lightning fast vector rasterization.
"""
from pathlib import Path
from typing import Optional
from PIL import Image
import pymupdf


class PreviewService:
    @staticmethod
    def render_pdf_to_image(pdf_path: Path | str, page_number: int = 0, dpi: int = 150) -> Optional[Image.Image]:
        """
        Render a single PDF page to a PIL Image at high DPI.
        """
        try:
            doc = pymupdf.open(str(pdf_path))
            if page_number >= len(doc):
                page_number = 0

            page = doc[page_number]
            zoom = dpi / 72.0  # 72 is standard PDF point resolution
            mat = pymupdf.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)

            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            doc.close()
            return img
        except Exception as e:
            print(f"Error rendering PDF preview: {e}")
            return None
