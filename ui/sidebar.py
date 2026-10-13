import customtkinter as ctk
from ui.theme import Theme
from ui.components.badge import StatusBadge
from ui.components.notification import ConfirmDialog
from utils.icon_factory import IconFactory


class Sidebar(ctk.CTkFrame):
    """
    Fixed left navigation sidebar with logo header, styled navigation items,
    active indicators, user profile summary, and logout trigger.
    """

    NAV_ITEMS = [
        {"id": "dashboard", "label": "Dashboard", "icon": "dashboard"},
        {"id": "books", "label": "Books Catalog", "icon": "books"},
        {"id": "members", "label": "Members", "icon": "members"},
        {"id": "circulation", "label": "Circulation", "icon": "circulation"},
        {"id": "fines", "label": "Fines & Payments", "icon": "fines"},
        {"id": "reports", "label": "Reports & Analytics", "icon": "reports"},
        {"id": "settings", "label": "Settings", "icon": "settings"},
    ]

    def __init__(self, master, current_user, on_navigate, on_logout, **kwargs):
        super().__init__(
            master,
            width=240,
            fg_color=Theme.BG_SIDEBAR,
            corner_radius=0,
            **kwargs,
        )
        self.pack_propagate(False)
        self.current_user = current_user
        self.on_navigate = on_navigate
        self.on_logout = on_logout
        self.active_id = "dashboard"
        self.buttons = {}

        self._render_view()

    def _render_view(self):
        # 1. Brand Logo Header
        logo_box = ctk.CTkFrame(self, fg_color="transparent")
        logo_box.pack(fill="x", padx=20, pady=(24, 28))

        brand_row = ctk.CTkFrame(logo_box, fg_color="transparent")
        brand_row.pack(fill="x")

        # Book icon inside teal square
        icon_wrapper = ctk.CTkFrame(brand_row, fg_color=Theme.PRIMARY, width=38, height=38, corner_radius=10)
        icon_wrapper.pack(side="left")
        icon_wrapper.pack_propagate(False)

        lib_icon = IconFactory.get_icon("books", size=(20, 20), color_light="#ffffff", color_dark="#ffffff")
        icon_lbl = ctk.CTkLabel(icon_wrapper, text="", image=lib_icon)
        icon_lbl.place(relx=0.5, rely=0.5, anchor="center")

        text_col = ctk.CTkFrame(brand_row, fg_color="transparent")
        text_col.pack(side="left", padx=(12, 0))

        title_lbl = ctk.CTkLabel(
            text_col,
            text="ALEXANDRIA",
            font=("Segoe UI", 14, "bold"),
            text_color="#ffffff",
        )
        title_lbl.pack(anchor="w")

        sub_lbl = ctk.CTkLabel(
            text_col,
            text="Library System 2.0",
            font=("Segoe UI", 10),
            text_color="#94a3b8",
        )
        sub_lbl.pack(anchor="w")

        # 2. Navigation items
        nav_container = ctk.CTkFrame(self, fg_color="transparent")
        nav_container.pack(fill="x", padx=12, pady=0)

        for item in self.NAV_ITEMS:
            btn_frame = ctk.CTkFrame(nav_container, fg_color="transparent", corner_radius=8, height=44)
            btn_frame.pack(fill="x", pady=2)
            btn_frame.pack_propagate(False)

            icon_img = IconFactory.get_icon(item["icon"], size=(18, 18), color_light="#94a3b8", color_dark="#94a3b8")

            btn = ctk.CTkButton(
                btn_frame,
                text=f"   {item['label']}",
                image=icon_img,
                compound="left",
                font=("Segoe UI", 12, "bold"),
                fg_color="transparent",
                hover_color="#1e293b",
                text_color="#94a3b8",
                anchor="w",
                corner_radius=8,
                command=lambda page_id=item["id"]: self._select_page(page_id),
            )
            btn.pack(fill="both", expand=True)
            self.buttons[item["id"]] = (btn, btn_frame)

        # 3. User Profile Card & Logout at bottom
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.pack(side="bottom", fill="x", padx=16, pady=20)

        user_card = ctk.CTkFrame(bottom_frame, fg_color="#1e293b", corner_radius=10)
        user_card.pack(fill="x", pady=(0, 10))

        u_info = ctk.CTkFrame(user_card, fg_color="transparent")
        u_info.pack(fill="x", padx=12, pady=10)

        # Avatar circle
        av_img = IconFactory.get_icon("members", size=(16, 16), color_light="#14b8a6", color_dark="#14b8a6")
        av_lbl = ctk.CTkLabel(u_info, text="", image=av_img)
        av_lbl.pack(side="left", padx=(0, 8))

        u_details = ctk.CTkFrame(u_info, fg_color="transparent")
        u_details.pack(side="left")

        u_name = ctk.CTkLabel(
            u_details,
            text=self.current_user.full_name[:16],
            font=("Segoe UI", 11, "bold"),
            text_color="#f8fafc",
        )
        u_name.pack(anchor="w")

        u_role = ctk.CTkLabel(
            u_details,
            text=self.current_user.role.upper(),
            font=("Segoe UI", 9, "bold"),
            text_color="#14b8a6",
        )
        u_role.pack(anchor="w")

        # Logout button
        logout_icon = IconFactory.get_icon("logout", size=(16, 16), color_light="#f87171", color_dark="#f87171")
        logout_btn = ctk.CTkButton(
            bottom_frame,
            text="  Sign Out",
            image=logout_icon,
            compound="left",
            font=("Segoe UI", 11, "bold"),
            fg_color="#334155",
            hover_color="#475569",
            text_color="#ffffff",
            height=34,
            corner_radius=8,
            command=self._handle_logout,
        )
        logout_btn.pack(fill="x")

        self.set_active("dashboard")

    def _select_page(self, page_id: str):
        self.set_active(page_id)
        if self.on_navigate:
            self.on_navigate(page_id)

    def set_active(self, page_id: str):
        self.active_id = page_id
        for pid, (btn, frame) in self.buttons.items():
            if pid == page_id:
                btn.configure(
                    fg_color=Theme.PRIMARY,
                    text_color="#ffffff",
                    hover_color=Theme.PRIMARY_HOVER,
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color="#94a3b8",
                    hover_color="#1e293b",
                )

    def _handle_logout(self):
        ConfirmDialog(
            self.winfo_toplevel(),
            title="Confirm Sign Out",
            message="Are you sure you want to sign out of the application?",
            on_confirm=self.on_logout,
            confirm_text="Sign Out",
            danger=False,
        )
