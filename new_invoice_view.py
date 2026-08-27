"""
New Invoice View: Rich structured form with dynamic line items and live PDF preview.
"""
import customtkinter as ctk
from tkinter import filedialog, messagebox
from typing import Dict, Any, List, Optional
from datetime import datetime
from PIL import Image

from src.utils.calculations import calculate_invoice_totals, format_indian_currency
from src.utils.number_to_words import amount_to_words
from src.utils.validators import validate_invoice_payload
from src.services.pdf_generator import PDFGenerator
from src.services.docx_generator import DocxGenerator
from src.services.preview_service import PreviewService
from src.services.print_service import PrintService
from src.gui.components.modal_dialog import CustomerDialog, ProductDialog, ConfirmDialog
from src.config import (
    COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_SUCCESS,
    COLOR_WARNING, COLOR_DANGER, COLOR_SECONDARY, COLOR_INFO,
    CARD_DARK, CARD_LIGHT, COPY_TYPES, PAYMENT_STATUSES,
    PAYMENT_METHODS
)


class ItemRowFrame(ctk.CTkFrame):
    """Single line item row in the invoice editor."""
    def __init__(self, master, index: int, on_change: callable, on_delete: callable, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.index = index
        self.on_change = on_change
        self.on_delete = on_delete

        self.grid_columnconfigure(1, weight=3)  # Description gets more width
        self.grid_columnconfigure((0, 2, 3, 4, 5, 6), weight=1)

        # 0. S.No
        self.lbl_sno = ctk.CTkLabel(self, text=str(index), width=28, font=ctk.CTkFont(size=12, weight="bold"))
        self.lbl_sno.grid(row=0, column=0, padx=2, pady=2)

        # 1. Description
        self.entry_desc = ctk.CTkEntry(self, placeholder_text="Item / Description of Goods", height=32, corner_radius=6)
        self.entry_desc.grid(row=0, column=1, padx=2, pady=2, sticky="ew")
        self.entry_desc.bind("<KeyRelease>", self._on_field_change)

        # 2. HSN
        self.entry_hsn = ctk.CTkEntry(self, placeholder_text="HSN", width=65, height=32, corner_radius=6)
        self.entry_hsn.grid(row=0, column=2, padx=2, pady=2)
        self.entry_hsn.bind("<KeyRelease>", self._on_field_change)

        # 3. Qty
        self.entry_qty = ctk.CTkEntry(self, placeholder_text="Qty", width=55, height=32, corner_radius=6)
        self.entry_qty.insert(0, "1")
        self.entry_qty.grid(row=0, column=3, padx=2, pady=2)
        self.entry_qty.bind("<KeyRelease>", self._on_field_change)

        # 4. Unit
        self.entry_unit = ctk.CTkEntry(self, placeholder_text="NOS", width=50, height=32, corner_radius=6)
        self.entry_unit.insert(0, "NOS")
        self.entry_unit.grid(row=0, column=4, padx=2, pady=2)

        # 5. Rate (Rs.)
        self.entry_rate = ctk.CTkEntry(self, placeholder_text="Rate (₹)", width=75, height=32, corner_radius=6)
        self.entry_rate.insert(0, "0")
        self.entry_rate.grid(row=0, column=5, padx=2, pady=2)
        self.entry_rate.bind("<KeyRelease>", self._on_field_change)

        # 6. Amount (Read-only)
        self.lbl_amount = ctk.CTkLabel(self, text="₹ 0.00", width=80, font=ctk.CTkFont(size=12, weight="bold"), anchor="e")
        self.lbl_amount.grid(row=0, column=6, padx=4, pady=2, sticky="e")

        # 7. Delete Button
        self.btn_del = ctk.CTkButton(
            self,
            text="✕",
            width=28,
            height=28,
            fg_color=("gray85", "#334155"),
            text_color=COLOR_DANGER,
            hover_color=("gray75", "#475569"),
            command=lambda: self.on_delete(self)
        )
        self.btn_del.grid(row=0, column=7, padx=(2, 0), pady=2)

    def _on_field_change(self, event=None):
        self.calculate_amount()
        if self.on_change:
            self.on_change()

    def calculate_amount(self) -> float:
        try:
            qty = float(self.entry_qty.get() or 0)
            rate = float(self.entry_rate.get() or 0)
            amt = round(qty * rate, 2)
            self.lbl_amount.configure(text=f"₹ {amt:,.2f}")
            return amt
        except ValueError:
            self.lbl_amount.configure(text="₹ 0.00")
            return 0.0

    def get_data(self) -> Dict[str, Any]:
        qty = float(self.entry_qty.get() or 0) if self.entry_qty.get() else 0.0
        rate = float(self.entry_rate.get() or 0) if self.entry_rate.get() else 0.0
        return {
            "s_no": self.index,
            "description": self.entry_desc.get().strip(),
            "hsn_code": self.entry_hsn.get().strip(),
            "quantity": qty,
            "unit": self.entry_unit.get().strip() or "NOS",
            "rate": rate,
            "amount": round(qty * rate, 2)
        }

    def set_data(self, data: Dict[str, Any]):
        self.entry_desc.delete(0, "end")
        self.entry_desc.insert(0, data.get("description", ""))
        self.entry_hsn.delete(0, "end")
        self.entry_hsn.insert(0, data.get("hsn_code", ""))
        self.entry_qty.delete(0, "end")
        self.entry_qty.insert(0, str(data.get("quantity", 1)))
        self.entry_unit.delete(0, "end")
        self.entry_unit.insert(0, data.get("unit", "NOS"))
        self.entry_rate.delete(0, "end")
        self.entry_rate.insert(0, str(data.get("rate", 0)))
        self.calculate_amount()


class NewInvoiceView(ctk.CTkFrame):
    def __init__(self, master, app_controller, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.app = app_controller
        self.pdf_generator = PDFGenerator()
        self.docx_generator = DocxGenerator()
        self.item_rows: List[ItemRowFrame] = []
        self.current_invoice_id: Optional[int] = None
        self.generated_pdf_path: Optional[str] = None
        self.cached_preview_image: Optional[Image.Image] = None

        # Two Main Panes: Left (Form), Right (Live Preview)
        self.grid_columnconfigure(0, weight=6)  # Form
        self.grid_columnconfigure(1, weight=5)  # Preview
        self.grid_rowconfigure(0, weight=1)

        self._build_left_form_pane()
        self._build_right_preview_pane()

    def _build_left_form_pane(self):
        self.form_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.form_scroll.grid(row=0, column=0, sticky="nsew", padx=(16, 8), pady=16)

        # 1. Title & Action Bar
        top_bar = ctk.CTkFrame(self.form_scroll, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 12))

        self.view_title = ctk.CTkLabel(
            top_bar,
            text="Create New Tax Invoice",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold")
        )
        self.view_title.pack(side="left")

        # Action Buttons on Top Bar
        ctk.CTkButton(
            top_bar,
            text="Reset Form",
            width=85,
            height=32,
            fg_color=("gray80", "#334155"),
            text_color=("black", "white"),
            hover_color=("gray70", "#475569"),
            command=self.reset_form
        ).pack(side="right", padx=(6, 0))

        ctk.CTkButton(
            top_bar,
            text="👁 Live Preview",
            width=100,
            height=32,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            command=self.render_live_preview
        ).pack(side="right")

        # 2. Card: Invoice Metadata
        meta_card = ctk.CTkFrame(self.form_scroll, corner_radius=10, fg_color=(CARD_LIGHT, CARD_DARK), border_width=1, border_color=("gray85", "#334155"))
        meta_card.pack(fill="x", pady=(0, 12), padx=2)

        ctk.CTkLabel(meta_card, text="1. Invoice & Transport Details", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=14, pady=(10, 6))

        grid1 = ctk.CTkFrame(meta_card, fg_color="transparent")
        grid1.pack(fill="x", padx=14, pady=(0, 12))
        grid1.grid_columnconfigure((0, 1, 2), weight=1)

        # Row 0
        ctk.CTkLabel(grid1, text="Invoice Number *", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=0, sticky="w", padx=4, pady=2)
        ctk.CTkLabel(grid1, text="Invoice Date (DD/MM/YYYY) *", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=1, sticky="w", padx=4, pady=2)
        ctk.CTkLabel(grid1, text="Copy Type", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=2, sticky="w", padx=4, pady=2)

        self.entry_inv_no = ctk.CTkEntry(grid1, height=34, corner_radius=6)
        self.entry_inv_no.grid(row=1, column=0, sticky="ew", padx=4, pady=(0, 8))

        self.entry_inv_date = ctk.CTkEntry(grid1, height=34, corner_radius=6)
        self.entry_inv_date.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.entry_inv_date.grid(row=1, column=1, sticky="ew", padx=4, pady=(0, 8))

        self.copy_type_var = ctk.StringVar(value="Original Copy")
        self.menu_copy_type = ctk.CTkOptionMenu(grid1, values=COPY_TYPES, variable=self.copy_type_var, height=34, corner_radius=6)
        self.menu_copy_type.grid(row=1, column=2, sticky="ew", padx=4, pady=(0, 8))

        # Row 1
        ctk.CTkLabel(grid1, text="P.O. Number", font=ctk.CTkFont(size=11, weight="bold")).grid(row=2, column=0, sticky="w", padx=4, pady=2)
        ctk.CTkLabel(grid1, text="P.O. Date", font=ctk.CTkFont(size=11, weight="bold")).grid(row=2, column=1, sticky="w", padx=4, pady=2)
        ctk.CTkLabel(grid1, text="Vehicle Number", font=ctk.CTkFont(size=11, weight="bold")).grid(row=2, column=2, sticky="w", padx=4, pady=2)

        self.entry_po_no = ctk.CTkEntry(grid1, placeholder_text="e.g. PO-8874", height=34, corner_radius=6)
        self.entry_po_no.grid(row=3, column=0, sticky="ew", padx=4)

        self.entry_po_date = ctk.CTkEntry(grid1, placeholder_text="DD/MM/YYYY", height=34, corner_radius=6)
        self.entry_po_date.grid(row=3, column=1, sticky="ew", padx=4)

        self.entry_vehicle_no = ctk.CTkEntry(grid1, placeholder_text="e.g. TN 38 AB 1234", height=34, corner_radius=6)
        self.entry_vehicle_no.grid(row=3, column=2, sticky="ew", padx=4)

        # 3. Card: Customer & Party Details
        cust_card = ctk.CTkFrame(self.form_scroll, corner_radius=10, fg_color=(CARD_LIGHT, CARD_DARK), border_width=1, border_color=("gray85", "#334155"))
        cust_card.pack(fill="x", pady=(0, 12), padx=2)

        cust_hdr = ctk.CTkFrame(cust_card, fg_color="transparent")
        cust_hdr.pack(fill="x", padx=14, pady=(10, 6))

        ctk.CTkLabel(cust_hdr, text="2. Customer & Billing Details", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left")

        ctk.CTkButton(
            cust_hdr,
            text="+ Add New Customer",
            font=ctk.CTkFont(size=11),
            width=130,
            height=28,
            fg_color=("gray85", "#334155"),
            text_color=("black", "white"),
            hover_color=COLOR_PRIMARY,
            command=self._quick_add_customer
        ).pack(side="right")

        # Customer Dropdown Selector
        sel_row = ctk.CTkFrame(cust_card, fg_color="transparent")
        sel_row.pack(fill="x", padx=14, pady=(0, 8))

        ctk.CTkLabel(sel_row, text="Select Saved Customer:", font=ctk.CTkFont(size=11)).pack(side="left", padx=(0, 8))
        self.customer_var = ctk.StringVar(value="-- Select Existing Customer --")
        self.customer_dropdown = ctk.CTkOptionMenu(
            sel_row,
            values=["-- Select Existing Customer --"],
            variable=self.customer_var,
            command=self._on_customer_selected,
            height=32,
            corner_radius=6
        )
        self.customer_dropdown.pack(side="left", fill="x", expand=True)

        # Customer details grid
        grid2 = ctk.CTkFrame(cust_card, fg_color="transparent")
        grid2.pack(fill="x", padx=14, pady=(0, 12))
        grid2.grid_columnconfigure((0, 1), weight=1)

        # Billed To
        ctk.CTkLabel(grid2, text="Billed To (Customer Name) *", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=0, sticky="w", padx=4, pady=2)
        ctk.CTkLabel(grid2, text="Billed Address", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=1, sticky="w", padx=4, pady=2)

        self.entry_billed_name = ctk.CTkEntry(grid2, placeholder_text="Customer / Company Name", height=34, corner_radius=6)
        self.entry_billed_name.grid(row=1, column=0, sticky="ew", padx=4, pady=(0, 6))

        self.txt_billed_addr = ctk.CTkTextbox(grid2, height=55, corner_radius=6)
        self.txt_billed_addr.grid(row=1, column=1, rowspan=3, sticky="nsew", padx=4, pady=(0, 6))

        ctk.CTkLabel(grid2, text="Phone Number", font=ctk.CTkFont(size=11, weight="bold")).grid(row=2, column=0, sticky="w", padx=4, pady=2)
        self.entry_billed_phone = ctk.CTkEntry(grid2, placeholder_text="Phone", height=34, corner_radius=6)
        self.entry_billed_phone.grid(row=3, column=0, sticky="ew", padx=4, pady=(0, 6))

        ctk.CTkLabel(grid2, text="GSTIN", font=ctk.CTkFont(size=11, weight="bold")).grid(row=4, column=0, sticky="w", padx=4, pady=2)
        ctk.CTkLabel(grid2, text="State Code (e.g. 33)", font=ctk.CTkFont(size=11, weight="bold")).grid(row=4, column=1, sticky="w", padx=4, pady=2)

        self.entry_billed_gstin = ctk.CTkEntry(grid2, placeholder_text="GSTIN Number", height=34, corner_radius=6)
        self.entry_billed_gstin.grid(row=5, column=0, sticky="ew", padx=4)

        self.entry_billed_state = ctk.CTkEntry(grid2, placeholder_text="33", height=34, corner_radius=6)
        self.entry_billed_state.grid(row=5, column=1, sticky="ew", padx=4)

        # Checkbox for Shipped To
        self.same_as_billed_var = ctk.BooleanVar(value=True)
        self.chk_same = ctk.CTkCheckBox(
            cust_card,
            text="Shipped To is same as Billed To",
            variable=self.same_as_billed_var,
            command=self._toggle_shipped_to
        )
        self.chk_same.pack(anchor="w", padx=18, pady=(4, 10))

        # Shipped To Frame (collapsible)
        self.shipped_frame = ctk.CTkFrame(cust_card, fg_color="transparent")
        self.shipped_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(self.shipped_frame, text="Shipped To Name", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=0, sticky="w", padx=4, pady=2)
        ctk.CTkLabel(self.shipped_frame, text="Shipping Address", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=1, sticky="w", padx=4, pady=2)

        self.entry_shipped_name = ctk.CTkEntry(self.shipped_frame, height=34, corner_radius=6)
        self.entry_shipped_name.grid(row=1, column=0, sticky="ew", padx=4, pady=(0, 6))

        self.txt_shipped_addr = ctk.CTkTextbox(self.shipped_frame, height=55, corner_radius=6)
        self.txt_shipped_addr.grid(row=1, column=1, rowspan=3, sticky="nsew", padx=4, pady=(0, 6))

        ctk.CTkLabel(self.shipped_frame, text="Shipped Phone", font=ctk.CTkFont(size=11, weight="bold")).grid(row=2, column=0, sticky="w", padx=4, pady=2)
        self.entry_shipped_phone = ctk.CTkEntry(self.shipped_frame, height=34, corner_radius=6)
        self.entry_shipped_phone.grid(row=3, column=0, sticky="ew", padx=4, pady=(0, 6))

        # 4. Card: Line Items Table
        items_card = ctk.CTkFrame(self.form_scroll, corner_radius=10, fg_color=(CARD_LIGHT, CARD_DARK), border_width=1, border_color=("gray85", "#334155"))
        items_card.pack(fill="x", pady=(0, 12), padx=2)

        items_hdr = ctk.CTkFrame(items_card, fg_color="transparent")
        items_hdr.pack(fill="x", padx=14, pady=(10, 6))

        ctk.CTkLabel(items_hdr, text="3. Items & Services Table", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left")

        # Quick Add from catalog button & dropdown
        self.product_var = ctk.StringVar(value="+ Quick Insert Product")
        self.product_dropdown = ctk.CTkOptionMenu(
            items_hdr,
            values=["+ Quick Insert Product"],
            variable=self.product_var,
            command=self._on_product_insert_selected,
            height=28,
            corner_radius=6
        )
        self.product_dropdown.pack(side="right", padx=(8, 0))

        ctk.CTkButton(
            items_hdr,
            text="+ Add Row",
            font=ctk.CTkFont(size=11),
            width=80,
            height=28,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            command=self.add_item_row
        ).pack(side="right")

        # Items Table Headers
        tbl_th = ctk.CTkFrame(items_card, fg_color=("gray90", "#0F172A"), height=30, corner_radius=6)
        tbl_th.pack(fill="x", padx=14, pady=(0, 4))
        tbl_th.grid_columnconfigure(1, weight=3)
        tbl_th.grid_columnconfigure((0, 2, 3, 4, 5, 6), weight=1)

        ctk.CTkLabel(tbl_th, text="#", width=28, font=ctk.CTkFont(size=10, weight="bold")).grid(row=0, column=0, padx=2)
        ctk.CTkLabel(tbl_th, text="Description of Goods", font=ctk.CTkFont(size=10, weight="bold"), anchor="w").grid(row=0, column=1, padx=2, sticky="w")
        ctk.CTkLabel(tbl_th, text="HSN", width=65, font=ctk.CTkFont(size=10, weight="bold")).grid(row=0, column=2, padx=2)
        ctk.CTkLabel(tbl_th, text="Qty", width=55, font=ctk.CTkFont(size=10, weight="bold")).grid(row=0, column=3, padx=2)
        ctk.CTkLabel(tbl_th, text="Unit", width=50, font=ctk.CTkFont(size=10, weight="bold")).grid(row=0, column=4, padx=2)
        ctk.CTkLabel(tbl_th, text="Rate (₹)", width=75, font=ctk.CTkFont(size=10, weight="bold")).grid(row=0, column=5, padx=2)
        ctk.CTkLabel(tbl_th, text="Amount (₹)", width=80, font=ctk.CTkFont(size=10, weight="bold"), anchor="e").grid(row=0, column=6, padx=4, sticky="e")
        ctk.CTkLabel(tbl_th, text="", width=28).grid(row=0, column=7, padx=(2, 0))

        # Dynamic Item Rows Container
        self.rows_container = ctk.CTkFrame(items_card, fg_color="transparent")
        self.rows_container.pack(fill="x", padx=14, pady=(0, 8))

        # 5. Card: Tax & Totals Breakdown
        totals_card = ctk.CTkFrame(self.form_scroll, corner_radius=10, fg_color=(CARD_LIGHT, CARD_DARK), border_width=1, border_color=("gray85", "#334155"))
        totals_card.pack(fill="x", pady=(0, 12), padx=2)

        tot_grid = ctk.CTkFrame(totals_card, fg_color="transparent")
        tot_grid.pack(fill="x", padx=14, pady=12)
        tot_grid.grid_columnconfigure((0, 1), weight=1)

        # Left Column: Tax Type Selector & Payment Info
        left_tax = ctk.CTkFrame(tot_grid, fg_color="transparent")
        left_tax.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        ctk.CTkLabel(left_tax, text="GST Tax Type", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(0, 4))
        self.tax_type_var = ctk.StringVar(value="Intra-State (CGST 9% + SGST 9%)")
        self.rad_intra = ctk.CTkRadioButton(
            left_tax,
            text="Intra-State (CGST + SGST)",
            variable=self.tax_type_var,
            value="intra",
            command=self._on_tax_change
        )
        self.rad_intra.pack(anchor="w", pady=2)

        self.rad_inter = ctk.CTkRadioButton(
            left_tax,
            text="Inter-State (IGST 18%)",
            variable=self.tax_type_var,
            value="inter",
            command=self._on_tax_change
        )
        self.rad_inter.pack(anchor="w", pady=2)
        self.tax_type_var.set("intra")

        ctk.CTkLabel(left_tax, text="Payment Status", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(10, 2))
        self.status_var = ctk.StringVar(value="Unpaid")
        self.status_menu = ctk.CTkOptionMenu(left_tax, values=PAYMENT_STATUSES, variable=self.status_var, height=32, corner_radius=6)
        self.status_menu.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(left_tax, text="Payment Method", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(4, 2))
        self.method_var = ctk.StringVar(value="Bank Transfer / NEFT / RTGS")
        self.method_menu = ctk.CTkOptionMenu(left_tax, values=PAYMENT_METHODS, variable=self.method_var, height=32, corner_radius=6)
        self.method_menu.pack(fill="x")

        # Right Column: Totals Summary
        right_tot = ctk.CTkFrame(tot_grid, fg_color=("gray95", "#0F172A"), corner_radius=8, border_width=1, border_color=("gray85", "#334155"))
        right_tot.grid(row=0, column=1, sticky="nsew")

        r_grid = ctk.CTkFrame(right_tot, fg_color="transparent")
        r_grid.pack(fill="x", padx=12, pady=10)
        r_grid.grid_columnconfigure(0, weight=1)
        r_grid.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(r_grid, text="Subtotal:").grid(row=0, column=0, sticky="w", pady=2)
        self.lbl_subtotal = ctk.CTkLabel(r_grid, text="₹ 0.00", font=ctk.CTkFont(weight="bold"))
        self.lbl_subtotal.grid(row=0, column=1, sticky="e", pady=2)

        self.lbl_cgst_title = ctk.CTkLabel(r_grid, text="CGST (9%):")
        self.lbl_cgst_title.grid(row=1, column=0, sticky="w", pady=2)
        self.lbl_cgst_val = ctk.CTkLabel(r_grid, text="₹ 0.00")
        self.lbl_cgst_val.grid(row=1, column=1, sticky="e", pady=2)

        self.lbl_sgst_title = ctk.CTkLabel(r_grid, text="SGST (9%):")
        self.lbl_sgst_title.grid(row=2, column=0, sticky="w", pady=2)
        self.lbl_sgst_val = ctk.CTkLabel(r_grid, text="₹ 0.00")
        self.lbl_sgst_val.grid(row=2, column=1, sticky="e", pady=2)

        self.lbl_igst_title = ctk.CTkLabel(r_grid, text="IGST (18%):")
        self.lbl_igst_title.grid(row=3, column=0, sticky="w", pady=2)
        self.lbl_igst_val = ctk.CTkLabel(r_grid, text="-")
        self.lbl_igst_val.grid(row=3, column=1, sticky="e", pady=2)

        ctk.CTkLabel(r_grid, text="Total Tax:").grid(row=4, column=0, sticky="w", pady=2)
        self.lbl_tot_tax = ctk.CTkLabel(r_grid, text="₹ 0.00", font=ctk.CTkFont(weight="bold"))
        self.lbl_tot_tax.grid(row=4, column=1, sticky="e", pady=2)

        # Divider
        ctk.CTkFrame(r_grid, height=1, fg_color="gray70").grid(row=5, column=0, columnspan=2, sticky="ew", pady=4)

        ctk.CTkLabel(r_grid, text="INVOICE TOTAL:", font=ctk.CTkFont(size=13, weight="bold")).grid(row=6, column=0, sticky="w", pady=2)
        self.lbl_grand_total = ctk.CTkLabel(r_grid, text="₹ 0.00", font=ctk.CTkFont(size=14, weight="bold"), text_color=COLOR_PRIMARY)
        self.lbl_grand_total.grid(row=6, column=1, sticky="e", pady=2)

        self.lbl_in_words = ctk.CTkLabel(
            right_tot,
            text="Rupees Zero Only",
            font=ctk.CTkFont(size=10, slant="italic"),
            text_color=("gray45", "#94A3B8"),
            wraplength=220,
            justify="right"
        )
        self.lbl_in_words.pack(fill="x", padx=12, pady=(0, 8), anchor="e")

        # 6. Bottom Master Action Bar
        action_bar = ctk.CTkFrame(self.form_scroll, fg_color="transparent")
        action_bar.pack(fill="x", pady=(8, 20))

        ctk.CTkButton(
            action_bar,
            text="💾 Save Draft",
            width=110,
            height=38,
            fg_color=("gray80", "#334155"),
            text_color=("black", "white"),
            hover_color=("gray70", "#475569"),
            command=self.save_draft
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            action_bar,
            text="⚡ Confirm & Generate Invoice",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=38,
            fg_color=COLOR_SUCCESS,
            hover_color="#059669",
            command=self.confirm_and_generate
        ).pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(
            action_bar,
            text="📄 Export Word",
            width=110,
            height=38,
            fg_color=COLOR_INFO,
            hover_color="#4F46E5",
            command=self.export_word
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            action_bar,
            text="🖨 Print",
            width=80,
            height=38,
            fg_color=COLOR_SECONDARY,
            hover_color=COLOR_PRIMARY_HOVER,
            command=self.print_invoice
        ).pack(side="left")

    def _build_right_preview_pane(self):
        self.preview_frame = ctk.CTkFrame(
            self,
            corner_radius=12,
            fg_color=(CARD_LIGHT, CARD_DARK),
            border_width=1,
            border_color=("gray85", "#334155")
        )
        self.preview_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 16), pady=16)

        # Header bar of preview
        prev_hdr = ctk.CTkFrame(self.preview_frame, fg_color="transparent")
        prev_hdr.pack(fill="x", padx=16, pady=(12, 8))

        ctk.CTkLabel(
            prev_hdr,
            text="Live Invoice PDF Preview",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        ).pack(side="left")

        ctk.CTkButton(
            prev_hdr,
            text="Open PDF ↗",
            width=90,
            height=28,
            font=ctk.CTkFont(size=11),
            fg_color=("gray85", "#334155"),
            text_color=("black", "white"),
            hover_color=COLOR_PRIMARY,
            command=self._open_current_pdf
        ).pack(side="right")

        # Scrollable image canvas
        self.preview_scroll = ctk.CTkScrollableFrame(self.preview_frame, fg_color=("gray95", "#0B1120"), corner_radius=8)
        self.preview_scroll.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.preview_image_label = ctk.CTkLabel(self.preview_scroll, text="Click 'Live Preview' or enter invoice data to view render.")
        self.preview_image_label.pack(expand=True, pady=40)

    def _toggle_shipped_to(self):
        if self.same_as_billed_var.get():
            self.shipped_frame.pack_forget()
        else:
            self.shipped_frame.pack(fill="x", padx=14, pady=(0, 10))

    def _on_tax_change(self):
        is_inter = (self.tax_type_var.get() == "inter")
        if is_inter:
            self.lbl_cgst_title.configure(text="CGST (0%):")
            self.lbl_cgst_val.configure(text="-")
            self.lbl_sgst_title.configure(text="SGST (0%):")
            self.lbl_sgst_val.configure(text="-")
            self.lbl_igst_title.configure(text="IGST (18%):")
        else:
            self.lbl_cgst_title.configure(text="CGST (9%):")
            self.lbl_sgst_title.configure(text="SGST (9%):")
            self.lbl_igst_title.configure(text="IGST (0%):")
            self.lbl_igst_val.configure(text="-")
        self.recalculate_totals()

    def add_item_row(self, data: Optional[Dict[str, Any]] = None):
        """Append a new item row to the table."""
        idx = len(self.item_rows) + 1
        row = ItemRowFrame(
            self.rows_container,
            index=idx,
            on_change=self.recalculate_totals,
            on_delete=self._remove_item_row
        )
        row.pack(fill="x", pady=2)
        if data:
            row.set_data(data)
        self.item_rows.append(row)
        self.recalculate_totals()

    def _remove_item_row(self, row_to_remove: ItemRowFrame):
        if len(self.item_rows) <= 1:
            # Clear fields instead of deleting last row
            row_to_remove.set_data({"description": "", "hsn_code": "", "quantity": 1, "unit": "NOS", "rate": 0})
            return
        row_to_remove.destroy()
        self.item_rows.remove(row_to_remove)
        # Renumber remaining rows
        for idx, r in enumerate(self.item_rows, start=1):
            r.index = idx
            r.lbl_sno.configure(text=str(idx))
        self.recalculate_totals()

    def recalculate_totals(self) -> Dict[str, Any]:
        """Compute all totals from item rows and tax rules."""
        items_data = [r.get_data() for r in self.item_rows]
        is_inter = (self.tax_type_var.get() == "inter")

        cgst_r = 0.0 if is_inter else 9.0
        sgst_r = 0.0 if is_inter else 9.0
        igst_r = 18.0 if is_inter else 0.0

        totals = calculate_invoice_totals(
            items_data,
            cgst_rate=cgst_r,
            sgst_rate=sgst_r,
            igst_rate=igst_r,
            is_interstate=is_inter
        )

        # Update labels
        self.lbl_subtotal.configure(text=f"₹ {totals['subtotal']:,.2f}")
        
        if is_inter:
            self.lbl_cgst_val.configure(text="-")
            self.lbl_sgst_val.configure(text="-")
            self.lbl_igst_val.configure(text=f"₹ {totals['igst_amount']:,.2f}")
        else:
            self.lbl_cgst_val.configure(text=f"₹ {totals['cgst_amount']:,.2f}")
            self.lbl_sgst_val.configure(text=f"₹ {totals['sgst_amount']:,.2f}")
            self.lbl_igst_val.configure(text="-")

        self.lbl_tot_tax.configure(text=f"₹ {totals['total_tax']:,.2f}")
        self.lbl_grand_total.configure(text=f"₹ {totals['grand_total']:,.2f}")

        words = amount_to_words(totals["grand_total"])
        self.lbl_in_words.configure(text=words)

        return totals

    def gather_form_data(self) -> Dict[str, Any]:
        """Collect all inputs from the form into a structured dictionary."""
        settings = self.app.settings_repo.get_settings()
        totals = self.recalculate_totals()
        items_data = [r.get_data() for r in self.item_rows if r.get_data().get("description")]

        billed_name = self.entry_billed_name.get().strip()
        billed_addr = self.txt_billed_addr.get("1.0", "end-1c").strip()
        billed_phone = self.entry_billed_phone.get().strip()
        billed_gstin = self.entry_billed_gstin.get().strip().upper()
        billed_state = self.entry_billed_state.get().strip()

        if self.same_as_billed_var.get():
            shipped_name = billed_name
            shipped_addr = billed_addr
            shipped_phone = billed_phone
            shipped_gstin = billed_gstin
            shipped_state = billed_state
        else:
            shipped_name = self.entry_shipped_name.get().strip()
            shipped_addr = self.txt_shipped_addr.get("1.0", "end-1c").strip()
            shipped_phone = self.entry_shipped_phone.get().strip()
            shipped_gstin = billed_gstin
            shipped_state = billed_state

        data = {
            "invoice_no": self.entry_inv_no.get().strip(),
            "invoice_date": self.entry_inv_date.get().strip(),
            "po_no": self.entry_po_no.get().strip(),
            "po_date": self.entry_po_date.get().strip(),
            "vehicle_no": self.entry_vehicle_no.get().strip(),
            "copy_type": self.copy_type_var.get(),
            
            # Company Details from Settings
            "company_name": settings.get("company_name", "NAMURA ENGG. WORKS"),
            "company_address": settings.get("address", "4/8, Balaji Nagar, Vilankurichi, Coimbatore-641035"),
            "company_phone": settings.get("phone", "9842811245"),
            "company_state_code": settings.get("state_code", "33"),
            "company_email": settings.get("email", "namuraew@gmail.com"),
            "company_gstin": settings.get("gstin", "33BKXPS7582P1ZR"),
            "company_pan": settings.get("pan", "BKXPS7582P"),
            "declaration": settings.get("declaration", "Certified that the above particulars are true & correct"),

            # Party details
            "billed_to_name": billed_name,
            "billed_to_address": billed_addr,
            "billed_to_phone": billed_phone,
            "billed_to_gstin": billed_gstin,
            "billed_to_state_code": billed_state,
            "shipped_to_name": shipped_name,
            "shipped_to_address": shipped_addr,
            "shipped_to_phone": shipped_phone,
            "shipped_to_gstin": shipped_gstin,
            "shipped_to_state_code": shipped_state,

            # Line items & totals
            "items": items_data,
            "subtotal": totals["subtotal"],
            "cgst_rate": totals["cgst_rate"],
            "cgst_amount": totals["cgst_amount"],
            "sgst_rate": totals["sgst_rate"],
            "sgst_amount": totals["sgst_amount"],
            "igst_rate": totals["igst_rate"],
            "igst_amount": totals["igst_amount"],
            "total_tax": totals["total_tax"],
            "grand_total": totals["grand_total"],
            "total_in_words": amount_to_words(totals["grand_total"]),
            "payment_status": self.status_var.get(),
            "payment_method": self.method_var.get()
        }

        return data

    def render_live_preview(self):
        """Render temporary PDF and show real-time preview image in the right pane."""
        data = self.gather_form_data()
        
        # Temporary preview file
        preview_pdf = self.app.config_data_dir / "temp_preview.pdf"
        self.pdf_generator.generate(data, preview_pdf)

        # Render with PyMuPDF
        pil_img = PreviewService.render_pdf_to_image(preview_pdf, dpi=130)
        if pil_img:
            # Scale smoothly for display
            display_width = 460
            w_ratio = display_width / float(pil_img.width)
            display_height = int(float(pil_img.height) * w_ratio)

            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(display_width, display_height))
            self.preview_image_label.configure(image=ctk_img, text="")
            self.cached_preview_image = pil_img
            self.generated_pdf_path = str(preview_pdf)

    def confirm_and_generate(self):
        """Validate, save to database, generate final PDF, and update UI."""
        data = self.gather_form_data()
        is_valid, errors = validate_invoice_payload(data)
        if not is_valid:
            messagebox.showerror("Validation Error", "\n".join(errors))
            return

        # Generate final PDF file
        final_pdf_path = self.pdf_generator.generate(data)
        data["pdf_path"] = str(final_pdf_path)

        # Generate final Word file
        final_docx_path = self.docx_generator.generate(data)
        data["docx_path"] = str(final_docx_path)

        # Save to database
        if self.current_invoice_id:
            self.app.invoice_repo.update(self.current_invoice_id, data, data["items"])
        else:
            self.current_invoice_id = self.app.invoice_repo.create(data, data["items"])
            # Increment numbering counter
            self.app.settings_repo.get_next_invoice_number(increment=True)

        self.generated_pdf_path = str(final_pdf_path)
        self.render_live_preview()

        # Show modern confirmation
        msg = f"Invoice {data['invoice_no']} generated successfully!\n\nSaved at:\n{final_pdf_path}"
        ConfirmDialog(
            self,
            title="Invoice Generated Successfully 🎉",
            message=msg,
            on_confirm=self._open_current_pdf,
            confirm_text="Open PDF"
        )

    def save_draft(self):
        """Save invoice without strict item validations."""
        data = self.gather_form_data()
        if not data.get("invoice_no") or not data.get("billed_to_name"):
            messagebox.showerror("Error", "Invoice Number and Customer Name are required to save a draft.")
            return

        if self.current_invoice_id:
            self.app.invoice_repo.update(self.current_invoice_id, data, data["items"])
        else:
            self.current_invoice_id = self.app.invoice_repo.create(data, data["items"])

        messagebox.showinfo("Draft Saved", f"Draft for Invoice {data['invoice_no']} saved successfully.")

    def export_word(self):
        """Export invoice as a Word (.docx) file."""
        data = self.gather_form_data()
        is_valid, errors = validate_invoice_payload(data)
        if not is_valid:
            messagebox.showerror("Validation Error", "\n".join(errors))
            return

        out_path = self.docx_generator.generate(data)
        messagebox.showinfo("Word Export", f"Invoice exported as Word document:\n{out_path}")
        PrintService.open_file(out_path)

    def print_invoice(self):
        """Send current invoice to default printer."""
        if not self.generated_pdf_path:
            self.render_live_preview()
        if self.generated_pdf_path:
            PrintService.print_file(self.generated_pdf_path)

    def _open_current_pdf(self):
        if not self.generated_pdf_path:
            self.render_live_preview()
        if self.generated_pdf_path:
            PrintService.open_file(self.generated_pdf_path)

    def reset_form(self):
        """Clear form and prepare for a new invoice."""
        self.current_invoice_id = None
        self.view_title.configure(text="Create New Tax Invoice")
        
        # Next invoice number
        next_no = self.app.settings_repo.get_next_invoice_number(increment=False)
        self.entry_inv_no.delete(0, "end")
        self.entry_inv_no.insert(0, next_no)

        self.entry_inv_date.delete(0, "end")
        self.entry_inv_date.insert(0, datetime.now().strftime("%d/%m/%Y"))

        self.entry_po_no.delete(0, "end")
        self.entry_po_date.delete(0, "end")
        self.entry_vehicle_no.delete(0, "end")

        self.entry_billed_name.delete(0, "end")
        self.txt_billed_addr.delete("1.0", "end")
        self.entry_billed_phone.delete(0, "end")
        self.entry_billed_gstin.delete(0, "end")
        self.entry_billed_state.delete(0, "end")

        self.same_as_billed_var.set(True)
        self._toggle_shipped_to()

        # Clear item rows and add 2 blank rows
        for r in self.item_rows:
            r.destroy()
        self.item_rows.clear()
        self.add_item_row()
        self.add_item_row()

        self.recalculate_totals()
        self.preview_image_label.configure(image=None, text="Click 'Live Preview' or enter invoice data to view render.")

    def load_invoice(self, invoice_data: Dict[str, Any]):
        """Load an existing invoice for editing or duplicating."""
        self.current_invoice_id = invoice_data.get("id")
        self.view_title.configure(text=f"Edit Invoice {invoice_data.get('invoice_no')}")

        self.entry_inv_no.delete(0, "end")
        self.entry_inv_no.insert(0, invoice_data.get("invoice_no", ""))

        self.entry_inv_date.delete(0, "end")
        self.entry_inv_date.insert(0, invoice_data.get("invoice_date", ""))

        self.entry_po_no.delete(0, "end")
        self.entry_po_no.insert(0, invoice_data.get("po_no", "") or "")

        self.entry_po_date.delete(0, "end")
        self.entry_po_date.insert(0, invoice_data.get("po_date", "") or "")

        self.entry_vehicle_no.delete(0, "end")
        self.entry_vehicle_no.insert(0, invoice_data.get("vehicle_no", "") or "")

        self.copy_type_var.set(invoice_data.get("copy_type", "Original Copy"))

        self.entry_billed_name.delete(0, "end")
        self.entry_billed_name.insert(0, invoice_data.get("billed_to_name", ""))

        self.txt_billed_addr.delete("1.0", "end")
        self.txt_billed_addr.insert("1.0", invoice_data.get("billed_to_address", "") or "")

        self.entry_billed_phone.delete(0, "end")
        self.entry_billed_phone.insert(0, invoice_data.get("billed_to_phone", "") or "")

        self.entry_billed_gstin.delete(0, "end")
        self.entry_billed_gstin.insert(0, invoice_data.get("billed_to_gstin", "") or "")

        self.entry_billed_state.delete(0, "end")
        self.entry_billed_state.insert(0, invoice_data.get("billed_to_state_code", "") or "")

        self.status_var.set(invoice_data.get("payment_status", "Unpaid"))
        self.method_var.set(invoice_data.get("payment_method", "Bank Transfer / NEFT / RTGS"))

        # Items
        for r in self.item_rows:
            r.destroy()
        self.item_rows.clear()

        items = invoice_data.get("items", [])
        if items:
            for itm in items:
                self.add_item_row(itm)
        else:
            self.add_item_row()

        self.recalculate_totals()
        self.render_live_preview()

    def refresh_catalogs(self):
        """Refresh customer and product dropdowns."""
        customers = self.app.customer_repo.get_all()
        cust_names = ["-- Select Existing Customer --"] + [c["name"] for c in customers]
        self.customer_dropdown.configure(values=cust_names)

        products = self.app.product_repo.get_all()
        prod_names = ["+ Quick Insert Product"] + [f"{p['name']} (₹{p['default_rate']})" for p in products]
        self.product_dropdown.configure(values=prod_names)

    def _on_customer_selected(self, choice):
        if choice.startswith("--"):
            return
        customers = self.app.customer_repo.get_all()
        for c in customers:
            if c["name"] == choice:
                self.entry_billed_name.delete(0, "end")
                self.entry_billed_name.insert(0, c["name"])

                self.txt_billed_addr.delete("1.0", "end")
                self.txt_billed_addr.insert("1.0", c.get("address", "") or "")

                self.entry_billed_phone.delete(0, "end")
                self.entry_billed_phone.insert(0, c.get("phone", "") or "")

                self.entry_billed_gstin.delete(0, "end")
                self.entry_billed_gstin.insert(0, c.get("gstin", "") or "")

                self.entry_billed_state.delete(0, "end")
                self.entry_billed_state.insert(0, c.get("state_code", "") or "")
                break

    def _on_product_insert_selected(self, choice):
        if choice.startswith("+"):
            return
        # Parse product name
        prod_name = choice.split(" (₹")[0]
        products = self.app.product_repo.get_all()
        for p in products:
            if p["name"] == prod_name:
                self.add_item_row({
                    "description": p.get("description") or p["name"],
                    "hsn_code": p.get("hsn_code", ""),
                    "quantity": 1,
                    "unit": p.get("unit", "NOS"),
                    "rate": p.get("default_rate", 0)
                })
                break
        self.product_var.set("+ Quick Insert Product")

    def _quick_add_customer(self):
        def _on_save(data):
            self.app.customer_repo.add(data)
            self.refresh_catalogs()
            self.customer_var.set(data["name"])
            self._on_customer_selected(data["name"])

        CustomerDialog(self, on_save=_on_save)
