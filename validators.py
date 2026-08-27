"""
Form validation utilities for GSTIN, PAN, Dates, and Invoice Fields.
"""
import re
from datetime import datetime
from typing import Dict, List, Tuple, Any


def validate_gstin(gstin: str) -> bool:
    """Validate Indian GSTIN format (15 characters)."""
    if not gstin:
        return True  # Optional field
    pattern = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"
    return bool(re.match(pattern, gstin.strip().upper()))


def validate_pan(pan: str) -> bool:
    """Validate Indian PAN format (10 characters)."""
    if not pan:
        return True  # Optional field
    pattern = r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$"
    return bool(re.match(pattern, pan.strip().upper()))


def validate_date(date_str: str) -> bool:
    """Validate standard date format (DD/MM/YYYY or YYYY-MM-DD)."""
    if not date_str:
        return False
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            datetime.strptime(date_str.strip(), fmt)
            return True
        except ValueError:
            continue
    return False


def validate_invoice_payload(invoice_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate all fields of an invoice before generation or saving.
    Returns (is_valid, list_of_error_messages).
    """
    errors = []

    # Invoice Number
    inv_no = str(invoice_data.get("invoice_no", "")).strip()
    if not inv_no:
        errors.append("Invoice Number is required.")

    # Invoice Date
    inv_date = str(invoice_data.get("invoice_date", "")).strip()
    if not inv_date:
        errors.append("Invoice Date is required.")
    elif not validate_date(inv_date):
        errors.append("Invoice Date format is invalid (expected DD/MM/YYYY or YYYY-MM-DD).")

    # Customer Name / Billed To
    billed_to_name = str(invoice_data.get("billed_to_name", "")).strip()
    if not billed_to_name:
        errors.append("Customer Name (Billed To) is required.")

    # Items validation
    items = invoice_data.get("items", [])
    if not items or len(items) == 0:
        errors.append("At least one line item is required.")
    else:
        for idx, item in enumerate(items, start=1):
            desc = str(item.get("description", "")).strip()
            if not desc:
                errors.append(f"Item #{idx}: Description of Goods is required.")

            try:
                qty = float(item.get("quantity", 0))
                if qty <= 0:
                    errors.append(f"Item #{idx}: Quantity must be greater than 0.")
            except (ValueError, TypeError):
                errors.append(f"Item #{idx}: Quantity must be a valid number.")

            try:
                rate = float(item.get("rate", -1))
                if rate < 0:
                    errors.append(f"Item #{idx}: Rate must be 0 or positive.")
            except (ValueError, TypeError):
                errors.append(f"Item #{idx}: Rate must be a valid number.")

    return (len(errors) == 0, errors)
