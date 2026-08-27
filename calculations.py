"""
Calculation helpers for invoice line items, tax breakdown, and currency formatting.
"""
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Tuple, Any


def round_curr(val: float | Decimal) -> Decimal:
    """Round a currency value to 2 decimal places using standard half-up rounding."""
    return Decimal(str(val)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def split_rs_paise(amount: float | Decimal | str) -> Tuple[str, str]:
    """
    Split a monetary amount into Rupees and Paise strings.
    Example: 1250.75 -> ('1,250', '75')
    Example: 500.00  -> ('500', '00')
    Example: None    -> ('-', '-')
    """
    if amount is None or str(amount).strip() == "" or str(amount).strip() == "-":
        return ("-", "-")
    try:
        dec = round_curr(amount)
        if dec == Decimal("0.00"):
            return ("0", "00")
        
        int_part = int(dec)
        paise_part = int(abs(dec - int_part) * 100)
        
        # Format integer part with Indian commas if needed, or standard comma
        rs_str = format_indian_currency(int_part)
        paise_str = f"{paise_part:02d}"
        return (rs_str, paise_str)
    except Exception:
        return (str(amount), "00")


def format_indian_currency(number: int | float | Decimal) -> str:
    """
    Format a number in the Indian numbering system:
    100000 -> 1,00,000
    10000000 -> 1,00,00,000
    """
    try:
        n = int(number)
        s = str(abs(n))
        if len(s) <= 3:
            res = s
        else:
            last3 = s[-3:]
            remaining = s[:-3]
            groups = []
            while len(remaining) > 2:
                groups.insert(0, remaining[-2:])
                remaining = remaining[:-2]
            if remaining:
                groups.insert(0, remaining)
            res = ",".join(groups) + "," + last3
        return f"-{res}" if n < 0 else res
    except Exception:
        return str(number)


def calculate_invoice_totals(
    items: List[Dict[str, Any]],
    cgst_rate: float = 9.0,
    sgst_rate: float = 9.0,
    igst_rate: float = 0.0,
    is_interstate: bool = False
) -> Dict[str, Any]:
    """
    Calculate comprehensive invoice totals from line items and tax rates.
    
    Returns a dictionary with:
    - calculated_items: List of items with normalized qty, rate, amount
    - subtotal: float
    - cgst_rate: float
    - cgst_amount: float
    - sgst_rate: float
    - sgst_amount: float
    - igst_rate: float
    - igst_amount: float
    - total_tax: float
    - grand_total: float
    """
    calculated_items = []
    subtotal = Decimal("0.00")

    for i, item in enumerate(items, start=1):
        try:
            qty = Decimal(str(item.get("quantity", 1) or 1))
        except Exception:
            qty = Decimal("1")

        try:
            rate = Decimal(str(item.get("rate", 0) or 0))
        except Exception:
            rate = Decimal("0")

        amount = (qty * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        subtotal += amount

        calculated_items.append({
            "s_no": item.get("s_no", i),
            "description": str(item.get("description", "")),
            "hsn_code": str(item.get("hsn_code", "")),
            "quantity": float(qty),
            "unit": str(item.get("unit", "")),
            "rate": float(rate),
            "amount": float(amount)
        })

    subtotal_curr = subtotal.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    if is_interstate:
        # Inter-state: Only IGST applies
        cgst_r = 0.0
        sgst_r = 0.0
        igst_r = float(igst_rate) if igst_rate > 0 else (float(cgst_rate) + float(sgst_rate))
        
        cgst_amt = Decimal("0.00")
        sgst_amt = Decimal("0.00")
        igst_amt = (subtotal_curr * Decimal(str(igst_r)) / Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    else:
        # Intra-state: CGST and SGST apply
        cgst_r = float(cgst_rate)
        sgst_r = float(sgst_rate)
        igst_r = 0.0
        
        cgst_amt = (subtotal_curr * Decimal(str(cgst_r)) / Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        sgst_amt = (subtotal_curr * Decimal(str(sgst_r)) / Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        igst_amt = Decimal("0.00")

    total_tax = (cgst_amt + sgst_amt + igst_amt).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    grand_total = (subtotal_curr + total_tax).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    return {
        "items": calculated_items,
        "subtotal": float(subtotal_curr),
        "cgst_rate": cgst_r,
        "cgst_amount": float(cgst_amt),
        "sgst_rate": sgst_r,
        "sgst_amount": float(sgst_amt),
        "igst_rate": igst_r,
        "igst_amount": float(igst_amt),
        "total_tax": float(total_tax),
        "grand_total": float(grand_total)
    }
