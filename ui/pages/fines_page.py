import customtkinter as ctk
from ui.theme import Theme
from ui.components.badge import StatusBadge
from ui.components.stat_card import StatCard
from ui.components.table import ModernTable
from ui.components.notification import AlertDialog, ReceiptDialog
from ui.components.modals import PayFineModal
from utils.icon_factory import IconFactory
from utils.receipt_generator import ReceiptGenerator
from services.fine_service import FineService
from services.settings_service import SettingsService


class FinesPage(ctk.CTkFrame):
    """
    Fine management ledger for reviewing accrued penalties,
    settling member payments, and issuing official financial receipts.
    """

    def __init__(self, master, current_user, on_navigate, **kwargs):
        super().__init__(master, fg_color="transparent", corner_radius=0, **kwargs)
        self.current_user = current_user
        self.on_navigate = on_navigate

        self._render_view()

    def _render_view(self):
        # 1. Top Stat Summary Row
        self.stats_row = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_row.pack(fill="x", padx=16, pady=(16, 12))
        self.stats_row.columnconfigure((0, 1, 2), weight=1, uniform="fine_stat")

        # 2. Controls & Filter Bar
        ctrl_frame = ctk.CTkFrame(self, fg_color=Theme.BG_CARD, border_color=Theme.BORDER, border_width=1, corner_radius=Theme.RADIUS_CARD)
        ctrl_frame.pack(fill="x", padx=16, pady=(0, 12))

        box = ctk.CTkFrame(ctrl_frame, fg_color="transparent")
        box.pack(fill="x", padx=16, pady=12)

        # Search
        self.search_entry = ctk.CTkEntry(
            box,
            placeholder_text="Search fines by member, book title, receipt #...",
            fg_color=Theme.BG_INPUT,
            height=36,
            width=340,
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_fines())

        # Status filter
        self.status_menu = ctk.CTkComboBox(
            box,
            values=["All", "Pending", "Paid"],
            height=36,
            width=130,
            fg_color=Theme.BG_INPUT,
            command=lambda _: self.load_fines(),
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

        # 3. Fines Table
        columns = [
            {"key": "issue_id_str", "label": "Loan #", "width": 80, "anchor": "center"},
            {"key": "member_name", "label": "Member / Patron", "width": 190, "anchor": "w"},
            {"key": "book_title", "label": "Book Title", "width": 240, "anchor": "w"},
            {"key": "amount_str", "label": "Fine Amount", "width": 110, "anchor": "center"},
            {"key": "status", "label": "Status", "width": 100, "anchor": "center", "renderer": self._render_status_badge},
            {"key": "receipt_no", "label": "Receipt #", "width": 150, "anchor": "center"},
            {"key": "_actions", "label": "Actions", "width": 150, "anchor": "center"},
        ]

        self.table = ModernTable(self, columns=columns, empty_message="No fine records found.")
        self.table.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        self.load_fines()

    def _render_status_badge(self, container, value):
        StatusBadge(container, text=value).pack(anchor="center")

    def _reset_filters(self):
        self.search_entry.delete(0, "end")
        self.status_menu.set("All")
        self.load_fines()

    def load_fines(self):
        # Refresh top stats
        for child in self.stats_row.winfo_children():
            child.destroy()

        collected, pending = FineService.get_fine_totals()
        rate = SettingsService.get_daily_fine_rate()

        c1 = StatCard(self.stats_row, title="Total Fines Collected", value=f"${collected:.2f}", icon_name="check", subtext="Settled revenue", accent_color=Theme.SUCCESS)
        c1.grid(row=0, column=0, padx=6, sticky="nsew")

        c2 = StatCard(self.stats_row, title="Pending Overdue Fines", value=f"${pending:.2f}", icon_name="alert", subtext="Unpaid overdue penalties", accent_color=Theme.DANGER)
        c2.grid(row=0, column=1, padx=6, sticky="nsew")

        c3 = StatCard(self.stats_row, title="Overdue Fine Rate", value=f"${rate:.2f} / day", icon_name="fines", subtext="Configured in settings", accent_color=Theme.PRIMARY)
        c3.grid(row=0, column=2, padx=6, sticky="nsew")

        # Load Table records
        q = self.search_entry.get().strip()
        filter_st = self.status_menu.get()

        records = FineService.get_all_fine_records(filter_status=filter_st, query=q)
        rows = []
        for r in records:
            is_paid = r["fine_paid"] == 1
            rows.append({
                "issue_id": r["issue_id"],
                "issue_id_str": f"#{r['issue_id']}",
                "member_name": f"{r['member_name']} ({r['member_code']})",
                "book_title": r["book_title"],
                "amount_str": f"${r['fine_amount']:.2f}",
                "status": "Paid" if is_paid else "Pending",
                "receipt_no": r["receipt_number"] or "—",
                "raw_record": r,
            })

        self.table.set_data(rows, render_actions=self._render_row_actions)

    def _render_row_actions(self, container, row_data):
        raw_r = row_data["raw_record"]

        if raw_r["fine_paid"] == 0:
            pay_btn = ctk.CTkButton(
                container,
                text="Collect",
                font=Theme.FONT_CAPTION_BOLD,
                fg_color=Theme.PRIMARY,
                hover_color=Theme.PRIMARY_HOVER,
                text_color=Theme.TEXT_WHITE,
                width=60,
                height=26,
                corner_radius=6,
                command=lambda: PayFineModal(self.winfo_toplevel(), fine_record=raw_r, on_success=self.load_fines),
            )
            pay_btn.pack(side="left", padx=2)
        else:
            rec_btn = ctk.CTkButton(
                container,
                text="Receipt",
                font=Theme.FONT_CAPTION_BOLD,
                fg_color=Theme.SECONDARY,
                hover_color=Theme.SECONDARY_HOVER,
                text_color=Theme.SECONDARY_TEXT,
                width=60,
                height=26,
                corner_radius=6,
                command=lambda: self._view_receipt(raw_r),
            )
            rec_btn.pack(side="left", padx=2)

    def _view_receipt(self, record):
        lib_name = SettingsService.get_setting("library_name")
        receipt = ReceiptGenerator.generate_fine_receipt(
            receipt_number=record.get("receipt_number", "REC-PAID"),
            member_name=record.get("member_name", ""),
            member_code=record.get("member_code", ""),
            amount_paid=record.get("fine_amount", 0.0),
            payment_method=record.get("payment_method", "Cash"),
            book_title=record.get("book_title", ""),
            notes="Settled fine payment",
            library_name=lib_name,
        )
        ReceiptDialog(self.winfo_toplevel(), "Payment Receipt", receipt)
