import customtkinter as ctk
from ui.theme import Theme
from ui.components.badge import StatusBadge
from ui.components.table import ModernTable
from ui.components.notification import AlertDialog, ReceiptDialog
from ui.components.modals import IssueBookModal, ReturnBookModal
from utils.icon_factory import IconFactory
from utils.receipt_generator import ReceiptGenerator
from services.circulation_service import CirculationService
from services.settings_service import SettingsService


class CirculationPage(ctk.CTkFrame):
    """
    Circulation desk interface for checkouts, returns, loan tracking,
    and overdue monitoring.
    """

    def __init__(self, master, current_user, on_navigate, **kwargs):
        super().__init__(master, fg_color="transparent", corner_radius=0, **kwargs)
        self.current_user = current_user
        self.on_navigate = on_navigate

        self._render_view()

    def _render_view(self):
        # 1. Top Controls
        ctrl_frame = ctk.CTkFrame(self, fg_color=Theme.BG_CARD, border_color=Theme.BORDER, border_width=1, corner_radius=Theme.RADIUS_CARD)
        ctrl_frame.pack(fill="x", padx=16, pady=(16, 12))

        box = ctk.CTkFrame(ctrl_frame, fg_color="transparent")
        box.pack(fill="x", padx=16, pady=12)

        # Search
        self.search_entry = ctk.CTkEntry(
            box,
            placeholder_text="Search loans by title, borrower, ISBN, or loan #...",
            fg_color=Theme.BG_INPUT,
            height=36,
            width=320,
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_records())

        # Status Filter
        statuses = ["All", "Issued", "Overdue", "Returned"]
        self.status_menu = ctk.CTkComboBox(
            box,
            values=statuses,
            height=36,
            width=130,
            fg_color=Theme.BG_INPUT,
            command=lambda _: self.load_records(),
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

        # Checkout & Return Action Buttons
        ret_btn = ctk.CTkButton(
            box,
            text="Return Book",
            font=Theme.FONT_BODY_BOLD,
            fg_color=Theme.SECONDARY,
            hover_color=Theme.SECONDARY_HOVER,
            text_color=Theme.SECONDARY_TEXT,
            height=36,
            corner_radius=8,
            command=lambda: ReturnBookModal(self.winfo_toplevel(), on_success=self.load_records),
        )
        ret_btn.pack(side="right", padx=(8, 0))

        iss_btn = ctk.CTkButton(
            box,
            text="+ Issue Book",
            font=Theme.FONT_BODY_BOLD,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            text_color=Theme.TEXT_WHITE,
            height=36,
            corner_radius=8,
            command=lambda: IssueBookModal(self.winfo_toplevel(), on_success=self.load_records),
        )
        iss_btn.pack(side="right")

        # 2. Circulation Table
        columns = [
            {"key": "id_str", "label": "Loan #", "width": 80, "anchor": "center"},
            {"key": "book_title", "label": "Book Title", "width": 260, "anchor": "w"},
            {"key": "borrower", "label": "Borrower", "width": 190, "anchor": "w"},
            {"key": "issue_date", "label": "Issue Date", "width": 110, "anchor": "center"},
            {"key": "due_date", "label": "Due Date", "width": 110, "anchor": "center"},
            {"key": "status", "label": "Status", "width": 110, "anchor": "center", "renderer": self._render_status_badge},
            {"key": "_actions", "label": "Actions", "width": 180, "anchor": "center"},
        ]

        self.table = ModernTable(self, columns=columns, empty_message="No circulation records found matching criteria.")
        self.table.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        self.load_records()

    def _render_status_badge(self, container, value):
        StatusBadge(container, text=value).pack(anchor="center")

    def _reset_filters(self):
        self.search_entry.delete(0, "end")
        self.status_menu.set("All")
        self.load_records()

    def load_records(self):
        CirculationService.sync_overdue_statuses()
        q = self.search_entry.get().strip()
        status = self.status_menu.get()

        issues = CirculationService.search_issues(
            status=status,
            query=q,
        )

        rows = []
        for i in issues:
            rows.append({
                "id": i.id,
                "id_str": f"#{i.id}",
                "book_title": i.book_title,
                "borrower": f"{i.member_name} ({i.member_code})",
                "issue_date": i.issue_date,
                "due_date": i.due_date,
                "status": i.status,
                "raw_issue": i,
            })

        self.table.set_data(rows, render_actions=self._render_row_actions)

    def _render_row_actions(self, container, row_data):
        raw_i = row_data["raw_issue"]

        # If not yet returned, provide 1-click Return action
        if raw_i.status in ("Issued", "Overdue"):
            ret_btn = ctk.CTkButton(
                container,
                text="Return",
                font=Theme.FONT_CAPTION_BOLD,
                fg_color=Theme.PRIMARY,
                hover_color=Theme.PRIMARY_HOVER,
                text_color=Theme.TEXT_WHITE,
                width=56,
                height=26,
                corner_radius=6,
                command=lambda: ReturnBookModal(self.winfo_toplevel(), issue_record=raw_i, on_success=self.load_records),
            )
            ret_btn.pack(side="left", padx=2)

        # Receipt button
        rec_btn = ctk.CTkButton(
            container,
            text="Receipt",
            font=Theme.FONT_CAPTION_BOLD,
            fg_color=Theme.SECONDARY,
            hover_color=Theme.SECONDARY_HOVER,
            text_color=Theme.SECONDARY_TEXT,
            width=56,
            height=26,
            corner_radius=6,
            command=lambda: self._show_receipt(raw_i),
        )
        rec_btn.pack(side="left", padx=2)

    def _show_receipt(self, issue):
        lib_name = SettingsService.get_setting("library_name")
        if issue.status == "Returned":
            receipt = ReceiptGenerator.generate_return_receipt(
                {
                    "issue_id": issue.id,
                    "book_title": issue.book_title,
                    "member_name": issue.member_name,
                    "issue_date": issue.issue_date,
                    "due_date": issue.due_date,
                    "return_date": issue.return_date,
                    "overdue_days": issue.overdue_days,
                    "fine_amount": issue.fine_amount,
                },
                library_name=lib_name,
            )
        else:
            receipt = ReceiptGenerator.generate_issue_receipt(
                issue_id=issue.id,
                member_name=issue.member_name,
                member_code=issue.member_code,
                book_title=issue.book_title,
                book_isbn=issue.book_isbn,
                issue_date=issue.issue_date,
                due_date=issue.due_date,
                library_name=lib_name,
            )

        ReceiptDialog(self.winfo_toplevel(), "Transaction Receipt", receipt)
