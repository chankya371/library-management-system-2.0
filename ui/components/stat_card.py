import customtkinter as ctk
from ui.theme import Theme
from utils.icon_factory import IconFactory


class StatCard(ctk.CTkFrame):
    """Modern SaaS-style summary metric card with icon container, title, large stat, and subtext."""

    def __init__(
        self,
        master,
        title: str,
        value: str,
        icon_name: str,
        subtext: str = "",
        accent_color: tuple = Theme.PRIMARY,
        icon_color: str = "#0d9488",
        **kwargs
    ):
        super().__init__(
            master,
            fg_color=Theme.BG_CARD,
            border_color=Theme.BORDER,
            border_width=1,
            corner_radius=Theme.RADIUS_CARD,
            **kwargs
        )

        # Header row: Icon pill + Title
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=16, pady=(16, 8))

        # Icon wrapper
        icon_wrapper = ctk.CTkFrame(
            header_frame,
            fg_color=accent_color,
            width=36,
            height=36,
            corner_radius=10,
        )
        icon_wrapper.pack(side="left")
        icon_wrapper.pack_propagate(False)

        icon_img = IconFactory.get_icon(icon_name, size=(18, 18), color_light="#ffffff", color_dark="#ffffff")
        icon_lbl = ctk.CTkLabel(icon_wrapper, text="", image=icon_img)
        icon_lbl.place(relx=0.5, rely=0.5, anchor="center")

        title_lbl = ctk.CTkLabel(
            header_frame,
            text=title,
            font=Theme.FONT_BODY_BOLD,
            text_color=Theme.TEXT_SECONDARY,
        )
        title_lbl.pack(side="left", padx=(10, 0))

        # Value label
        self.val_lbl = ctk.CTkLabel(
            self,
            text=str(value),
            font=Theme.FONT_STAT_VAL,
            text_color=Theme.TEXT_PRIMARY,
            anchor="w",
        )
        self.val_lbl.pack(fill="x", padx=16, pady=(0, 4))

        # Subtext
        if subtext:
            self.sub_lbl = ctk.CTkLabel(
                self,
                text=subtext,
                font=Theme.FONT_CAPTION,
                text_color=Theme.TEXT_MUTED,
                anchor="w",
            )
            self.sub_lbl.pack(fill="x", padx=16, pady=(0, 16))
        else:
            self.sub_lbl = None
            self.val_lbl.pack_configure(pady=(0, 16))

    def update_value(self, new_value: str, new_subtext: str = None):
        self.val_lbl.configure(text=str(new_value))
        if new_subtext and self.sub_lbl:
            self.sub_lbl.configure(text=new_subtext)
