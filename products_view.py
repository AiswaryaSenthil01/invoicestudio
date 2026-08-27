"""
Products and Services Catalog View.
"""
import customtkinter as ctk
from src.gui.components.search_bar import SearchBar
from src.gui.components.modal_dialog import ProductDialog, ConfirmDialog
from src.utils.calculations import format_indian_currency
from src.config import (
    COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_DANGER,
    CARD_DARK, CARD_LIGHT
)


class ProductsView(ctk.CTkFrame):
    def __init__(self, master, app_controller, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.app = app_controller

        self._build_header()
        self._build_search()
        self._build_list_container()

    def _build_header(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=24, pady=(20, 10))

        title_frame = ctk.CTkFrame(hdr, fg_color="transparent")
        title_frame.pack(side="left")

        ctk.CTkLabel(
            title_frame,
            text="Products & Services Catalog",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold")
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_frame,
            text="Manage standard items, default unit rates, HSN codes, and tax classifications.",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=("gray45", "#94A3B8")
        ).pack(anchor="w")

        ctk.CTkButton(
            hdr,
            text="+ Add Item",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            height=36,
            corner_radius=8,
            command=self.open_add_dialog
        ).pack(side="right")

    def _build_search(self):
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

        self.search_bar = SearchBar(
            f_row,
            placeholder="Search by product name, description, HSN code...",
            on_search=lambda q, f: self.refresh(query=q)
        )
        self.search_bar.pack(side="left", fill="x", expand=True)

    def _build_list_container(self):
        self.list_card = ctk.CTkFrame(
            self,
            corner_radius=10,
            fg_color=(CARD_LIGHT, CARD_DARK),
            border_width=1,
            border_color=("gray85", "#334155")
        )
        self.list_card.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        # Table Header
        self.th_frame = ctk.CTkFrame(self.list_card, fg_color=("gray90", "#0F172A"), height=36, corner_radius=6)
        self.th_frame.pack(fill="x", padx=12, pady=(12, 6))
        self.th_frame.grid_columnconfigure(0, weight=3)  # Name / Desc
        self.th_frame.grid_columnconfigure(1, weight=2)  # HSN
        self.th_frame.grid_columnconfigure(2, weight=2)  # Unit & Tax
        self.th_frame.grid_columnconfigure(3, weight=2)  # Default Rate
        self.th_frame.grid_columnconfigure(4, weight=2)  # Actions

        ctk.CTkLabel(self.th_frame, text="PRODUCT / SERVICE", font=ctk.CTkFont(size=11, weight="bold"), anchor="w").grid(row=0, column=0, padx=10, pady=8, sticky="w")
        ctk.CTkLabel(self.th_frame, text="HSN CODE", font=ctk.CTkFont(size=11, weight="bold"), anchor="center").grid(row=0, column=1, padx=10, pady=8, sticky="ew")
        ctk.CTkLabel(self.th_frame, text="UNIT / TAX", font=ctk.CTkFont(size=11, weight="bold"), anchor="center").grid(row=0, column=2, padx=10, pady=8, sticky="ew")
        ctk.CTkLabel(self.th_frame, text="DEFAULT RATE", font=ctk.CTkFont(size=11, weight="bold"), anchor="e").grid(row=0, column=3, padx=10, pady=8, sticky="e")
        ctk.CTkLabel(self.th_frame, text="ACTIONS", font=ctk.CTkFont(size=11, weight="bold"), anchor="center").grid(row=0, column=4, padx=10, pady=8, sticky="ew")

        self.rows_scroll = ctk.CTkScrollableFrame(self.list_card, fg_color="transparent")
        self.rows_scroll.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def refresh(self, query: str = ""):
        for w in self.rows_scroll.winfo_children():
            w.destroy()

        products = self.app.product_repo.get_all(search_query=query)

        if not products:
            ctk.CTkLabel(
                self.rows_scroll,
                text="No products or services found in catalog.",
                font=ctk.CTkFont(size=13),
                text_color=("gray45", "#64748B")
            ).pack(pady=40)
            return

        for idx, prod in enumerate(products):
            row_frame = ctk.CTkFrame(
                self.rows_scroll,
                fg_color=("white", "#1E293B" if idx % 2 == 0 else "#243048"),
                corner_radius=6,
                height=48
            )
            row_frame.pack(fill="x", pady=2)
            row_frame.grid_columnconfigure(0, weight=3)
            row_frame.grid_columnconfigure(1, weight=2)
            row_frame.grid_columnconfigure(2, weight=2)
            row_frame.grid_columnconfigure(3, weight=2)
            row_frame.grid_columnconfigure(4, weight=2)

            # Name & Desc
            p_name_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            p_name_frame.grid(row=0, column=0, padx=10, pady=6, sticky="w")
            ctk.CTkLabel(p_name_frame, text=prod["name"], font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(anchor="w")
            if prod.get("description"):
                ctk.CTkLabel(p_name_frame, text=prod["description"][:40] + ("..." if len(prod["description"]) > 40 else ""), font=ctk.CTkFont(size=10), text_color=("gray45", "#94A3B8"), anchor="w").pack(anchor="w")

            # HSN
            ctk.CTkLabel(
                row_frame,
                text=prod.get("hsn_code") or "-",
                font=ctk.CTkFont(size=12),
                anchor="center"
            ).grid(row=0, column=1, padx=10, pady=6, sticky="ew")

            # Unit & Tax
            unit_tax_str = f"{prod.get('unit', 'NOS')} • GST {prod.get('tax_rate', 18):g}%"
            ctk.CTkLabel(
                row_frame,
                text=unit_tax_str,
                font=ctk.CTkFont(size=11),
                anchor="center"
            ).grid(row=0, column=2, padx=10, pady=6, sticky="ew")

            # Rate
            rate_str = f"₹ {format_indian_currency(int(prod.get('default_rate', 0)))}"
            ctk.CTkLabel(
                row_frame,
                text=rate_str,
                font=ctk.CTkFont(size=12, weight="bold"),
                anchor="e"
            ).grid(row=0, column=3, padx=10, pady=6, sticky="e")

            # Actions
            act_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            act_frame.grid(row=0, column=4, padx=10, pady=6, sticky="e")

            ctk.CTkButton(
                act_frame,
                text="Edit",
                width=55,
                height=28,
                font=ctk.CTkFont(size=11),
                fg_color=("gray85", "#334155"),
                text_color=("black", "white"),
                hover_color=COLOR_PRIMARY,
                command=lambda p=prod: self.open_edit_dialog(p)
            ).pack(side="left", padx=4)

            ctk.CTkButton(
                act_frame,
                text="✕",
                width=28,
                height=28,
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color=("gray85", "#334155"),
                text_color=COLOR_DANGER,
                hover_color=COLOR_DANGER,
                command=lambda p=prod: self._delete_product(p)
            ).pack(side="left", padx=2)

    def open_add_dialog(self):
        def _on_save(data):
            self.app.product_repo.add(data)
            self.refresh()
            self.app.new_invoice_view.refresh_catalogs()

        ProductDialog(self, on_save=_on_save)

    def open_edit_dialog(self, product: Dict[str, Any]):
        def _on_save(data):
            self.app.product_repo.update(product["id"], data)
            self.refresh()
            self.app.new_invoice_view.refresh_catalogs()

        ProductDialog(self, product_data=product, on_save=_on_save)

    def _delete_product(self, product: Dict[str, Any]):
        def _confirm():
            self.app.product_repo.delete(product["id"])
            self.refresh()
            self.app.new_invoice_view.refresh_catalogs()

        ConfirmDialog(
            self,
            title="Delete Product",
            message=f"Are you sure you want to delete '{product['name']}'?",
            on_confirm=_confirm,
            confirm_text="Delete",
            is_danger=True
        )
