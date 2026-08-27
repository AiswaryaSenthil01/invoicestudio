"""
High-Fidelity PDF Generator using ReportLab.
Faithfully replicates and refines the reference GST Tax Invoice format.
"""
from pathlib import Path
from typing import Dict, Any, List
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit

from src.utils.calculations import split_rs_paise
from src.utils.number_to_words import amount_to_words
from src.utils.file_utils import get_invoice_storage_path


class PDFGenerator:
    def __init__(self):
        self.page_width, self.page_height = A4  # 595.27, 841.89

    def generate(self, invoice_data: Dict[str, Any], output_path: Path | str = None) -> Path:
        """
        Generate a professional GST Tax Invoice PDF matching the exact reference layout.
        """
        invoice_no = invoice_data.get("invoice_no", "INV-001")
        invoice_date = invoice_data.get("invoice_date", "")

        if output_path is None:
            output_path = get_invoice_storage_path(invoice_no, invoice_date, "pdf")
        else:
            output_path = Path(output_path)

        output_path.parent.mkdir(parents=True, exist_ok=True)

        c = canvas.Canvas(str(output_path), pagesize=A4)
        self._draw_invoice(c, invoice_data)
        c.save()

        return output_path

    def _draw_invoice(self, c: canvas.Canvas, data: Dict[str, Any]):
        # Coordinate Bounds
        x_left = 22.0
        x_right = 573.0
        width = x_right - x_left  # 551.0 pt
        y_top = 818.0
        y_bottom = 24.0
        height = y_top - y_bottom  # 794.0 pt

        # 1. Outer Box
        c.setLineWidth(1.0)
        c.setStrokeColor(colors.black)
        c.rect(x_left, y_bottom, width, height)

        # 2. Header Section
        gstin = data.get("company_gstin") or data.get("gstin") or "33BKXPS7582P1ZR"
        pan = data.get("company_pan") or data.get("pan") or "BKXPS7582P"
        copy_type = data.get("copy_type", "Original Copy")
        company_name = data.get("company_name", "NAMURA ENGG. WORKS")
        company_addr = data.get("company_address", "4/8, Balaji Nagar, Vilankurichi, Coimbatore-641035")
        company_phone = data.get("company_phone", "9842811245")
        company_state_code = data.get("company_state_code", "33")
        company_email = data.get("company_email", "namuraew@gmail.com")

        # Top Left: GSTIN & PAN
        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(x_left + 8, y_top - 16, "GSTIN NO:")
        c.setFont("Helvetica", 8.5)
        c.drawString(x_left + 58, y_top - 16, gstin)

        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(x_left + 8, y_top - 28, "PAN NO:")
        c.setFont("Helvetica", 8.5)
        c.drawString(x_left + 52, y_top - 28, pan)

        # Top Right: Copy Type
        c.setFont("Helvetica-Oblique", 9.5)
        c.drawRightString(x_right - 10, y_top - 16, copy_type)

        # Center Title & Company Details
        c.setFont("Helvetica-Bold", 12.5)
        c.drawCentredString(x_left + width / 2.0, y_top - 28, "TAX INVOICE")

        c.setFont("Helvetica-Bold", 11.5)
        c.drawCentredString(x_left + width / 2.0, y_top - 46, company_name)

        c.setFont("Helvetica", 8.5)
        c.drawCentredString(x_left + width / 2.0, y_top - 60, company_addr)
        
        phone_state_str = f"Phone No: {company_phone}    State Code: {company_state_code}"
        c.drawCentredString(x_left + width / 2.0, y_top - 73, phone_state_str)

        email_str = f"E-mail: {company_email}"
        c.drawCentredString(x_left + width / 2.0, y_top - 86, email_str)

        # Horizontal Line 1: Header to Meta Box
        y_h1 = y_top - 96.0  # 722.0
        c.setLineWidth(0.8)
        c.line(x_left, y_h1, x_right, y_h1)

        # 3. Invoice Meta Box
        y_h2 = y_h1 - 48.0   # 674.0
        x_mid = x_left + (width / 2.0)  # 297.5

        # Vertical Divider for Meta Box
        c.line(x_mid, y_h1, x_mid, y_h2)

        # Left Column Meta
        c.setFont("Helvetica", 8.5)
        c.drawString(x_left + 8, y_h1 - 16, "Invoice No   :")
        c.drawString(x_left + 8, y_h1 - 32, "Date            :")

        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(x_left + 72, y_h1 - 16, str(data.get("invoice_no", "")))
        c.drawString(x_left + 72, y_h1 - 32, str(data.get("invoice_date", "")))

        # Right Column Meta
        c.setFont("Helvetica", 8.5)
        c.drawString(x_mid + 8, y_h1 - 14, "P.O. No       :")
        c.drawString(x_mid + 8, y_h1 - 27, "P.O. Date    :")
        c.drawString(x_mid + 8, y_h1 - 40, "Vehicle No  :")

        c.drawString(x_mid + 70, y_h1 - 14, str(data.get("po_no", "") or ""))
        c.drawString(x_mid + 70, y_h1 - 27, str(data.get("po_date", "") or ""))
        c.drawString(x_mid + 70, y_h1 - 40, str(data.get("vehicle_no", "") or ""))

        # Horizontal Line 2: Meta to Party Box
        c.line(x_left, y_h2, x_right, y_h2)

        # 4. Party Details Box (Billed To / Shipped To)
        y_h3 = y_h2 - 82.0   # 592.0
        c.line(x_mid, y_h2, x_mid, y_h3)

        # Left Party: Billed To
        c.setFont("Helvetica-Bold", 9.0)
        c.drawString(x_left + 8, y_h2 - 14, "Billed To:")
        
        billed_name = data.get("billed_to_name", "")
        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(x_left + 8, y_h2 - 27, billed_name[:45])

        c.setFont("Helvetica", 8.0)
        billed_addr = data.get("billed_to_address", "")
        addr_lines = simpleSplit(billed_addr, "Helvetica", 8.0, x_mid - x_left - 16)
        curr_y = y_h2 - 39
        for line in addr_lines[:2]:
            c.drawString(x_left + 8, curr_y, line)
            curr_y -= 11

        billed_gstin = data.get("billed_to_gstin", "")
        billed_phone = data.get("billed_to_phone", "")
        billed_state = data.get("billed_to_state_code", "")
        extra_party_info = []
        if billed_phone:
            extra_party_info.append(f"Ph: {billed_phone}")
        if billed_gstin:
            extra_party_info.append(f"GSTIN: {billed_gstin}")
        if billed_state:
            extra_party_info.append(f"State: {billed_state}")
        if extra_party_info:
            c.drawString(x_left + 8, curr_y, " | ".join(extra_party_info))

        # Right Party: Shipped To
        c.setFont("Helvetica-Bold", 9.0)
        c.drawString(x_mid + 8, y_h2 - 14, "Shipped To:")

        shipped_name = data.get("shipped_to_name") or billed_name
        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(x_mid + 8, y_h2 - 27, shipped_name[:45])

        c.setFont("Helvetica", 8.0)
        shipped_addr = data.get("shipped_to_address") or billed_addr
        shipped_lines = simpleSplit(shipped_addr, "Helvetica", 8.0, x_right - x_mid - 16)
        curr_y = y_h2 - 39
        for line in shipped_lines[:2]:
            c.drawString(x_mid + 8, curr_y, line)
            curr_y -= 11

        shipped_gstin = data.get("shipped_to_gstin") or billed_gstin
        shipped_phone = data.get("shipped_to_phone") or billed_phone
        shipped_state = data.get("shipped_to_state_code") or billed_state
        extra_ship_info = []
        if shipped_phone:
            extra_ship_info.append(f"Ph: {shipped_phone}")
        if shipped_gstin:
            extra_ship_info.append(f"GSTIN: {shipped_gstin}")
        if shipped_state:
            extra_ship_info.append(f"State: {shipped_state}")
        if extra_ship_info:
            c.drawString(x_mid + 8, curr_y, " | ".join(extra_ship_info))

        # Horizontal Line 3: Party to Table Header
        c.line(x_left, y_h3, x_right, y_h3)

        # 5. Table Layout Setup
        # Column X coordinates
        x_col0 = x_left          # 22.0
        x_col1 = x_col0 + 32.0   # 54.0   (S.NO)
        x_col2 = x_col1 + 203.0  # 257.0  (Description)
        x_col3 = x_col2 + 54.0   # 311.0  (HSN)
        x_col4 = x_col3 + 45.0   # 356.0  (QTY)
        x_col5 = x_col4 + 105.0  # 461.0  (RATE: Rs / P)
        x_rate_split = x_col4 + 75.0  # 431.0
        x_col6 = x_right         # 573.0  (AMOUNT: Rs / P)
        x_amt_split = x_col5 + 78.0   # 539.0

        y_th_top = y_h3          # 592.0
        y_th_bottom = y_th_top - 32.0  # 560.0
        y_totals_top = 188.0     # Top of Totals Box
        y_totals_bottom = 98.0   # Bottom of Totals Box / start of footer

        # Draw Table Header Texts
        c.setFont("Helvetica-Bold", 8.5)
        c.drawCentredString((x_col0 + x_col1) / 2.0, y_th_top - 18, "S.NO")
        c.drawString(x_col1 + 6, y_th_top - 18, "Description of Goods")
        
        c.drawCentredString((x_col2 + x_col3) / 2.0, y_th_top - 13, "HSN")
        c.drawCentredString((x_col2 + x_col3) / 2.0, y_th_top - 24, "CODE")

        c.drawCentredString((x_col3 + x_col4) / 2.0, y_th_top - 18, "QTY.")

        # RATE Header with subcolumns
        c.drawCentredString((x_col4 + x_col5) / 2.0, y_th_top - 12, "RATE")
        c.line(x_col4, y_th_top - 17, x_col5, y_th_top - 17)
        c.setFont("Helvetica", 7.5)
        c.drawString(x_col4 + 8, y_th_top - 27, "Rs.")
        c.drawString(x_rate_split + 10, y_th_top - 27, "P")

        # AMOUNT Header with subcolumns
        c.setFont("Helvetica-Bold", 8.5)
        c.drawCentredString((x_col5 + x_col6) / 2.0, y_th_top - 12, "AMOUNT")
        c.line(x_col5, y_th_top - 17, x_col6, y_th_top - 17)
        c.setFont("Helvetica", 7.5)
        c.drawString(x_col5 + 8, y_th_top - 27, "Rs.")
        c.drawString(x_amt_split + 10, y_th_top - 27, "P")

        # Horizontal line below table header
        c.line(x_left, y_th_bottom, x_right, y_th_bottom)

        # Draw Table Vertical Column Lines:
        # 1. S.NO, Description, HSN, QTY stop at y_totals_top (leaving RUPEES area open)
        for col_x in [x_col1, x_col2, x_col3]:
            c.line(col_x, y_th_top, col_x, y_totals_top)

        # 2. x_col4 (separates items & RUPEES from Totals), x_col5, x_col6 go down to y_totals_bottom
        c.line(x_col4, y_th_top, x_col4, y_totals_bottom)
        c.line(x_col5, y_th_top, x_col5, y_totals_bottom)
        
        # 3. Rate split stops at y_totals_top (only exists in items body)
        c.line(x_rate_split, y_th_top - 17, x_rate_split, y_totals_top)
        
        # 4. Amount split goes down all the way through totals
        c.line(x_amt_split, y_th_top - 17, x_amt_split, y_totals_bottom)

        # 6. Draw Line Items
        items: List[Dict[str, Any]] = data.get("items", [])
        row_y = y_th_bottom - 15.0

        for idx, item in enumerate(items, start=1):
            if row_y < y_totals_top + 15:
                break

            s_no = str(item.get("s_no", idx))
            desc = str(item.get("description", ""))
            hsn = str(item.get("hsn_code", ""))
            qty = item.get("quantity", 1)
            rate = item.get("rate", 0)
            amount = item.get("amount", 0)

            # Format numbers
            qty_str = f"{qty:g}" if isinstance(qty, (int, float)) else str(qty)
            rate_rs, rate_p = split_rs_paise(rate)
            amt_rs, amt_p = split_rs_paise(amount)

            c.setFont("Helvetica", 8.5)
            c.drawCentredString((x_col0 + x_col1) / 2.0, row_y, s_no)

            # Multi-line item description wrapping
            desc_lines = simpleSplit(desc, "Helvetica", 8.5, x_col2 - x_col1 - 10)
            c.drawString(x_col1 + 5, row_y, desc_lines[0] if desc_lines else "")
            
            c.drawCentredString((x_col2 + x_col3) / 2.0, row_y, hsn)
            c.drawCentredString((x_col3 + x_col4) / 2.0, row_y, qty_str)

            # Right align Rate and Amount
            c.drawRightString(x_rate_split - 4, row_y, rate_rs)
            c.drawCentredString((x_rate_split + x_col5) / 2.0, row_y, rate_p)

            c.drawRightString(x_amt_split - 4, row_y, amt_rs)
            c.drawCentredString((x_amt_split + x_col6) / 2.0, row_y, amt_p)

            # If description has second line
            extra_lines = len(desc_lines) - 1
            if extra_lines > 0:
                for line in desc_lines[1:3]:
                    row_y -= 11.0
                    c.drawString(x_col1 + 5, row_y, line)

            row_y -= 16.0

        # 7. Totals Section
        # Horizontal lines for totals
        tot_y_lines = [188.0, 173.0, 158.0, 143.0, 128.0, 113.0, 98.0]
        
        # Line at 188 separates items table from totals across full width
        c.line(x_left, 188.0, x_right, 188.0)

        # Intermediate totals horizontal lines span from x_col4 to x_right
        for y_l in tot_y_lines[1:-1]:
            c.line(x_col4, y_l, x_right, y_l)

        # Line at 98 closes the bottom of the table across full width
        c.line(x_left, 98.0, x_right, 98.0)

        # RUPEES in Words (Clean left box spanning x_left to x_col4)
        grand_total = data.get("grand_total", 0.0)
        in_words = data.get("total_in_words") or amount_to_words(grand_total)

        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(x_left + 8, 173.0, "RUPEES:")

        c.setFont("Helvetica-Oblique", 8.0)
        word_lines = simpleSplit(in_words, "Helvetica-Oblique", 8.0, x_col4 - x_left - 16)
        w_y = 158.0
        for w_line in word_lines[:5]:
            c.drawString(x_left + 8, w_y, w_line)
            w_y -= 11.0

        # Right-side Totals Rows
        subtotal = data.get("subtotal", 0.0)
        cgst_rate = data.get("cgst_rate", 0.0)
        cgst_amount = data.get("cgst_amount", 0.0)
        sgst_rate = data.get("sgst_rate", 0.0)
        sgst_amount = data.get("sgst_amount", 0.0)
        igst_rate = data.get("igst_rate", 0.0)
        igst_amount = data.get("igst_amount", 0.0)
        total_tax = data.get("total_tax", 0.0)

        # Row 1: TOTAL (Subtotal)
        c.setFont("Helvetica", 8.0)
        c.drawString(x_col4 + 6, 177.0, "TOTAL")
        sub_rs, sub_p = split_rs_paise(subtotal)
        c.drawRightString(x_amt_split - 4, 177.0, sub_rs)
        c.drawCentredString((x_amt_split + x_col6) / 2.0, 177.0, sub_p)

        # Row 2: CGST
        c.drawString(x_col4 + 6, 162.0, "CGST.")
        if cgst_rate > 0:
            c.drawRightString(x_col5 - 6, 162.0, f"{cgst_rate:g}%")
            cgst_rs, cgst_p = split_rs_paise(cgst_amount)
            c.drawRightString(x_amt_split - 4, 162.0, cgst_rs)
            c.drawCentredString((x_amt_split + x_col6) / 2.0, 162.0, cgst_p)
        else:
            c.drawCentredString((x_amt_split + x_col6) / 2.0, 162.0, "-")

        # Row 3: SGST
        c.drawString(x_col4 + 6, 147.0, "SGST.")
        if sgst_rate > 0:
            c.drawRightString(x_col5 - 6, 147.0, f"{sgst_rate:g}%")
            sgst_rs, sgst_p = split_rs_paise(sgst_amount)
            c.drawRightString(x_amt_split - 4, 147.0, sgst_rs)
            c.drawCentredString((x_amt_split + x_col6) / 2.0, 147.0, sgst_p)
        else:
            c.drawCentredString((x_amt_split + x_col6) / 2.0, 147.0, "-")

        # Row 4: IGST
        c.drawString(x_col4 + 6, 132.0, "IGST.")
        if igst_rate > 0 and igst_amount > 0:
            c.drawRightString(x_col5 - 6, 132.0, f"{igst_rate:g}%")
            igst_rs, igst_p = split_rs_paise(igst_amount)
            c.drawRightString(x_amt_split - 4, 132.0, igst_rs)
            c.drawCentredString((x_amt_split + x_col6) / 2.0, 132.0, igst_p)
        else:
            c.drawRightString(x_amt_split - 10, 132.0, "-")
            c.drawCentredString((x_amt_split + x_col6) / 2.0, 132.0, "-")

        # Row 5: TOTAL TAX
        c.drawString(x_col4 + 6, 117.0, "TOTAL TAX")
        tax_rs, tax_p = split_rs_paise(total_tax)
        c.drawRightString(x_amt_split - 4, 117.0, tax_rs)
        c.drawCentredString((x_amt_split + x_col6) / 2.0, 117.0, tax_p)

        # Row 6: INVOICE TOTAL
        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(x_col4 + 6, 102.0, "INVOICE TOTAL")
        gt_rs, gt_p = split_rs_paise(grand_total)
        c.drawRightString(x_amt_split - 4, 102.0, gt_rs)
        c.drawCentredString((x_amt_split + x_col6) / 2.0, 102.0, gt_p)

        # 8. Footer (Signatures & Declaration)
        declaration = data.get("declaration", "Certified that the above particulars are true & correct")
        c.setFont("Helvetica", 7.5)
        c.drawRightString(x_right - 10, 85.0, declaration)

        c.setFont("Helvetica-Bold", 8.0)
        c.drawRightString(x_right - 10, 72.0, f"For {company_name}")

        c.setFont("Helvetica", 8.5)
        c.drawString(x_left + 35, 34.0, "Receiver’s Signature")
        c.drawRightString(x_right - 35, 34.0, "Authorized Signatory")
