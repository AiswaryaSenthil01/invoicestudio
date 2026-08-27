"""
Dashboard View: Executive summary metrics, quick actions, and recent activity.
"""
import customtkinter as ctk
from typing import Callable, Optional
from datetime import datetime

from src.gui.components.stat_card import StatCard
from src.utils.calculations import format_indian_currency
from src.config import (
    COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_SUCCESS,
    COLOR_WARNING, COLOR_DANGER, COLOR_INFO,
    CARD_DARK, CARD_LIGHT
)


class DashboardView(ctk.CTkFrame):
    def __init__(self, master, app_controller, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.app = app_controller

        # Main Scrollable Container
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=24, pady=20)

        # Header Section
        self._build_header()

        # Metrics Grid (4 Stat Cards)
        self._build_metrics_grid()

        # Quick Actions Row
        self._build_quick_actions()

        # Recent Invoices Section
        self._build_recent_invoices_table()

    def _build_header(self):
        hdr = ctk.CTkFrame(self.scroll, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 20))

        title_frame = ctk.CTkFrame(hdr, fg_color="transparent")
        title_frame.pack(side="left")

        ctk.CTkLabel(
            title_frame,
            text="Business Overview",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold")
        ).pack(anchor="w")

        today_str = datetime.now().strftime("%A, %d %B %Y")
        ctk.CTkLabel(
            title_frame,
            text=f"Today is {today_str}",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=("gray45", "#94A3B8")
        ).pack(anchor="w")

        # Action button
        ctk.CTkButton(
            hdr,
            text="+ Create New Invoice",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            height=40,
            corner_radius=8,
            command=lambda: self.app.navigate_to("new_invoice")
        ).pack(side="right")

    def _build_metrics_grid(self):
        self.metrics_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.metrics_frame.pack(fill="x", pady=(0, 24))
        self.metrics_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="stat_cards")

        self.card_rev = StatCard(self.metrics_frame, title="Total Revenue", value="₹ 0", subtitle="Lifetime billed", accent_color=COLOR_PRIMARY, icon_text="₹")
        self.card_rev.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

        self.card_inv = StatCard(self.metrics_frame, title="Total Invoices", value="0", subtitle="Invoices generated", accent_color=COLOR_INFO, icon_text="DOC")
        self.card_inv.grid(row=0, column=1, padx=5, sticky="nsew")

        self.card_paid = StatCard(self.metrics_frame, title="Paid Revenue", value="₹ 0", subtitle="0 fully paid", accent_color=COLOR_SUCCESS, icon_text="PAID")
        self.card_paid.grid(row=0, column=2, padx=5, sticky="nsew")

        self.card_unpaid = StatCard(self.metrics_frame, title="Unpaid / Pending", value="₹ 0", subtitle="0 pending collection", accent_color=COLOR_WARNING, icon_text="DUE")
        self.card_unpaid.grid(row=0, column=3, padx=(10, 0), sticky="nsew")

    def _build_quick_actions(self):
        actions_card = ctk.CTkFrame(
            self.scroll,
            corner_radius=12,
            fg_color=(CARD_LIGHT, CARD_DARK),
            border_width=1,
            border_color=("gray85", "#334155")
        )
        actions_card.pack(fill="x", pady=(0, 24))

        ctk.CTkLabel(
            actions_card,
            text="Quick Shortcuts",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        ).pack(anchor="w", padx=16, pady=(12, 10))

        btn_row = ctk.CTkFrame(actions_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=16, pady=(0, 14))

        buttons = [
            ("+ New Customer", lambda: self.app.navigate_to("customers", action="add")),
            ("+ New Product / Service", lambda: self.app.navigate_to("products", action="add")),
            ("📜 Invoice History", lambda: self.app.navigate_to("history")),
            ("⚙ Company Settings", lambda: self.app.navigate_to("settings"))
        ]

        for text, cmd in buttons:
            ctk.CTkButton(
                btn_row,
                text=text,
                font=ctk.CTkFont(family="Segoe UI", size=12),
                fg_color=("gray85", "#334155"),
                text_color=("black", "white"),
                hover_color=("gray75", "#475569"),
                height=36,
                corner_radius=8,
                command=cmd
            ).pack(side="left", padx=(0, 10))

    def _build_recent_invoices_table(self):
        self.recent_card = ctk.CTkFrame(
            self.scroll,
            corner_radius=12,
            fg_color=(CARD_LIGHT, CARD_DARK),
            border_width=1,
            border_color=("gray85", "#334155")
        )
        self.recent_card.pack(fill="both", expand=True)

        header_bar = ctk.CTkFrame(self.recent_card, fg_color="transparent")
        header_bar.pack(fill="x", padx=16, pady=(14, 10))

        ctk.CTkLabel(
            header_bar,
            text="Recent Invoices",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        ).pack(side="left")

        ctk.CTkButton(
            header_bar,
            text="View All →",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color="transparent",
            text_color=COLOR_PRIMARY,
            hover=False,
            command=lambda: self.app.navigate_to("history")
        ).pack(side="right")

        self.table_container = ctk.CTkFrame(self.recent_card, fg_color="transparent")
        self.table_container.pack(fill="both", expand=True, padx=16, pady=(0, 14))

    def refresh(self):
        """Refresh stats and recent invoices list from SQLite."""
        stats = self.app.invoice_repo.get_dashboard_stats()

        # Update cards
        tot_rev_str = f"₹ {format_indian_currency(int(stats['total_revenue']))}"
        self.card_rev.update_value(tot_rev_str)

        self.card_inv.update_value(str(stats["total_invoices"]))

        paid_str = f"₹ {format_indian_currency(int(stats['paid_amount']))}"
        self.card_paid.update_value(paid_str, f"{stats['paid_count']} invoices settled")

        unpaid_str = f"₹ {format_indian_currency(int(stats['unpaid_amount']))}"
        self.card_unpaid.update_value(unpaid_str, f"{stats['unpaid_count']} pending payments")

        # Clear and repopulate table
        for widget in self.table_container.winfo_children():
            widget.destroy()

        recent = stats.get("recent_invoices", [])
        if not recent:
            ctk.CTkLabel(
                self.table_container,
                text="No invoices generated yet. Click '+ Create New Invoice' to start!",
                font=ctk.CTkFont(size=12),
                text_color=("gray40", "#64748B")
            ).pack(pady=30)
            return

        # Table Header
        tbl_hdr = ctk.CTkFrame(self.table_container, fg_color=("gray90", "#0F172A"), height=36, corner_radius=6)
        tbl_hdr.pack(fill="x", pady=(0, 6))
        tbl_hdr.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        cols = ["INVOICE #", "CUSTOMER", "DATE", "AMOUNT", "STATUS", "ACTION"]
        for col_idx, col_name in enumerate(cols):
            anchor = "w" if col_idx in (0, 1) else ("e" if col_idx == 3 else "center")
            ctk.CTkLabel(
                tbl_hdr,
                text=col_name,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=("gray50", "#94A3B8"),
                anchor=anchor
            ).grid(row=0, column=col_idx, padx=10, pady=8, sticky="ew")

        # Rows
        for r_idx, inv in enumerate(recent):
            row_frame = ctk.CTkFrame(self.table_container, fg_color=("white", "#1E293B" if r_idx % 2 == 0 else "#243048"), height=42, corner_radius=6)
            row_frame.pack(fill="x", pady=2)
            row_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

            # Invoice No
            ctk.CTkLabel(
                row_frame,
                text=inv.get("invoice_no", ""),
                font=ctk.CTkFont(size=12, weight="bold"),
                anchor="w"
            ).grid(row=0, column=0, padx=10, pady=6, sticky="w")

            # Customer Name
            ctk.CTkLabel(
                row_frame,
                text=inv.get("billed_to_name", "")[:26],
                font=ctk.CTkFont(size=12),
                anchor="w"
            ).grid(row=0, column=1, padx=10, pady=6, sticky="w")

            # Date
            ctk.CTkLabel(
                row_frame,
                text=inv.get("invoice_date", ""),
                font=ctk.CTkFont(size=12),
                anchor="center"
            ).grid(row=0, column=2, padx=10, pady=6, sticky="ew")

            # Amount
            amt_str = f"₹ {format_indian_currency(int(inv.get('grand_total', 0)))}"
            ctk.CTkLabel(
                row_frame,
                text=amt_str,
                font=ctk.CTkFont(size=12, weight="bold"),
                anchor="e"
            ).grid(row=0, column=3, padx=10, pady=6, sticky="e")

            # Status Badge
            status = inv.get("payment_status", "Unpaid")
            badge_color = COLOR_SUCCESS if status == "Paid" else (COLOR_WARNING if status == "Pending" else COLOR_DANGER)
            badge = ctk.CTkLabel(
                row_frame,
                text=f" {status} ",
                font=ctk.CTkFont(size=10, weight="bold"),
                fg_color=badge_color,
                text_color="white",
                corner_radius=6
            )
            badge.grid(row=0, column=4, padx=10, pady=6)

            # Action Button
            pdf_path = inv.get("pdf_path")
            act_btn = ctk.CTkButton(
                row_frame,
                text="View PDF",
                font=ctk.CTkFont(size=11),
                width=75,
                height=26,
                corner_radius=6,
                fg_color=("gray85", "#334155"),
                text_color=("black", "white"),
                hover_color=COLOR_PRIMARY,
                command=lambda p=pdf_path, i=inv: self.app.open_invoice_pdf(p, i)
            )
            act_btn.grid(row=0, column=5, padx=10, pady=6)
