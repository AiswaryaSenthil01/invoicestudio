"""
Modern Dashboard Stat Card component.
"""
import customtkinter as ctk
from src.config import CARD_DARK, CARD_LIGHT, COLOR_PRIMARY, TEXT_LIGHT, TEXT_MUTED


class StatCard(ctk.CTkFrame):
    def __init__(
        self,
        master,
        title: str,
        value: str,
        subtitle: str = "",
        accent_color: str = COLOR_PRIMARY,
        icon_text: str = "",
        **kwargs
    ):
        super().__init__(
            master,
            corner_radius=12,
            fg_color=(CARD_LIGHT, CARD_DARK),
            border_width=1,
            border_color=("gray85", "#334155"),
            **kwargs
        )

        self.accent_color = accent_color
        self.grid_columnconfigure(0, weight=1)

        # Header Row: Title and Icon Badge
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=16, pady=(14, 6))

        self.title_label = ctk.CTkLabel(
            header_frame,
            text=title.upper(),
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=("gray50", "#94A3B8"),
            anchor="w"
        )
        self.title_label.pack(side="left")

        if icon_text:
            self.icon_badge = ctk.CTkLabel(
                header_frame,
                text=f" {icon_text} ",
                font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                fg_color=accent_color,
                text_color="white",
                corner_radius=6
            )
            self.icon_badge.pack(side="right")

        # Value Label
        self.value_label = ctk.CTkLabel(
            self,
            text=value,
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=("gray10", "#F8FAFC"),
            anchor="w"
        )
        self.value_label.pack(fill="x", padx=16, pady=(0, 4))

        # Subtitle Label
        if subtitle:
            self.sub_label = ctk.CTkLabel(
                self,
                text=subtitle,
                font=ctk.CTkFont(family="Segoe UI", size=11),
                text_color=("gray45", "#64748B"),
                anchor="w"
            )
            self.sub_label.pack(fill="x", padx=16, pady=(0, 14))

    def update_value(self, new_value: str, new_subtitle: str = None):
        """Update card value and subtitle dynamically."""
        self.value_label.configure(text=new_value)
        if new_subtitle is not None and hasattr(self, "sub_label"):
            self.sub_label.configure(text=new_subtitle)
