"""
Modern Modal Dialogs for entity creation/editing and confirmation alerts.
"""
import customtkinter as ctk
from typing import Dict, Any, Callable, Optional
from src.config import COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_DANGER, COLOR_SUCCESS


class ModalDialog(ctk.CTkToplevel):
    def __init__(self, parent, title: str, width: int = 480, height: int = 520):
        super().__init__(parent)
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        # Center on parent
        self.update_idletasks()
        try:
            x = parent.winfo_x() + (parent.winfo_width() - width) // 2
            y = parent.winfo_y() + (parent.winfo_height() - height) // 2
            self.geometry(f"+{max(0, x)}+{max(0, y)}")
        except Exception:
            pass


class CustomerDialog(ModalDialog):
    def __init__(self, parent, customer_data: Optional[Dict[str, Any]] = None, on_save: Optional[Callable] = None):
        super().__init__(parent, "Edit Customer" if customer_data else "Add New Customer", width=520, height=620)
        self.customer_data = customer_data or {}
        self.on_save = on_save

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=15)

        # Title
        ctk.CTkLabel(
            self.scroll_frame,
            text="Customer Profile" if not customer_data else f"Edit {customer_data.get('name', 'Customer')}",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
        ).pack(anchor="w", pady=(0, 15))

        # Fields
        self.entries = {}
        fields = [
            ("name", "Company / Customer Name *", self.customer_data.get("name", "")),
            ("phone", "Phone Number", self.customer_data.get("phone", "")),
            ("email", "Email Address", self.customer_data.get("email", "")),
            ("gstin", "GSTIN Number", self.customer_data.get("gstin", "")),
            ("pan", "PAN Number", self.customer_data.get("pan", "")),
            ("state_code", "State Code (e.g. 33)", self.customer_data.get("state_code", "")),
            ("address", "Billing Address", self.customer_data.get("address", "")),
            ("shipping_address", "Shipping Address (if different)", self.customer_data.get("shipping_address", ""))
        ]

        for field_id, label, default_val in fields:
            lbl = ctk.CTkLabel(self.scroll_frame, text=label, font=ctk.CTkFont(size=12, weight="bold"), anchor="w")
            lbl.pack(fill="x", pady=(6, 2))
            
            if field_id in ("address", "shipping_address"):
                txt = ctk.CTkTextbox(self.scroll_frame, height=60, corner_radius=8)
                txt.insert("1.0", default_val or "")
                txt.pack(fill="x", pady=(0, 6))
                self.entries[field_id] = txt
            else:
                entry = ctk.CTkEntry(self.scroll_frame, corner_radius=8, height=36)
                entry.insert(0, default_val or "")
                entry.pack(fill="x", pady=(0, 6))
                self.entries[field_id] = entry

        # Error label
        self.err_label = ctk.CTkLabel(self.scroll_frame, text="", text_color=COLOR_DANGER, font=ctk.CTkFont(size=11))
        self.err_label.pack(fill="x", pady=(4, 8))

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 15))

        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            fg_color=("gray75", "#334155"),
            text_color=("black", "white"),
            width=100,
            command=self.destroy
        ).pack(side="left")

        ctk.CTkButton(
            btn_frame,
            text="Save Customer",
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            width=140,
            command=self._handle_save
        ).pack(side="right")

    def _handle_save(self):
        data = {}
        for field_id, widget in self.entries.items():
            if isinstance(widget, ctk.CTkTextbox):
                data[field_id] = widget.get("1.0", "end-1c").strip()
            else:
                data[field_id] = widget.get().strip()

        if not data.get("name"):
            self.err_label.configure(text="Customer Name is required.")
            return

        if self.on_save:
            self.on_save(data)
        self.destroy()


