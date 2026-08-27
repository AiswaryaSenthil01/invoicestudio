"""
Invoice History View: Searchable and filterable archive with comprehensive invoice actions.
"""
import customtkinter as ctk
from tkinter import messagebox, filedialog
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.gui.components.search_bar import SearchBar
from src.gui.components.modal_dialog import ConfirmDialog
from src.utils.calculations import format_indian_currency
from src.services.print_service import PrintService
from src.services.pdf_generator import PDFGenerator
from src.services.docx_generator import DocxGenerator
from src.config import (
    COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_SUCCESS,
    COLOR_WARNING, COLOR_DANGER, COLOR_INFO,
    CARD_DARK, CARD_LIGHT
)


class HistoryView(ctk.CTkFrame):
    def __init__(self, master, app_controller, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.app = app_controller
        self.pdf_generator = PDFGenerator()
        self.docx_generator = DocxGenerator()

        # Top Header
        self._build_header()

        # Filter & Search Toolbar
        self._build_filters()

        # Invoices Table
        self._build_table_container()

    def _build_header(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=24, pady=(20, 10))

        title_frame = ctk.CTkFrame(hdr, fg_color="transparent")
        title_frame.pack(side="left")

        ctk.CTkLabel(
            title_frame,
            text="Invoice History & Management",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold")
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_frame,
            text="Search, filter, view, duplicate, and manage all your generated GST invoices.",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=("gray45", "#94A3B8")
        ).pack(anchor="w")

        ctk.CTkButton(
            hdr,
            text="+ Create New Invoice",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            height=36,
            corner_radius=8,
            command=lambda: self.app.navigate_to("new_invoice")
        ).pack(side="right")

    def _build_filters(self):
        filter_card = ctk.CTkFrame(
            self,
            corner_radius=10,
            fg_color=(CARD_LIGHT, CARD_DARK),
            border_width=1,
            border_color=("gray85", "#334155")
        )
        filter_card.pack(fill="x", padx=24, pady=(0, 12))

        f_row = ctk.CTkFrame(filter_card, fg_color="transparent")
        f_row.pack(fill="x", padx=16, pady=12)

        # Search Bar
        self.search_bar = SearchBar(
            f_row,
            placeholder="Search by Invoice No, Customer, PO #, Vehicle #...",
            filters=["All", "Paid", "Unpaid", "Pending"],
            filter_label="Status",
            on_search=self._on_search_triggered
        )
        self.search_bar.pack(side="left", fill="x", expand=True)

    def _build_table_container(self):
        self.table_card = ctk.CTkFrame(
            self,
            corner_radius=10,
            fg_color=(CARD_LIGHT, CARD_DARK),
            border_width=1,
            border_color=("gray85", "#334155")
        )
        self.table_card.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        # Table Header
        self.th_frame = ctk.CTkFrame(self.table_card, fg_color=("gray90", "#0F172A"), height=38, corner_radius=6)
        self.th_frame.pack(fill="x", padx=12, pady=(12, 6))
        self.th_frame.grid_columnconfigure(0, weight=2)  # Invoice No
        self.th_frame.grid_columnconfigure(1, weight=3)  # Customer
        self.th_frame.grid_columnconfigure(2, weight=2)  # Date
        self.th_frame.grid_columnconfigure(3, weight=2)  # Amount
        self.th_frame.grid_columnconfigure(4, weight=2)  # Status
        self.th_frame.grid_columnconfigure(5, weight=4)  # Actions

        cols = ["INVOICE #", "CUSTOMER", "DATE", "AMOUNT", "STATUS", "ACTIONS"]
        for c_idx, col_name in enumerate(cols):
            anchor = "w" if c_idx in (0, 1) else ("e" if c_idx == 3 else "center")
            ctk.CTkLabel(
                self.th_frame,
                text=col_name,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=("gray50", "#94A3B8"),
                anchor=anchor
            ).grid(row=0, column=c_idx, padx=10, pady=8, sticky="ew")

        # Scrollable Rows
        self.rows_scroll = ctk.CTkScrollableFrame(self.table_card, fg_color="transparent")
        self.rows_scroll.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def _on_search_triggered(self, query: str, status_filter: str):
        self.refresh(query=query, status=status_filter)

    def refresh(self, query: str = "", status: str = "All"):
        """Reload invoices list from SQLite."""
        for w in self.rows_scroll.winfo_children():
            w.destroy()

        invoices = self.app.invoice_repo.get_all(search_query=query, status_filter=status)

        if not invoices:
            ctk.CTkLabel(
                self.rows_scroll,
                text="No invoices found matching your criteria.",
                font=ctk.CTkFont(size=13),
                text_color=("gray45", "#64748B")
            ).pack(pady=40)
            return

        for idx, inv in enumerate(invoices):
            row_frame = ctk.CTkFrame(
                self.rows_scroll,
                fg_color=("white", "#1E293B" if idx % 2 == 0 else "#243048"),
                corner_radius=6,
                height=48
            )
            row_frame.pack(fill="x", pady=2)
            row_frame.grid_columnconfigure(0, weight=2)
            row_frame.grid_columnconfigure(1, weight=3)
            row_frame.grid_columnconfigure(2, weight=2)
            row_frame.grid_columnconfigure(3, weight=2)
            row_frame.grid_columnconfigure(4, weight=2)
            row_frame.grid_columnconfigure(5, weight=4)

            # Invoice No
            ctk.CTkLabel(
                row_frame,
                text=inv.get("invoice_no", ""),
                font=ctk.CTkFont(size=12, weight="bold"),
                anchor="w"
            ).grid(row=0, column=0, padx=10, pady=8, sticky="w")

            # Customer Name
            ctk.CTkLabel(
                row_frame,
                text=inv.get("billed_to_name", "")[:28],
                font=ctk.CTkFont(size=12),
                anchor="w"
            ).grid(row=0, column=1, padx=10, pady=8, sticky="w")

            # Date
            ctk.CTkLabel(
                row_frame,
                text=inv.get("invoice_date", ""),
                font=ctk.CTkFont(size=12),
                anchor="center"
            ).grid(row=0, column=2, padx=10, pady=8, sticky="ew")

            # Amount
            amt_str = f"₹ {format_indian_currency(int(inv.get('grand_total', 0)))}"
            ctk.CTkLabel(
                row_frame,
                text=amt_str,
                font=ctk.CTkFont(size=12, weight="bold"),
                anchor="e"
            ).grid(row=0, column=3, padx=10, pady=8, sticky="e")

            # Status Badge Button (Click to toggle status!)
            status_val = inv.get("payment_status", "Unpaid")
            badge_color = COLOR_SUCCESS if status_val == "Paid" else (COLOR_WARNING if status_val == "Pending" else COLOR_DANGER)
            
            btn_status = ctk.CTkButton(
                row_frame,
                text=status_val,
                font=ctk.CTkFont(size=10, weight="bold"),
                fg_color=badge_color,
                hover_color=COLOR_PRIMARY,
                width=75,
                height=24,
                corner_radius=6,
                command=lambda i=inv: self._toggle_invoice_status(i)
            )
            btn_status.grid(row=0, column=4, padx=10, pady=8)

            # Actions Bar
            act_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            act_frame.grid(row=0, column=5, padx=10, pady=8, sticky="e")

            # 1. View PDF
            ctk.CTkButton(
                act_frame,
                text="PDF",
                width=45,
                height=26,
                font=ctk.CTkFont(size=11),
                fg_color=COLOR_PRIMARY,
                hover_color=COLOR_PRIMARY_HOVER,
                command=lambda i=inv: self._view_pdf(i)
            ).pack(side="left", padx=2)

            # 2. Word
            ctk.CTkButton(
                act_frame,
                text="Word",
                width=48,
                height=26,
                font=ctk.CTkFont(size=11),
                fg_color=COLOR_INFO,
                hover_color="#4F46E5",
                command=lambda i=inv: self._export_docx(i)
            ).pack(side="left", padx=2)

            # 3. Edit
            ctk.CTkButton(
                act_frame,
                text="Edit",
                width=45,
                height=26,
                font=ctk.CTkFont(size=11),
                fg_color=("gray85", "#334155"),
                text_color=("black", "white"),
                hover_color=("gray75", "#475569"),
                command=lambda i=inv: self._edit_invoice(i)
            ).pack(side="left", padx=2)

            # 4. Duplicate
            ctk.CTkButton(
                act_frame,
                text="Clone",
                width=48,
                height=26,
                font=ctk.CTkFont(size=11),
                fg_color=("gray85", "#334155"),
                text_color=("black", "white"),
                hover_color=("gray75", "#475569"),
                command=lambda i=inv: self._duplicate_invoice(i)
            ).pack(side="left", padx=2)

            # 5. Delete
            ctk.CTkButton(
                act_frame,
                text="✕",
                width=28,
                height=26,
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color=("gray85", "#334155"),
                text_color=COLOR_DANGER,
                hover_color=COLOR_DANGER,
                command=lambda i=inv: self._delete_invoice(i)
            ).pack(side="left", padx=2)

    def _view_pdf(self, inv: Dict[str, Any]):
        full_inv = self.app.invoice_repo.get_by_id(inv["id"])
        if not full_inv:
            return
        pdf_path = full_inv.get("pdf_path")
        if not pdf_path or not self.app.file_exists(pdf_path):
            # Regenerate if file missing
            pdf_path = str(self.pdf_generator.generate(full_inv))
            self.app.invoice_repo.update(full_inv["id"], {**full_inv, "pdf_path": pdf_path}, full_inv.get("items", []))
        PrintService.open_file(pdf_path)

    def _export_docx(self, inv: Dict[str, Any]):
        full_inv = self.app.invoice_repo.get_by_id(inv["id"])
        if not full_inv:
            return
        docx_path = str(self.docx_generator.generate(full_inv))
        PrintService.open_file(docx_path)

    def _edit_invoice(self, inv: Dict[str, Any]):
        full_inv = self.app.invoice_repo.get_by_id(inv["id"])
        if full_inv:
            self.app.new_invoice_view.load_invoice(full_inv)
            self.app.navigate_to("new_invoice")

    def _duplicate_invoice(self, inv: Dict[str, Any]):
        full_inv = self.app.invoice_repo.get_by_id(inv["id"])
        if not full_inv:
            return
        # Clone with new invoice number and current date
        next_no = self.app.settings_repo.get_next_invoice_number(increment=False)
        cloned_data = dict(full_inv)
        cloned_data["id"] = None
        cloned_data["invoice_no"] = next_no
        cloned_data["invoice_date"] = datetime.now().strftime("%d/%m/%Y")
        cloned_data["payment_status"] = "Unpaid"

        self.app.new_invoice_view.load_invoice(cloned_data)
        self.app.navigate_to("new_invoice")

    def _toggle_invoice_status(self, inv: Dict[str, Any]):
        statuses = ["Unpaid", "Paid", "Pending"]
        curr = inv.get("payment_status", "Unpaid")
        next_idx = (statuses.index(curr) + 1) % len(statuses) if curr in statuses else 0
        new_status = statuses[next_idx]
        self.app.invoice_repo.update_payment_status(inv["id"], new_status)
        self.refresh(query=self.search_bar.search_entry.get(), status=self.search_bar.filter_var.get())

    def _delete_invoice(self, inv: Dict[str, Any]):
        def _confirm():
            self.app.invoice_repo.delete(inv["id"])
            self.refresh(query=self.search_bar.search_entry.get(), status=self.search_bar.filter_var.get())

        ConfirmDialog(
            self,
            title="Delete Invoice",
            message=f"Are you sure you want to permanently delete Invoice {inv.get('invoice_no')}?",
            on_confirm=_confirm,
            confirm_text="Delete",
            is_danger=True
        )
