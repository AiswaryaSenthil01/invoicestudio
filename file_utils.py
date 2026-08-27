"""
File system helper functions for organizing invoice PDFs and Word documents.
"""
import re
from datetime import datetime
from pathlib import Path
from src.config import INVOICES_DIR


def sanitize_filename(name: str) -> str:
    """Replace illegal characters for filenames with safe underscores."""
    return re.sub(r'[\\/*?:"<>|]', '_', str(name).strip())


def get_invoice_storage_path(invoice_no: str, invoice_date: str = None, extension: str = "pdf") -> Path:
    """
    Generate an organized file path: Invoices/<Year>/<Month_Name>/<Invoice_No>.<ext>
    Example: Invoices/2026/August/INV-001.pdf
    """
    now = datetime.now()
    if invoice_date:
        for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
            try:
                dt = datetime.strptime(invoice_date.strip(), fmt)
                year_str = dt.strftime("%Y")
                month_str = dt.strftime("%B")
                break
            except ValueError:
                year_str = now.strftime("%Y")
                month_str = now.strftime("%B")
    else:
        year_str = now.strftime("%Y")
        month_str = now.strftime("%B")

    target_dir = INVOICES_DIR / year_str / month_str
    target_dir.mkdir(parents=True, exist_ok=True)

    safe_inv_no = sanitize_filename(invoice_no)
    ext = extension.lstrip(".")
    return target_dir / f"{safe_inv_no}.{ext}"
