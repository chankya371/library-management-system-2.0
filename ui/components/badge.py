import customtkinter as ctk
from ui.theme import Theme


class StatusBadge(ctk.CTkFrame):
    """Clean, rounded status badge pill for tables and cards."""

    PRESETS = {
        "Available": (Theme.SUCCESS_BG, Theme.SUCCESS_TEXT),
        "Active": (Theme.SUCCESS_BG, Theme.SUCCESS_TEXT),
        "Returned": (Theme.SUCCESS_BG, Theme.SUCCESS_TEXT),
        "Paid": (Theme.SUCCESS_BG, Theme.SUCCESS_TEXT),
        "Low Stock": (Theme.WARNING_BG, Theme.WARNING_TEXT),
        "Issued": (Theme.INFO_BG, Theme.INFO_TEXT),
        "Pending": (Theme.WARNING_BG, Theme.WARNING_TEXT),
        "Overdue": (Theme.DANGER_BG, Theme.DANGER_TEXT),
        "Out of Stock": (Theme.DANGER_BG, Theme.DANGER_TEXT),
        "Inactive": (Theme.SECONDARY, Theme.TEXT_MUTED),
        "Suspended": (Theme.DANGER_BG, Theme.DANGER_TEXT),
    }

    def __init__(self, master, text: str, status_type: str = None, **kwargs):
        st = status_type or text
        bg_col, fg_col = self.PRESETS.get(st, (Theme.SECONDARY, Theme.TEXT_PRIMARY))

        super().__init__(
            master,
            fg_color=bg_col,
            corner_radius=Theme.RADIUS_BADGE,
            border_width=0,
            **kwargs,
        )

        self.label = ctk.CTkLabel(
            self,
            text=f"  {text}  ",
            font=Theme.FONT_CAPTION_BOLD,
            text_color=fg_col,
        )
        self.label.pack(padx=6, pady=2)
