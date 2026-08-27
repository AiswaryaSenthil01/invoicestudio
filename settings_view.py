"""
Company Settings and Invoice Numbering Configuration View.
"""
import customtkinter as ctk
from tkinter import messagebox
from typing import Dict, Any
from src.config import (
    COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_SUCCESS,
    CARD_DARK, CARD_LIGHT
)


class SettingsView(ctk.CTkFrame):
    def __init__(self, master, app_controller, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.app = app_controller

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=24, pady=20)

        self._build_header()
        self._build_settings_form()

    def _build_header(self):
        hdr = ctk.CTkFrame(self.scroll, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(
            hdr,
            text="Company & System Settings",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold")
        ).pack(anchor="w")

        ctk.CTkLabel(
            hdr,
            text="Configure your business profile, GST tax details, and automatic invoice numbering format.",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=("gray45", "#94A3B8")
        ).pack(anchor="w")

    def _build_settings_form(self):
        self.entries: Dict[str, Any] = {}

        # Card 1: Company Profile
        card1 = ctk.CTkFrame(self.scroll, corner_radius=10, fg_color=(CARD_LIGHT, CARD_DARK), border_width=1, border_color=("gray85", "#334155"))
        card1.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(card1, text="1. Business Profile (Prints on Invoices)", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=16, pady=(12, 10))

        grid1 = ctk.CTkFrame(card1, fg_color="transparent")
        grid1.pack(fill="x", padx=16, pady=(0, 14))
        grid1.grid_columnconfigure((0, 1), weight=1)

        # Company Name
        ctk.CTkLabel(grid1, text="Company Name *", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=0, sticky="w", padx=6, pady=2)
        ctk.CTkLabel(grid1, text="Company Address *", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=1, sticky="w", padx=6, pady=2)

        self.entries["company_name"] = ctk.CTkEntry(grid1, height=36, corner_radius=6)
        self.entries["company_name"].grid(row=1, column=0, sticky="ew", padx=6, pady=(0, 8))

        self.entries["address"] = ctk.CTkEntry(grid1, height=36, corner_radius=6)
        self.entries["address"].grid(row=1, column=1, sticky="ew", padx=6, pady=(0, 8))

        # Phone & Email
        ctk.CTkLabel(grid1, text="Phone Number *", font=ctk.CTkFont(size=11, weight="bold")).grid(row=2, column=0, sticky="w", padx=6, pady=2)
        ctk.CTkLabel(grid1, text="Email Address *", font=ctk.CTkFont(size=11, weight="bold")).grid(row=2, column=1, sticky="w", padx=6, pady=2)

        self.entries["phone"] = ctk.CTkEntry(grid1, height=36, corner_radius=6)
        self.entries["phone"].grid(row=3, column=0, sticky="ew", padx=6, pady=(0, 8))

        self.entries["email"] = ctk.CTkEntry(grid1, height=36, corner_radius=6)
        self.entries["email"].grid(row=3, column=1, sticky="ew", padx=6, pady=(0, 8))

        # GSTIN, PAN, State Code
        ctk.CTkLabel(grid1, text="GSTIN NO *", font=ctk.CTkFont(size=11, weight="bold")).grid(row=4, column=0, sticky="w", padx=6, pady=2)
        ctk.CTkLabel(grid1, text="PAN NO *", font=ctk.CTkFont(size=11, weight="bold")).grid(row=4, column=1, sticky="w", padx=6, pady=2)

        self.entries["gstin"] = ctk.CTkEntry(grid1, height=36, corner_radius=6)
        self.entries["gstin"].grid(row=5, column=0, sticky="ew", padx=6, pady=(0, 8))

        self.entries["pan"] = ctk.CTkEntry(grid1, height=36, corner_radius=6)
        self.entries["pan"].grid(row=5, column=1, sticky="ew", padx=6, pady=(0, 8))

        ctk.CTkLabel(grid1, text="State Code (e.g. 33)", font=ctk.CTkFont(size=11, weight="bold")).grid(row=6, column=0, sticky="w", padx=6, pady=2)
        self.entries["state_code"] = ctk.CTkEntry(grid1, height=36, corner_radius=6)
        self.entries["state_code"].grid(row=7, column=0, sticky="ew", padx=6)

        # Card 2: Invoice Numbering & Sequence
        card2 = ctk.CTkFrame(self.scroll, corner_radius=10, fg_color=(CARD_LIGHT, CARD_DARK), border_width=1, border_color=("gray85", "#334155"))
        card2.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(card2, text="2. Automatic Invoice Numbering Sequence", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=16, pady=(12, 10))

        grid2 = ctk.CTkFrame(card2, fg_color="transparent")
        grid2.pack(fill="x", padx=16, pady=(0, 14))
        grid2.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(grid2, text="Invoice Prefix (e.g. INV-)", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=0, sticky="w", padx=6, pady=2)
        ctk.CTkLabel(grid2, text="Next Number (e.g. 1)", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=1, sticky="w", padx=6, pady=2)
        ctk.CTkLabel(grid2, text="Zero Padding (e.g. 3 -> 001)", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=2, sticky="w", padx=6, pady=2)

        self.entries["invoice_prefix"] = ctk.CTkEntry(grid2, height=36, corner_radius=6)
        self.entries["invoice_prefix"].grid(row=1, column=0, sticky="ew", padx=6)

        self.entries["next_invoice_num"] = ctk.CTkEntry(grid2, height=36, corner_radius=6)
        self.entries["next_invoice_num"].grid(row=1, column=1, sticky="ew", padx=6)

        self.entries["invoice_num_padding"] = ctk.CTkEntry(grid2, height=36, corner_radius=6)
        self.entries["invoice_num_padding"].grid(row=1, column=2, sticky="ew", padx=6)

        # Card 3: Declaration & Legal
        card3 = ctk.CTkFrame(self.scroll, corner_radius=10, fg_color=(CARD_LIGHT, CARD_DARK), border_width=1, border_color=("gray85", "#334155"))
        card3.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(card3, text="3. Footer Declaration & Terms", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=16, pady=(12, 10))

        ctk.CTkLabel(card3, text="Invoice Declaration (Printed above signature):", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w", padx=16, pady=(0, 4))
        self.entries["declaration"] = ctk.CTkEntry(card3, height=36, corner_radius=6)
        self.entries["declaration"].pack(fill="x", padx=16, pady=(0, 14))

        # Save Button
        btn_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkButton(
            btn_frame,
            text="Save Settings",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=COLOR_SUCCESS,
            hover_color="#059669",
            height=40,
            width=160,
            command=self._save_settings
        ).pack(side="right")

    def refresh(self):
        settings = self.app.settings_repo.get_settings()
        for field, widget in self.entries.items():
            val = settings.get(field, "")
            widget.delete(0, "end")
            widget.insert(0, str(val) if val is not None else "")

    def _save_settings(self):
        data = {}
        for field, widget in self.entries.items():
            val = widget.get().strip()
            if field in ("next_invoice_num", "invoice_num_padding"):
                try:
                    data[field] = int(val)
                except ValueError:
                    messagebox.showerror("Error", f"{field} must be an integer.")
                    return
            else:
                data[field] = val

        self.app.settings_repo.update_settings(data)
        messagebox.showinfo("Success", "Company settings saved successfully!")
        self.app.new_invoice_view.refresh_catalogs()