class ProductDialog(ModalDialog):
    def __init__(self, parent, product_data: Optional[Dict[str, Any]] = None, on_save: Optional[Callable] = None):
        super().__init__(parent, "Edit Product/Service" if product_data else "Add Product / Service", width=480, height=520)
        self.product_data = product_data or {}
        self.on_save = on_save

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=15)

        # Title
        ctk.CTkLabel(
            self.scroll_frame,
            text="Product / Service Details",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
        ).pack(anchor="w", pady=(0, 15))

        self.entries = {}
        fields = [
            ("name", "Product / Service Name *", self.product_data.get("name", "")),
            ("description", "Description of Goods", self.product_data.get("description", "")),
            ("hsn_code", "HSN / SAC Code", self.product_data.get("hsn_code", "")),
            ("unit", "Unit of Measure (e.g. NOS, SET, KG)", self.product_data.get("unit", "NOS")),
            ("default_rate", "Default Rate (Rs.)", str(self.product_data.get("default_rate", 0.0))),
            ("tax_rate", "GST Tax Rate (%)", str(self.product_data.get("tax_rate", 18.0)))
        ]

        for field_id, label, default_val in fields:
            lbl = ctk.CTkLabel(self.scroll_frame, text=label, font=ctk.CTkFont(size=12, weight="bold"), anchor="w")
            lbl.pack(fill="x", pady=(6, 2))

            if field_id == "description":
                txt = ctk.CTkTextbox(self.scroll_frame, height=55, corner_radius=8)
                txt.insert("1.0", default_val or "")
                txt.pack(fill="x", pady=(0, 6))
                self.entries[field_id] = txt
            else:
                entry = ctk.CTkEntry(self.scroll_frame, corner_radius=8, height=36)
                entry.insert(0, str(default_val) if default_val is not None else "")
                entry.pack(fill="x", pady=(0, 6))
                self.entries[field_id] = entry

        # Error label
        self.err_label = ctk.CTkLabel(self.scroll_frame, text="", text_color=COLOR_DANGER, font=ctk.CTkFont(size=11))
        self.err_label.pack(fill="x", pady=(4, 8))

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 15))

        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            fg_color=("gray75", "#334155"),
            text_color=("black", "white"),
            width=100,
            command=self.destroy
        ).pack(side="left")

        ctk.CTkButton(
            btn_frame,
            text="Save Item",
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            width=140,
            command=self._handle_save
        ).pack(side="right")

    def _handle_save(self):
        data = {}
        for field_id, widget in self.entries.items():
            if isinstance(widget, ctk.CTkTextbox):
                data[field_id] = widget.get("1.0", "end-1c").strip()
            else:
                data[field_id] = widget.get().strip()

        if not data.get("name"):
            self.err_label.configure(text="Item Name is required.")
            return

        try:
            data["default_rate"] = float(data.get("default_rate") or 0.0)
            data["tax_rate"] = float(data.get("tax_rate") or 18.0)
        except ValueError:
            self.err_label.configure(text="Rate and Tax Rate must be numeric.")
            return

        if self.on_save:
            self.on_save(data)
        self.destroy()


class ConfirmDialog(ModalDialog):
    def __init__(self, parent, title: str, message: str, on_confirm: Callable, confirm_text: str = "Confirm", is_danger: bool = False):
        super().__init__(parent, title, width=420, height=200)
        self.on_confirm = on_confirm

        ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold")
        ).pack(anchor="w", padx=24, pady=(20, 8))

        ctk.CTkLabel(
            self,
            text=message,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            wraplength=370,
            justify="left"
        ).pack(anchor="w", padx=24, pady=(0, 20))

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=24, pady=(0, 20))

        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            fg_color=("gray75", "#334155"),
            text_color=("black", "white"),
            width=90,
            command=self.destroy
        ).pack(side="left")

        ctk.CTkButton(
            btn_frame,
            text=confirm_text,
            fg_color=COLOR_DANGER if is_danger else COLOR_PRIMARY,
            hover_color="#DC2626" if is_danger else COLOR_PRIMARY_HOVER,
            width=120,
            command=self._confirm
        ).pack(side="right")

    def _confirm(self):
        self.destroy()
        if self.on_confirm:
            self.on_confirm()
