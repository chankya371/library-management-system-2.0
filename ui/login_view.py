import customtkinter as ctk
from ui.theme import Theme
from utils.icon_factory import IconFactory
from services.auth_service import AuthService


class LoginView(ctk.CTkFrame):
    """
    Sleek, centered login portal frame that fits cleanly inside the main window.
    """

    def __init__(self, master, on_login_success, **kwargs):
        super().__init__(master, fg_color=Theme.BG_MAIN, corner_radius=0, **kwargs)
        self.on_login_success = on_login_success
        self.show_password = False

        self._render_view()

    def _render_view(self):
        # Center container
        center_box = ctk.CTkFrame(
            self,
            fg_color=Theme.BG_CARD,
            border_color=Theme.BORDER,
            border_width=1,
            corner_radius=16,
            width=460,
        )
        center_box.place(relx=0.5, rely=0.5, anchor="center")

        inner = ctk.CTkFrame(center_box, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=32, pady=32)

        # 1. Header with Logo & Brand
        icon_box = ctk.CTkFrame(inner, fg_color=Theme.PRIMARY, width=54, height=54, corner_radius=14)
        icon_box.pack(pady=(4, 14))
        icon_box.pack_propagate(False)

        lib_icon = IconFactory.get_icon("books", size=(28, 28), color_light="#ffffff", color_dark="#ffffff")
        icon_lbl = ctk.CTkLabel(icon_box, text="", image=lib_icon)
        icon_lbl.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            inner,
            text="Alexandria Library",
            font=("Segoe UI", 22, "bold"),
            text_color=Theme.TEXT_PRIMARY,
        ).pack()

        ctk.CTkLabel(
            inner,
            text="Staff circulation & administration portal",
            font=Theme.FONT_BODY,
            text_color=Theme.TEXT_SECONDARY,
        ).pack(pady=(4, 20))

        # 2. Form Inputs
        ctk.CTkLabel(
            inner,
            text="Username",
            font=Theme.FONT_BODY_BOLD,
            text_color=Theme.TEXT_SECONDARY,
        ).pack(anchor="w", pady=(0, 4))

        self.user_entry = ctk.CTkEntry(
            inner,
            placeholder_text="Enter your username",
            fg_color=Theme.BG_INPUT,
            height=40,
            font=Theme.FONT_BODY,
        )
        self.user_entry.pack(fill="x", pady=(0, 14))
        self.user_entry.insert(0, "admin")

        ctk.CTkLabel(
            inner,
            text="Password",
            font=Theme.FONT_BODY_BOLD,
            text_color=Theme.TEXT_SECONDARY,
        ).pack(anchor="w", pady=(0, 4))

        pw_row = ctk.CTkFrame(inner, fg_color="transparent")
        pw_row.pack(fill="x", pady=(0, 8))

        self.pw_entry = ctk.CTkEntry(
            pw_row,
            placeholder_text="Enter your password",
            show="•",
            fg_color=Theme.BG_INPUT,
            height=40,
            font=Theme.FONT_BODY,
        )
        self.pw_entry.pack(side="left", fill="x", expand=True)
        self.pw_entry.insert(0, "admin123")
        self.pw_entry.bind("<Return>", lambda e: self._attempt_login())

        self.toggle_pw_btn = ctk.CTkButton(
            pw_row,
            text="👁",
            font=("Segoe UI", 13),
            fg_color=Theme.SECONDARY,
            hover_color=Theme.SECONDARY_HOVER,
            text_color=Theme.SECONDARY_TEXT,
            width=40,
            height=40,
            corner_radius=8,
            command=self._toggle_password_visibility,
        )
        self.toggle_pw_btn.pack(side="right", padx=(6, 0))

        # Error notification label
        self.error_lbl = ctk.CTkLabel(
            inner,
            text="",
            font=Theme.FONT_CAPTION_BOLD,
            text_color=Theme.DANGER,
        )
        self.error_lbl.pack(pady=(0, 10))

        # Sign In Button
        login_btn = ctk.CTkButton(
            inner,
            text="Sign In to Portal",
            font=("Segoe UI", 13, "bold"),
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            text_color=Theme.TEXT_WHITE,
            height=42,
            corner_radius=8,
            command=self._attempt_login,
        )
        login_btn.pack(fill="x", pady=(0, 18))

        # 3. Demo Credentials Hint Card
        demo_card = ctk.CTkFrame(inner, fg_color=Theme.BG_INPUT, corner_radius=10)
        demo_card.pack(fill="x")

        hint_box = ctk.CTkFrame(demo_card, fg_color="transparent")
        hint_box.pack(padx=14, pady=10)

        ctk.CTkLabel(
            hint_box,
            text="💡 Demo Accounts:",
            font=Theme.FONT_CAPTION_BOLD,
            text_color=Theme.TEXT_PRIMARY,
        ).pack(anchor="w")

        ctk.CTkLabel(
            hint_box,
            text="• Admin: admin / admin123\n• Librarian: librarian / lib123",
            font=Theme.FONT_CAPTION,
            text_color=Theme.TEXT_SECONDARY,
            justify="left",
        ).pack(anchor="w", pady=(2, 0))

    def _toggle_password_visibility(self):
        self.show_password = not self.show_password
        if self.show_password:
            self.pw_entry.configure(show="")
            self.toggle_pw_btn.configure(text="🔒")
        else:
            self.pw_entry.configure(show="•")
            self.toggle_pw_btn.configure(text="👁")

    def _attempt_login(self):
        username = self.user_entry.get().strip()
        password = self.pw_entry.get().strip()

        if not username or not password:
            self.error_lbl.configure(text="Please enter both username and password.")
            return

        user = AuthService.authenticate(username, password)
        if user:
            self.error_lbl.configure(text="")
            self.on_login_success(user)
        else:
            self.error_lbl.configure(text="Invalid credentials. Please try again.")
