"""
Debounced Search and Filter Bar Component.
"""
import customtkinter as ctk
from typing import List, Callable, Optional


class SearchBar(ctk.CTkFrame):
    def __init__(
        self,
        master,
        placeholder: str = "Search...",
        filters: Optional[List[str]] = None,
        filter_label: str = "Status",
        on_search: Optional[Callable[[str, str], None]] = None,
        **kwargs
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.on_search = on_search
        self._timer_id = None

        # Search Entry
        self.search_entry = ctk.CTkEntry(
            self,
            placeholder_text=placeholder,
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=12)
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self._on_key_release)

        # Clear Button
        self.clear_btn = ctk.CTkButton(
            self,
            text="Clear",
            width=60,
            height=36,
            corner_radius=8,
            fg_color=("gray80", "#334155"),
            text_color=("black", "white"),
            hover_color=("gray70", "#475569"),
            command=self.clear
        )
        self.clear_btn.pack(side="left", padx=(0, 10))

        # Optional Filter Dropdown
        self.filter_var = ctk.StringVar(value=filters[0] if filters else "All")
        if filters:
            ctk.CTkLabel(self, text=f"{filter_label}:", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=(5, 5))
            self.filter_menu = ctk.CTkOptionMenu(
                self,
                values=filters,
                variable=self.filter_var,
                command=self._on_filter_change,
                height=36,
                corner_radius=8
            )
            self.filter_menu.pack(side="left")

    def _on_key_release(self, event=None):
        if self._timer_id:
            self.after_cancel(self._timer_id)
        self._timer_id = self.after(250, self._trigger_callback)

    def _on_filter_change(self, choice):
        self._trigger_callback()

    def _trigger_callback(self):
        if self.on_search:
            query = self.search_entry.get().strip()
            selected_filter = self.filter_var.get()
            self.on_search(query, selected_filter)

    def clear(self):
        self.search_entry.delete(0, "end")
        if hasattr(self, "filter_menu"):
            self.filter_var.set(self.filter_menu.cget("values")[0])
        self._trigger_callback()
