import customtkinter as ctk
from ui.theme import Theme
from ui.components.badge import StatusBadge
from ui.components.table import ModernTable
from ui.components.notification import ConfirmDialog, AlertDialog
from ui.components.modals import MemberFormModal, MemberProfileModal, IssueBookModal
from utils.icon_factory import IconFactory
from services.member_service import MemberService


class MembersPage(ctk.CTkFrame):
    """
    Member patron management screen for registration, profile inspection,
    status updating, and borrowing history tracking.
    """

    def __init__(self, master, current_user, on_navigate, **kwargs):
        super().__init__(master, fg_color="transparent", corner_radius=0, **kwargs)
        self.current_user = current_user
        self.on_navigate = on_navigate

        self._render_view()

    def _render_view(self):
        # 1. Controls Bar
        ctrl_frame = ctk.CTkFrame(self, fg_color=Theme.BG_CARD, border_color=Theme.BORDER, border_width=1, corner_radius=Theme.RADIUS_CARD)
        ctrl_frame.pack(fill="x", padx=16, pady=(16, 12))

        box = ctk.CTkFrame(ctrl_frame, fg_color="transparent")
        box.pack(fill="x", padx=16, pady=12)

        # Search
        self.search_entry = ctk.CTkEntry(
            box,
            placeholder_text="Search by name, email, phone, or member ID...",
            fg_color=Theme.BG_INPUT,
            height=36,
            width=300,
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_members())

        # Type Filter
        types = ["All", "Student", "Faculty", "Standard", "Premium"]
        self.type_menu = ctk.CTkComboBox(
            box,
            values=types,
            height=36,
            width=130,
            fg_color=Theme.BG_INPUT,
            command=lambda _: self.load_members(),
        )
        self.type_menu.set("All")
        self.type_menu.pack(side="left", padx=(0, 10))

        # Status Filter
        statuses = ["All", "Active", "Inactive", "Suspended"]
        self.status_menu = ctk.CTkComboBox(
            box,
            values=statuses,
            height=36,
            width=120,
            fg_color=Theme.BG_INPUT,
            command=lambda _: self.load_members(),
        )
        self.status_menu.set("All")
        self.status_menu.pack(side="left", padx=(0, 10))

        # Reset button
        reset_btn = ctk.CTkButton(
            box,
            text="Reset",
            fg_color=Theme.SECONDARY,
            hover_color=Theme.SECONDARY_HOVER,
            text_color=Theme.SECONDARY_TEXT,
            height=36,
            width=70,
            command=self._reset_filters,
        )
        reset_btn.pack(side="left")

        # Register Member Button
        reg_btn = ctk.CTkButton(
            box,
            text="+ Register Member",
            font=Theme.FONT_BODY_BOLD,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            text_color=Theme.TEXT_WHITE,
            height=36,
            corner_radius=8,
            command=lambda: MemberFormModal(self.winfo_toplevel(), on_success=self.load_members),
        )
        reg_btn.pack(side="right")

        # 2. Members Table
        columns = [
            {"key": "code", "label": "Member ID", "width": 110, "anchor": "w"},
            {"key": "name", "label": "Full Name", "width": 200, "anchor": "w"},
            {"key": "email", "label": "Email Address", "width": 220, "anchor": "w"},
            {"key": "phone", "label": "Phone Number", "width": 140, "anchor": "w"},
            {"key": "type", "label": "Type", "width": 100, "anchor": "center"},
            {"key": "status", "label": "Status", "width": 100, "anchor": "center", "renderer": self._render_status_badge},
            {"key": "_actions", "label": "Actions", "width": 210, "anchor": "center"},
        ]

        self.table = ModernTable(self, columns=columns, empty_message="No members found matching criteria.")
        self.table.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        self.load_members()

    def _render_status_badge(self, container, value):
        StatusBadge(container, text=value).pack(anchor="center")

    def _reset_filters(self):
        self.search_entry.delete(0, "end")
        self.type_menu.set("All")
        self.status_menu.set("All")
        self.load_members()

    def load_members(self):
        q = self.search_entry.get().strip()
        m_type = self.type_menu.get()
        status = self.status_menu.get()

        members = MemberService.search_members(
            query=q,
            membership_type=m_type,
            status=status,
        )

        rows = []
        for m in members:
            rows.append({
                "id": m.id,
                "code": m.member_code,
                "name": m.full_name,
                "email": m.email,
                "phone": m.phone,
                "type": m.membership_type,
                "status": m.status,
                "raw_member": m,
            })

        self.table.set_data(rows, render_actions=self._render_row_actions)

    def _render_row_actions(self, container, row_data):
        raw_m = row_data["raw_member"]

        # Profile button
        view_btn = ctk.CTkButton(
            container,
            text="Profile",
            font=Theme.FONT_CAPTION_BOLD,
            fg_color=Theme.SECONDARY,
            hover_color=Theme.SECONDARY_HOVER,
            text_color=Theme.SECONDARY_TEXT,
            width=50,
            height=26,
            corner_radius=6,
            command=lambda: MemberProfileModal(self.winfo_toplevel(), member_id=raw_m.id),
        )
        view_btn.pack(side="left", padx=2)

        # Issue shortcut (if active)
        if raw_m.status == "Active":
            loan_btn = ctk.CTkButton(
                container,
                text="Loan",
                font=Theme.FONT_CAPTION_BOLD,
                fg_color=Theme.INFO,
                hover_color=Theme.PRIMARY_HOVER,
                text_color=Theme.TEXT_WHITE,
                width=46,
                height=26,
                corner_radius=6,
                command=lambda: IssueBookModal(self.winfo_toplevel(), preselected_member_id=raw_m.id, on_success=self.load_members),
            )
            loan_btn.pack(side="left", padx=2)

        # Edit button
        edit_btn = ctk.CTkButton(
            container,
            text="Edit",
            font=Theme.FONT_CAPTION_BOLD,
            fg_color=Theme.SECONDARY,
            hover_color=Theme.SECONDARY_HOVER,
            text_color=Theme.SECONDARY_TEXT,
            width=46,
            height=26,
            corner_radius=6,
            command=lambda: MemberFormModal(self.winfo_toplevel(), member=raw_m, on_success=self.load_members),
        )
        edit_btn.pack(side="left", padx=2)

        # Delete button
        del_btn = ctk.CTkButton(
            container,
            text="Del",
            font=Theme.FONT_CAPTION_BOLD,
            fg_color=Theme.DANGER,
            hover_color=Theme.DANGER_HOVER,
            text_color=Theme.TEXT_WHITE,
            width=40,
            height=26,
            corner_radius=6,
            command=lambda: self._confirm_delete(raw_m),
        )
        del_btn.pack(side="left", padx=2)

    def _confirm_delete(self, member):
        def do_delete():
            ok, msg = MemberService.delete_member(member.id)
            if ok:
                AlertDialog(self.winfo_toplevel(), "Deleted", msg, level="success")
                self.load_members()
            else:
                AlertDialog(self.winfo_toplevel(), "Cannot Delete", msg, level="error")

        ConfirmDialog(
            self.winfo_toplevel(),
            title="Delete Member",
            message=f"Are you sure you want to delete member '{member.full_name}'?\n\nNote: Members with active loans or past records cannot be deleted.",
            on_confirm=do_delete,
            confirm_text="Delete Member",
            danger=True,
        )
