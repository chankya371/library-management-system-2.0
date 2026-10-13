import datetime
import customtkinter as ctk
from ui.theme import Theme
from utils.icon_factory import IconFactory


class Topbar(ctk.CTkFrame):
    """
    Top application bar containing title breadcrumb, global search,
    real-time clock date display, and theme switcher.
    """

    def __init__(self, master, current_user, on_global_search=None, **kwargs):
        super().__init__(
            master,
            height=64,
            fg_color=Theme.BG_CARD,
            border_color=Theme.BORDER,
            border_width=1,
            corner_radius=0,
            **kwargs,
        )
        self.pack_propagate(False)
        self.current_user = current_user
        self.on_global_search = on_global_search

        self._render_view()

    def _render_view(self):
        wrapper = ctk.CTkFrame(self, fg_color="transparent")
        wrapper.pack(fill="both", expand=True, padx=20)

        # 1. Left: Dynamic Page Title
        title_box = ctk.CTkFrame(wrapper, fg_color="transparent")
        title_box.pack(side="left")

        self.title_lbl = ctk.CTkLabel(
            title_box,
            text="Dashboard",
            font=Theme.FONT_TITLE,
            text_color=Theme.TEXT_PRIMARY,
        )
        self.title_lbl.pack(anchor="w")

        # 2. Center: Global Search Input
        search_box = ctk.CTkFrame(wrapper, fg_color="transparent")
        search_box.pack(side="left", padx=(40, 0))

        self.global_search_entry = ctk.CTkEntry(
            search_box,
            placeholder_text="Quick lookup books, members, or loans...",
            fg_color=Theme.BG_INPUT,
            height=36,
            width=320,
        )
        self.global_search_entry.pack(side="left")
        self.global_search_entry.bind("<Return>", self._handle_search)

        search_btn = ctk.CTkButton(
            search_box,
            text="Go",
            font=Theme.FONT_BODY_BOLD,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            text_color=Theme.TEXT_WHITE,
            width=46,
            height=36,
            command=lambda: self._handle_search(None),
        )
        search_btn.pack(side="left", padx=(6, 0))

        # 3. Right: Date, Theme Toggle
        right_box = ctk.CTkFrame(wrapper, fg_color="transparent")
        right_box.pack(side="right")

        # Live Date
        today_str = datetime.date.today().strftime("%a, %b %d, %Y")
        date_lbl = ctk.CTkLabel(
            right_box,
            text=f"📅 {today_str}",
            font=Theme.FONT_BODY,
            text_color=Theme.TEXT_SECONDARY,
        )
        date_lbl.pack(side="left", padx=(0, 16))

        # Appearance mode toggle (Dark / Light)
        self.theme_btn = ctk.CTkButton(
            right_box,
            text="🌙 Theme",
            font=Theme.FONT_BODY_BOLD,
            fg_color=Theme.SECONDARY,
            hover_color=Theme.SECONDARY_HOVER,
            text_color=Theme.SECONDARY_TEXT,
            width=80,
            height=34,
            corner_radius=8,
            command=self._toggle_theme,
        )
        self.theme_btn.pack(side="left")

    def set_title(self, title: str):
        self.title_lbl.configure(text=title)

    def _handle_search(self, _event):
        q = self.global_search_entry.get().strip()
        if q and self.on_global_search:
            self.on_global_search(q)

    def _toggle_theme(self):
        curr = ctk.get_appearance_mode().lower()
        if curr == "dark":
            ctk.set_appearance_mode("Light")
            self.theme_btn.configure(text="☀️ Light")
        else:
            ctk.set_appearance_mode("Dark")
            self.theme_btn.configure(text="🌙 Dark")
