import customtkinter as ctk
from typing import List, Dict, Any, Callable, Optional
from ui.theme import Theme
from utils.icon_factory import IconFactory


class ModernTable(ctk.CTkFrame):
    """
    Sleek, responsive data table with sticky header, clean rows,
    hover highlights, empty-state placeholder, and custom cell renderers.
    """

    def __init__(
        self,
        master,
        columns: List[Dict[str, Any]],  # [{"key": "id", "label": "ID", "width": 60, "anchor": "center"}, ...]
        empty_message: str = "No records found.",
        **kwargs,
    ):
        super().__init__(
            master,
            fg_color=Theme.BG_CARD,
            border_color=Theme.BORDER,
            border_width=1,
            corner_radius=Theme.RADIUS_CARD,
            **kwargs,
        )

        self.columns = columns
        self.empty_message = empty_message
        self.rows_data = []

        # Table Header
        self.header_frame = ctk.CTkFrame(self, fg_color=Theme.SECONDARY, corner_radius=0, height=42)
        self.header_frame.pack(fill="x", side="top")
        self.header_frame.pack_propagate(False)

        for col in self.columns:
            w = col.get("width", 100)
            anchor = col.get("anchor", "w")
            lbl = ctk.CTkLabel(
                self.header_frame,
                text=col["label"],
                font=Theme.FONT_BODY_BOLD,
                text_color=Theme.TEXT_SECONDARY,
                width=w,
                anchor=anchor,
            )
            lbl.pack(side="left", padx=8, pady=8)

        # Scrollable rows container
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
        )
        self.scroll_frame.pack(fill="both", expand=True, side="top")

        # Empty state container
        self.empty_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")

    def set_data(self, data: List[Dict[str, Any]], render_actions: Optional[Callable] = None):
        """Populates the table with data rows."""
        self.rows_data = data

        # Clear existing rows
        for child in self.scroll_frame.winfo_children():
            child.destroy()

        if not data:
            self._render_empty_state()
            return

        for idx, row in enumerate(data):
            self._render_row(idx, row, render_actions)

    def _render_empty_state(self):
        empty_box = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        empty_box.pack(fill="both", expand=True, pady=60)

        icon_img = IconFactory.get_icon("search", size=(36, 36), color_light="#94a3b8", color_dark="#64748b")
        icon_lbl = ctk.CTkLabel(empty_box, text="", image=icon_img)
        icon_lbl.pack(pady=(0, 10))

        lbl = ctk.CTkLabel(
            empty_box,
            text=self.empty_message,
            font=Theme.FONT_SUBTITLE,
            text_color=Theme.TEXT_MUTED,
        )
        lbl.pack()

    def _render_row(self, idx: int, row_data: Dict[str, Any], render_actions: Optional[Callable]):
        row_bg = "transparent" if idx % 2 == 0 else Theme.BG_CARD_HOVER
        row_frame = ctk.CTkFrame(self.scroll_frame, fg_color=row_bg, corner_radius=6, height=44)
        row_frame.pack(fill="x", pady=2, padx=4)
        row_frame.pack_propagate(False)

        for col in self.columns:
            key = col["key"]
            w = col.get("width", 100)
            anchor = col.get("anchor", "w")

            if key == "_actions" and render_actions:
                action_box = ctk.CTkFrame(row_frame, fg_color="transparent", width=w)
                action_box.pack(side="left", padx=8, pady=4)
                render_actions(action_box, row_data)
            elif col.get("renderer"):
                # Custom renderer callback
                cell_box = ctk.CTkFrame(row_frame, fg_color="transparent", width=w)
                cell_box.pack(side="left", padx=8, pady=4)
                col["renderer"](cell_box, row_data.get(key, ""))
            else:
                val = str(row_data.get(key, ""))
                lbl = ctk.CTkLabel(
                    row_frame,
                    text=val,
                    font=Theme.FONT_BODY,
                    text_color=Theme.TEXT_PRIMARY,
                    width=w,
                    anchor=anchor,
                )
                lbl.pack(side="left", padx=8, pady=6)
