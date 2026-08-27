"""
Customer Management View.
"""
import customtkinter as ctk
from src.gui.components.search_bar import SearchBar
from src.gui.components.modal_dialog import CustomerDialog, ConfirmDialog
from src.config import (
    COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_DANGER,
    CARD_DARK, CARD_LIGHT
)


class CustomersView(ctk.CTkFrame):
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
            text="Customer Directory",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold")
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_frame,
            text="Save, manage, and reuse customer profiles for faster GST invoicing.",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=("gray45", "#94A3B8")
        ).pack(anchor="w")

        ctk.CTkButton(
            hdr,
            text="+ Add Customer",
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
            placeholder="Search by customer name, phone, email, GSTIN...",
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
        self.th_frame.grid_columnconfigure(0, weight=3)  # Name
        self.th_frame.grid_columnconfigure(1, weight=3)  # GSTIN / PAN / State
        self.th_frame.grid_columnconfigure(2, weight=3)  # Contact
        self.th_frame.grid_columnconfigure(3, weight=2)  # Actions

        ctk.CTkLabel(self.th_frame, text="CUSTOMER NAME", font=ctk.CTkFont(size=11, weight="bold"), anchor="w").grid(row=0, column=0, padx=10, pady=8, sticky="w")
        ctk.CTkLabel(self.th_frame, text="GSTIN / PAN / STATE", font=ctk.CTkFont(size=11, weight="bold"), anchor="w").grid(row=0, column=1, padx=10, pady=8, sticky="w")
        ctk.CTkLabel(self.th_frame, text="CONTACT DETAILS", font=ctk.CTkFont(size=11, weight="bold"), anchor="w").grid(row=0, column=2, padx=10, pady=8, sticky="w")
        ctk.CTkLabel(self.th_frame, text="ACTIONS", font=ctk.CTkFont(size=11, weight="bold"), anchor="center").grid(row=0, column=3, padx=10, pady=8, sticky="ew")

        self.rows_scroll = ctk.CTkScrollableFrame(self.list_card, fg_color="transparent")
        self.rows_scroll.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def refresh(self, query: str = ""):
        for w in self.rows_scroll.winfo_children():
            w.destroy()

        customers = self.app.customer_repo.get_all(search_query=query)

        if not customers:
            ctk.CTkLabel(
                self.rows_scroll,
                text="No customers found.",
                font=ctk.CTkFont(size=13),
                text_color=("gray45", "#64748B")
            ).pack(pady=40)
            return

        for idx, cust in enumerate(customers):
            row_frame = ctk.CTkFrame(
                self.rows_scroll,
                fg_color=("white", "#1E293B" if idx % 2 == 0 else "#243048"),
                corner_radius=6,
                height=52
            )
            row_frame.pack(fill="x", pady=2)
            row_frame.grid_columnconfigure(0, weight=3)
            row_frame.grid_columnconfigure(1, weight=3)
            row_frame.grid_columnconfigure(2, weight=3)
            row_frame.grid_columnconfigure(3, weight=2)

            # Name & Address
            c_name_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            c_name_frame.grid(row=0, column=0, padx=10, pady=6, sticky="w")
            ctk.CTkLabel(c_name_frame, text=cust["name"], font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(anchor="w")
            if cust.get("address"):
                ctk.CTkLabel(c_name_frame, text=cust["address"][:35] + ("..." if len(cust["address"]) > 35 else ""), font=ctk.CTkFont(size=10), text_color=("gray45", "#94A3B8"), anchor="w").pack(anchor="w")

            # Tax Info
            c_tax_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            c_tax_frame.grid(row=0, column=1, padx=10, pady=6, sticky="w")
            gst_str = f"GSTIN: {cust.get('gstin') or 'Unregistered'}"
            ctk.CTkLabel(c_tax_frame, text=gst_str, font=ctk.CTkFont(size=11), anchor="w").pack(anchor="w")
            pan_state = []
            if cust.get("pan"):
                pan_state.append(f"PAN: {cust['pan']}")
            if cust.get("state_code"):
                pan_state.append(f"State: {cust['state_code']}")
            if pan_state:
                ctk.CTkLabel(c_tax_frame, text=" | ".join(pan_state), font=ctk.CTkFont(size=10), text_color=("gray45", "#94A3B8"), anchor="w").pack(anchor="w")

            # Contact Info
            c_contact_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            c_contact_frame.grid(row=0, column=2, padx=10, pady=6, sticky="w")
            if cust.get("phone"):
                ctk.CTkLabel(c_contact_frame, text=f"📞 {cust['phone']}", font=ctk.CTkFont(size=11), anchor="w").pack(anchor="w")
            if cust.get("email"):
                ctk.CTkLabel(c_contact_frame, text=f"✉ {cust['email']}", font=ctk.CTkFont(size=10), text_color=("gray45", "#94A3B8"), anchor="w").pack(anchor="w")

            # Actions
            act_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            act_frame.grid(row=0, column=3, padx=10, pady=6, sticky="e")

            ctk.CTkButton(
                act_frame,
                text="Edit",
                width=55,
                height=28,
                font=ctk.CTkFont(size=11),
                fg_color=("gray85", "#334155"),
                text_color=("black", "white"),
                hover_color=COLOR_PRIMARY,
                command=lambda c=cust: self.open_edit_dialog(c)
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
                command=lambda c=cust: self._delete_customer(c)
            ).pack(side="left", padx=2)

    def open_add_dialog(self):
        def _on_save(data):
            self.app.customer_repo.add(data)
            self.refresh()
            self.app.new_invoice_view.refresh_catalogs()

        CustomerDialog(self, on_save=_on_save)

    def open_edit_dialog(self, customer: Dict[str, Any]):
        def _on_save(data):
            self.app.customer_repo.update(customer["id"], data)
            self.refresh()
            self.app.new_invoice_view.refresh_catalogs()

        CustomerDialog(self, customer_data=customer, on_save=_on_save)

    def _delete_customer(self, customer: Dict[str, Any]):
        def _confirm():
            self.app.customer_repo.delete(customer["id"])
            self.refresh()
            self.app.new_invoice_view.refresh_catalogs()

        ConfirmDialog(
            self,
            title="Delete Customer",
            message=f"Are you sure you want to delete '{customer['name']}'?",
            on_confirm=_confirm,
            confirm_text="Delete",
            is_danger=True
        )
