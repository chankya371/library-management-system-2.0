import os
import customtkinter as ctk
from tkinter import filedialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ui.theme import Theme
from ui.components.badge import StatusBadge
from ui.components.table import ModernTable
from ui.components.notification import AlertDialog
from utils.icon_factory import IconFactory
from services.report_service import ReportService
from services.book_service import BookService
from services.member_service import MemberService
from services.circulation_service import CirculationService
from services.fine_service import FineService


class ReportsPage(ctk.CTkScrollableFrame):
    """
    Analytics & Business Intelligence center with multi-dataset reports,
    Matplotlib visualizations, and CSV / Excel export facilities.
    """

    def __init__(self, master, current_user, on_navigate, **kwargs):
        super().__init__(master, fg_color="transparent", corner_radius=0, **kwargs)
        self.current_user = current_user
        self.on_navigate = on_navigate

        self._render_view()

    def _render_view(self):
        # 1. Header & Report Type Selector Bar
        ctrl_frame = ctk.CTkFrame(self, fg_color=Theme.BG_CARD, border_color=Theme.BORDER, border_width=1, corner_radius=Theme.RADIUS_CARD)
        ctrl_frame.pack(fill="x", padx=16, pady=(16, 16))

        box = ctk.CTkFrame(ctrl_frame, fg_color="transparent")
        box.pack(fill="x", padx=16, pady=12)

        ctk.CTkLabel(box, text="Select Report Type:", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_SECONDARY).pack(side="left", padx=(0, 8))

        report_types = [
            "Total Inventory Catalog",
            "Most Borrowed Books",
            "Most Active Members",
            "Overdue Loans Audit",
            "Fines Collection Audit",
        ]
        self.report_menu = ctk.CTkComboBox(
            box,
            values=report_types,
            height=36,
            width=240,
            fg_color=Theme.BG_INPUT,
            command=lambda _: self.load_selected_report(),
        )
        self.report_menu.set(report_types[0])
        self.report_menu.pack(side="left", padx=(0, 16))

        # Export Buttons
        csv_btn = ctk.CTkButton(
            box,
            text="Export to CSV",
            font=Theme.FONT_BODY_BOLD,
            fg_color=Theme.SECONDARY,
            hover_color=Theme.SECONDARY_HOVER,
            text_color=Theme.SECONDARY_TEXT,
            height=36,
            corner_radius=8,
            command=self._export_csv,
        )
        csv_btn.pack(side="right", padx=(8, 0))

        excel_btn = ctk.CTkButton(
            box,
            text="Export to Excel (.xlsx)",
            font=Theme.FONT_BODY_BOLD,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            text_color=Theme.TEXT_WHITE,
            height=36,
            corner_radius=8,
            command=self._export_excel,
        )
        excel_btn.pack(side="right")

        # 2. Analytics Visualizations Row
        self.charts_card = ctk.CTkFrame(self, fg_color=Theme.BG_CARD, border_color=Theme.BORDER, border_width=1, corner_radius=12)
        self.charts_card.pack(fill="x", padx=16, pady=(0, 16))
        self._render_analytics_chart()

        # 3. Report Data Table Card
        self.table_card = ctk.CTkFrame(self, fg_color="transparent")
        self.table_card.pack(fill="both", expand=True, padx=16, pady=(0, 24))

        self.current_headers = []
        self.current_rows_raw = []
        self.table = None

        self.load_selected_report()

    def _render_analytics_chart(self):
        for child in self.charts_card.winfo_children():
            child.destroy()

        h_box = ctk.CTkFrame(self.charts_card, fg_color="transparent")
        h_box.pack(fill="x", padx=16, pady=(12, 4))
        ctk.CTkLabel(h_box, text="Circulation & Inventory Visual Intelligence", font=Theme.FONT_SUBTITLE, text_color=Theme.TEXT_PRIMARY).pack(side="left")

        trend_data = ReportService.get_circulation_trend_data(days=7)
        top_books = ReportService.get_most_borrowed_books(limit=5)

        is_dark = ctk.get_appearance_mode().lower() == "dark"
        chart_bg = "#1e293b" if is_dark else "#ffffff"
        text_color = "#f8fafc" if is_dark else "#0f172a"
        grid_color = "#334155" if is_dark else "#e2e8f0"

        fig = Figure(figsize=(10, 3.2), dpi=90, facecolor=chart_bg)

        # Subplot 1: Top Borrowed
        ax1 = fig.add_subplot(121)
        ax1.set_facecolor(chart_bg)
        if top_books:
            b_titles = [b["title"][:14] + "..." for b in top_books]
            b_counts = [b["borrow_count"] for b in top_books]
            ax1.barh(b_titles[::-1], b_counts[::-1], color="#14b8a6")
            ax1.set_title("Top 5 Borrowed Titles", color=text_color, fontsize=10)
        ax1.tick_params(colors=text_color, labelsize=8)
        ax1.grid(axis="x", linestyle="--", alpha=0.3, color=grid_color)
        for spine in ax1.spines.values():
            spine.set_color(grid_color)

        # Subplot 2: 7-day flow
        ax2 = fig.add_subplot(122)
        ax2.set_facecolor(chart_bg)
        x_idx = range(len(trend_data["labels"]))
        ax2.plot(x_idx, trend_data["issued"], marker="o", color="#0d9488", label="Issues")
        ax2.plot(x_idx, trend_data["returned"], marker="s", color="#3b82f6", label="Returns")
        ax2.set_xticks(x_idx)
        ax2.set_xticklabels(trend_data["labels"], color=text_color, fontsize=8)
        ax2.set_title("7-Day Loan Flow", color=text_color, fontsize=10)
        ax2.tick_params(colors=text_color, labelsize=8)
        ax2.grid(linestyle="--", alpha=0.3, color=grid_color)
        for spine in ax2.spines.values():
            spine.set_color(grid_color)
        ax2.legend(facecolor=chart_bg, edgecolor=grid_color, labelcolor=text_color, fontsize=8)

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.charts_card)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def load_selected_report(self):
        rep = self.report_menu.get()

        for child in self.table_card.winfo_children():
            child.destroy()

        if rep == "Total Inventory Catalog":
            books = BookService.get_all_books()
            self.current_headers = ["ISBN", "Title", "Author", "Category", "Total Copies", "Available Copies", "Shelf"]
            self.current_rows_raw = [
                [b.isbn, b.title, b.author, b.category, b.total_copies, b.available_copies, b.shelf_number]
                for b in books
            ]
            cols = [
                {"key": "col0", "label": "ISBN", "width": 130},
                {"key": "col1", "label": "Title", "width": 260},
                {"key": "col2", "label": "Author", "width": 180},
                {"key": "col3", "label": "Category", "width": 130},
                {"key": "col4", "label": "Total", "width": 80, "anchor": "center"},
                {"key": "col5", "label": "Available", "width": 80, "anchor": "center"},
                {"key": "col6", "label": "Shelf", "width": 100, "anchor": "center"},
            ]

        elif rep == "Most Borrowed Books":
            data = ReportService.get_most_borrowed_books(limit=20)
            self.current_headers = ["Book ID", "Title", "Author", "Category", "Total Times Borrowed"]
            self.current_rows_raw = [
                [d["id"], d["title"], d["author"], d["category"], d["borrow_count"]]
                for d in data
            ]
            cols = [
                {"key": "col0", "label": "ID", "width": 70, "anchor": "center"},
                {"key": "col1", "label": "Title", "width": 300},
                {"key": "col2", "label": "Author", "width": 200},
                {"key": "col3", "label": "Category", "width": 140},
                {"key": "col4", "label": "Times Borrowed", "width": 140, "anchor": "center"},
            ]

        elif rep == "Most Active Members":
            data = ReportService.get_most_active_members(limit=20)
            self.current_headers = ["Member ID", "Full Name", "Member Code", "Type", "Total Loans Taken"]
            self.current_rows_raw = [
                [d["id"], d["full_name"], d["member_code"], d["membership_type"], d["total_borrows"]]
                for d in data
            ]
            cols = [
                {"key": "col0", "label": "ID", "width": 70, "anchor": "center"},
                {"key": "col1", "label": "Full Name", "width": 240},
                {"key": "col2", "label": "Member Code", "width": 140},
                {"key": "col3", "label": "Type", "width": 120, "anchor": "center"},
                {"key": "col4", "label": "Total Loans", "width": 140, "anchor": "center"},
            ]

        elif rep == "Overdue Loans Audit":
            data = ReportService.get_overdue_report()
            self.current_headers = ["Loan #", "Title", "ISBN", "Borrower", "Email", "Phone", "Due Date", "Fine Accrued ($)"]
            self.current_rows_raw = [
                [d["issue_id"], d["title"], d["isbn"], d["full_name"], d["email"], d["phone"], d["due_date"], f"${d['fine_amount']:.2f}"]
                for d in data
            ]
            cols = [
                {"key": "col0", "label": "Loan #", "width": 80, "anchor": "center"},
                {"key": "col1", "label": "Title", "width": 240},
                {"key": "col3", "label": "Borrower", "width": 180},
                {"key": "col4", "label": "Email", "width": 200},
                {"key": "col6", "label": "Due Date", "width": 110, "anchor": "center"},
                {"key": "col7", "label": "Accrued Fine", "width": 120, "anchor": "center"},
            ]

        else:  # Fines Collection Audit
            data = FineService.get_all_fine_records()
            self.current_headers = ["Loan #", "Borrower", "Book Title", "Fine Amount ($)", "Status", "Receipt #"]
            self.current_rows_raw = [
                [d["issue_id"], d["member_name"], d["book_title"], f"${d['fine_amount']:.2f}", "Paid" if d["fine_paid"] else "Pending", d["receipt_number"] or "—"]
                for d in data
            ]
            cols = [
                {"key": "col0", "label": "Loan #", "width": 80, "anchor": "center"},
                {"key": "col1", "label": "Borrower", "width": 200},
                {"key": "col2", "label": "Book Title", "width": 260},
                {"key": "col3", "label": "Fine Amount", "width": 110, "anchor": "center"},
                {"key": "col4", "label": "Status", "width": 100, "anchor": "center"},
                {"key": "col5", "label": "Receipt #", "width": 140, "anchor": "center"},
            ]

        self.table = ModernTable(self.table_card, columns=cols, empty_message="No records for this report.")
        self.table.pack(fill="both", expand=True)

        # Convert rows for ModernTable display
        table_rows = []
        for r in self.current_rows_raw:
            row_dict = {}
            for idx, val in enumerate(r):
                row_dict[f"col{idx}"] = str(val)
            table_rows.append(row_dict)

        self.table.set_data(table_rows)

    def _export_csv(self):
        rep = self.report_menu.get().replace(" ", "_").lower()
        path = filedialog.asksaveasfilename(
            parent=self.winfo_toplevel(),
            defaultextension=".csv",
            initialfile=f"{rep}_export.csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export Report to CSV",
        )
        if path:
            ok, msg = ReportService.export_to_csv(path, self.current_headers, self.current_rows_raw)
            level = "success" if ok else "error"
            AlertDialog(self.winfo_toplevel(), "Export Result", msg, level=level)

    def _export_excel(self):
        rep = self.report_menu.get()
        sheet_title = rep[:28].replace(" ", "_")
        filename_def = f"{sheet_title.lower()}_export.xlsx"

        path = filedialog.asksaveasfilename(
            parent=self.winfo_toplevel(),
            defaultextension=".xlsx",
            initialfile=filename_def,
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            title="Export Report to Excel",
        )
        if path:
            ok, msg = ReportService.export_to_excel(path, sheet_title, self.current_headers, self.current_rows_raw)
            level = "success" if ok else "error"
            AlertDialog(self.winfo_toplevel(), "Export Result", msg, level=level)
