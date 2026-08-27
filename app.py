"""
Main Application Window with responsive modern sidebar navigation and view management.
"""
import os
import sys
from pathlib import Path
import customtkinter as ctk

from src.config import (
    APP_NAME, APP_SUBTITLE, APP_VERSION,
    THEME_MODE, SIDEBAR_DARK, SIDEBAR_LIGHT,
    COLOR_PRIMARY, COLOR_PRIMARY_HOVER, BG_DARK, BG_LIGHT,
    DATA_DIR, DATABASE_PATH, INVOICES_DIR
)
from src.database.db_manager import DatabaseManager
from src.database.settings_repository import SettingsRepository
from src.database.customer_repository import CustomerRepository
from src.database.product_repository import ProductRepository
from src.database.invoice_repository import InvoiceRepository
from src.services.print_service import PrintService

from src.gui.views.dashboard_view import DashboardView
from src.gui.views.new_invoice_view import NewInvoiceView
from src.gui.views.history_view import HistoryView
from src.gui.views.customers_view import CustomersView
from src.gui.views.products_view import ProductsView
from src.gui.views.settings_view import SettingsView


class InvoiceApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Appearance & Window Configuration
        ctk.set_appearance_mode(THEME_MODE)
        ctk.set_default_color_theme("blue")

        self.title(f"{APP_NAME} - {APP_SUBTITLE}")
        self.geometry("1280x820")
        self.minsize(1050, 700)

        # Initialize Database & Repositories
        self.config_data_dir = DATA_DIR
        self.db_manager = DatabaseManager(DATABASE_PATH)
        self.settings_repo = SettingsRepository(self.db_manager)
        self.customer_repo = CustomerRepository(self.db_manager)
        self.product_repo = ProductRepository(self.db_manager)
        self.invoice_repo = InvoiceRepository(self.db_manager)

        # Layout Configuration
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)  # Sidebar (fixed width)
        self.grid_columnconfigure(1, weight=1)  # Main View Container (responsive)

        # Navigation State
        self.nav_buttons = {}
        self.views = {}
        self.current_view_name = None

        # Build Sidebar and Main Container
        self._build_sidebar()
        self._build_main_container()

        # Initialize and show default view
        self.navigate_to("dashboard")

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self,
            width=230,
            corner_radius=0,
            fg_color=(SIDEBAR_LIGHT, SIDEBAR_DARK),
            border_width=0
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(8, weight=1)  # Spacer pushes settings/theme to bottom

        # App Brand Header
        brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_frame.grid(row=0, column=0, padx=20, pady=(24, 20), sticky="ew")

        ctk.CTkLabel(
            brand_frame,
            text="NAMURA",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=COLOR_PRIMARY,
            anchor="w"
        ).pack(anchor="w")

        ctk.CTkLabel(
            brand_frame,
            text="INVOICE STUDIO",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=("gray40", "#94A3B8"),
            anchor="w"
        ).pack(anchor="w")

        # Navigation Menu Items
        nav_items = [
            ("dashboard", "📊  Dashboard", 1),
            ("new_invoice", "➕  New Invoice", 2),
            ("history", "📜  Invoice History", 3),
            ("customers", "👥  Customers", 4),
            ("products", "📦  Products / Catalog", 5),
            ("settings", "⚙  Company Settings", 6),
        ]

        for view_key, label_text, row_idx in nav_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=label_text,
                font=ctk.CTkFont(family="Segoe UI", size=13),
                fg_color="transparent",
                text_color=("gray20", "#E2E8F0"),
                hover_color=("gray85", "#1E293B"),
                anchor="w",
                height=42,
                corner_radius=8,
                command=lambda k=view_key: self.navigate_to(k)
            )
            btn.grid(row=row_idx, column=0, padx=12, pady=4, sticky="ew")
            self.nav_buttons[view_key] = btn

        # Bottom Section (Theme Toggle & Info)
        bottom_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        bottom_frame.grid(row=9, column=0, padx=16, pady=16, sticky="ew")

        # Theme Toggle
        theme_row = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        theme_row.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            theme_row,
            text="Dark Theme",
            font=ctk.CTkFont(size=11),
            text_color=("gray40", "#94A3B8")
        ).pack(side="left")

        self.theme_switch = ctk.CTkSwitch(
            theme_row,
            text="",
            width=40,
            command=self._toggle_theme
        )
        self.theme_switch.pack(side="right")
        if ctk.get_appearance_mode() == "Dark":
            self.theme_switch.select()

        # Version text
        ctk.CTkLabel(
            bottom_frame,
            text=f"Version {APP_VERSION} • GST Ready",
            font=ctk.CTkFont(size=10),
            text_color=("gray50", "#64748B")
        ).pack(anchor="w")

    def _build_main_container(self):
        self.main_container = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew")
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        # Initialize all View instances
        self.dashboard_view = DashboardView(self.main_container, self)
        self.new_invoice_view = NewInvoiceView(self.main_container, self)
        self.history_view = HistoryView(self.main_container, self)
        self.customers_view = CustomersView(self.main_container, self)
        self.products_view = ProductsView(self.main_container, self)
        self.settings_view = SettingsView(self.main_container, self)

        self.views = {
            "dashboard": self.dashboard_view,
            "new_invoice": self.new_invoice_view,
            "history": self.history_view,
            "customers": self.customers_view,
            "products": self.products_view,
            "settings": self.settings_view,
        }

        # Grid all views (they will be raised on navigation)
        for view in self.views.values():
            view.grid(row=0, column=0, sticky="nsew")

    def navigate_to(self, view_name: str, action: str = None):
        """Switch active view and update sidebar indicator."""
        if view_name not in self.views:
            return

        # Hide / Show view
        target_view = self.views[view_name]
        target_view.tkraise()
        self.current_view_name = view_name

        # Update sidebar active states
        for k, btn in self.nav_buttons.items():
            if k == view_name:
                btn.configure(fg_color=COLOR_PRIMARY, text_color="white", hover_color=COLOR_PRIMARY_HOVER)
            else:
                btn.configure(fg_color="transparent", text_color=("gray20", "#E2E8F0"), hover_color=("gray85", "#1E293B"))

        # Trigger view-specific refresh
        if view_name == "dashboard":
            self.dashboard_view.refresh()
        elif view_name == "new_invoice":
            self.new_invoice_view.refresh_catalogs()
            if action == "reset" or self.new_invoice_view.current_invoice_id is None:
                if not self.new_invoice_view.entry_inv_no.get():
                    self.new_invoice_view.reset_form()
        elif view_name == "history":
            self.history_view.refresh()
        elif view_name == "customers":
            self.customers_view.refresh()
            if action == "add":
                self.customers_view.open_add_dialog()
        elif view_name == "products":
            self.products_view.refresh()
            if action == "add":
                self.products_view.open_add_dialog()
        elif view_name == "settings":
            self.settings_view.refresh()

    def _toggle_theme(self):
        if self.theme_switch.get() == 1:
            ctk.set_appearance_mode("Dark")
        else:
            ctk.set_appearance_mode("Light")

    def file_exists(self, file_path: str) -> bool:
        return Path(file_path).exists() if file_path else False

    def open_invoice_pdf(self, pdf_path: str, invoice_dict: dict = None):
        if pdf_path and self.file_exists(pdf_path):
            PrintService.open_file(pdf_path)
        elif invoice_dict:
            full_inv = self.invoice_repo.get_by_id(invoice_dict["id"])
            if full_inv:
                new_pdf = self.new_invoice_view.pdf_generator.generate(full_inv)
                self.invoice_repo.update(full_inv["id"], {**full_inv, "pdf_path": str(new_pdf)}, full_inv.get("items", []))
                PrintService.open_file(new_pdf)
