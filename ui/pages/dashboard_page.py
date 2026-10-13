import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ui.theme import Theme
from ui.components.stat_card import StatCard
from ui.components.badge import StatusBadge
from ui.components.table import ModernTable
from ui.components.modals import BookFormModal, MemberFormModal, IssueBookModal, ReturnBookModal
from utils.icon_factory import IconFactory
from services.report_service import ReportService
from services.settings_service import SettingsService


class DashboardPage(ctk.CTkScrollableFrame):
    """
    Primary landing dashboard with real-time stats cards,
    Matplotlib circulation analytics, recently added items,
    and quick action triggers.
    """

    def __init__(self, master, current_user, on_navigate, **kwargs):
        super().__init__(master, fg_color="transparent", corner_radius=0, **kwargs)
        self.current_user = current_user
        self.on_navigate = on_navigate

        self._render_view()

    def _render_view(self):
        # 1. Header Banner & Quick Actions
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", padx=16, pady=(16, 20))

        welcome_box = ctk.CTkFrame(top_bar, fg_color="transparent")
        welcome_box.pack(side="left")

        lib_name = SettingsService.get_setting("library_name", "Modern Library")
        ctk.CTkLabel(
            welcome_box,
            text=f"Welcome back, {self.current_user.full_name} 👋",
            font=Theme.FONT_TITLE,
            text_color=Theme.TEXT_PRIMARY,
        ).pack(anchor="w")

        ctk.CTkLabel(
            welcome_box,
            text=f"{lib_name} • System Overview & Circulation Control",
            font=Theme.FONT_BODY,
            text_color=Theme.TEXT_SECONDARY,
        ).pack(anchor="w", pady=(2, 0))

        # Quick action buttons row
        action_box = ctk.CTkFrame(top_bar, fg_color="transparent")
        action_box.pack(side="right")

        btn_add_book = ctk.CTkButton(
            action_box,
            text="+ Add Book",
            font=Theme.FONT_BODY_BOLD,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            text_color=Theme.TEXT_WHITE,
            height=36,
            corner_radius=8,
            command=lambda: BookFormModal(self.winfo_toplevel(), on_success=self.refresh_data),
        )
        btn_add_book.pack(side="left", padx=4)

        btn_reg_mem = ctk.CTkButton(
            action_box,
            text="+ New Member",
            font=Theme.FONT_BODY_BOLD,
            fg_color=Theme.SECONDARY,
            hover_color=Theme.SECONDARY_HOVER,
            text_color=Theme.SECONDARY_TEXT,
            height=36,
            corner_radius=8,
            command=lambda: MemberFormModal(self.winfo_toplevel(), on_success=self.refresh_data),
        )
        btn_reg_mem.pack(side="left", padx=4)

        btn_issue = ctk.CTkButton(
            action_box,
            text="Issue Book",
            font=Theme.FONT_BODY_BOLD,
            fg_color=Theme.INFO,
            hover_color=Theme.PRIMARY_HOVER,
            text_color=Theme.TEXT_WHITE,
            height=36,
            corner_radius=8,
            command=lambda: IssueBookModal(self.winfo_toplevel(), on_success=self.refresh_data),
        )
        btn_issue.pack(side="left", padx=4)

        btn_return = ctk.CTkButton(
            action_box,
            text="Return Book",
            font=Theme.FONT_BODY_BOLD,
            fg_color=Theme.SECONDARY,
            hover_color=Theme.SECONDARY_HOVER,
            text_color=Theme.SECONDARY_TEXT,
            height=36,
            corner_radius=8,
            command=lambda: ReturnBookModal(self.winfo_toplevel(), on_success=self.refresh_data),
        )
        btn_return.pack(side="left", padx=4)

        # 2. Stat Cards Grid (6 cards in a 3x2 grid)
        self.stats_grid = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_grid.pack(fill="x", padx=16, pady=(0, 20))
        self.stats_grid.columnconfigure((0, 1, 2), weight=1, uniform="stat_col")

        # 3. Charts Section (2 side-by-side charts)
        self.charts_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.charts_frame.pack(fill="x", padx=16, pady=(0, 20))
        self.charts_frame.columnconfigure((0, 1), weight=1, uniform="chart_col")

        # 4. Activity Tables Section (Recently Added & Urgent Overdue)
        self.activity_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.activity_frame.pack(fill="x", padx=16, pady=(0, 24))
        self.activity_frame.columnconfigure((0, 1), weight=1, uniform="act_col")

        self.refresh_data()

    def refresh_data(self):
        # Clear dynamic children in stats, charts, and activity
        for child in self.stats_grid.winfo_children():
            child.destroy()
        for child in self.charts_frame.winfo_children():
            child.destroy()
        for child in self.activity_frame.winfo_children():
            child.destroy()

        summary = ReportService.get_dashboard_summary()

        # Build 6 Stat Cards
        c1 = StatCard(
            self.stats_grid,
            title="Total Books",
            value=f"{summary['total_books']} copies",
            icon_name="books",
            subtext=f"{summary['total_titles']} unique titles cataloged",
            accent_color=Theme.INFO,
        )
        c1.grid(row=0, column=0, padx=6, pady=6, sticky="nsew")

        c2 = StatCard(
            self.stats_grid,
            title="Available Books",
            value=f"{summary['available_books']} copies",
            icon_name="check",
            subtext="Ready for checkout right now",
            accent_color=Theme.SUCCESS,
        )
        c2.grid(row=0, column=1, padx=6, pady=6, sticky="nsew")

        c3 = StatCard(
            self.stats_grid,
            title="Issued Books",
            value=f"{summary['issued_books']} copies",
            icon_name="circulation",
            subtext="Currently with borrowers",
            accent_color=Theme.PRIMARY,
        )
        c3.grid(row=0, column=2, padx=6, pady=6, sticky="nsew")

        c4 = StatCard(
            self.stats_grid,
            title="Registered Members",
            value=str(summary["total_members"]),
            icon_name="members",
            subtext=f"{summary['active_members']} active patrons",
            accent_color=Theme.SECONDARY,
        )
        c4.grid(row=1, column=0, padx=6, pady=6, sticky="nsew")

        c5 = StatCard(
            self.stats_grid,
            title="Overdue Books",
            value=str(summary["overdue_books"]),
            icon_name="alert",
            subtext="Past due return date",
            accent_color=Theme.DANGER,
        )
        c5.grid(row=1, column=1, padx=6, pady=6, sticky="nsew")

        c6 = StatCard(
            self.stats_grid,
            title="Total Fines",
            value=f"${summary['total_fines_collected']:.2f}",
            icon_name="fines",
            subtext=f"${summary['total_fines_pending']:.2f} pending collection",
            accent_color=Theme.WARNING,
        )
        c6.grid(row=1, column=2, padx=6, pady=6, sticky="nsew")

        # Render Matplotlib Charts
        self._render_charts()

        # Render Activity Tables
        self._render_activity_tables()

    def _render_charts(self):
        trend_data = ReportService.get_circulation_trend_data(days=7)
        cat_data = ReportService.get_category_distribution()

        is_dark = ctk.get_appearance_mode().lower() == "dark"
        chart_bg = "#1e293b" if is_dark else "#ffffff"
        text_color = "#f8fafc" if is_dark else "#0f172a"
        grid_color = "#334155" if is_dark else "#e2e8f0"

        # Chart 1: Circulation Trends (Bar Chart)
        card1 = ctk.CTkFrame(self.charts_frame, fg_color=Theme.BG_CARD, border_color=Theme.BORDER, border_width=1, corner_radius=12)
        card1.grid(row=0, column=0, padx=6, sticky="nsew")

        ctk.CTkLabel(card1, text="Circulation Trends (Last 7 Days)", font=Theme.FONT_SUBTITLE, text_color=Theme.TEXT_PRIMARY).pack(anchor="w", padx=16, pady=(14, 4))

        fig1 = Figure(figsize=(5.5, 3.2), dpi=90, facecolor=chart_bg)
        ax1 = fig1.add_subplot(111)
        ax1.set_facecolor(chart_bg)

        x_indices = range(len(trend_data["labels"]))
        bar_w = 0.35

        ax1.bar([x - bar_w/2 for x in x_indices], trend_data["issued"], width=bar_w, label="Issued", color="#0d9488")
        ax1.bar([x + bar_w/2 for x in x_indices], trend_data["returned"], width=bar_w, label="Returned", color="#3b82f6")

        ax1.set_xticks(x_indices)
        ax1.set_xticklabels(trend_data["labels"], color=text_color, fontsize=8)
        ax1.tick_params(colors=text_color)
        ax1.grid(axis="y", linestyle="--", alpha=0.3, color=grid_color)
        for spine in ax1.spines.values():
            spine.set_color(grid_color)
        ax1.legend(facecolor=chart_bg, edgecolor=grid_color, labelcolor=text_color, fontsize=8)
        fig1.tight_layout()

        canvas1 = FigureCanvasTkAgg(fig1, master=card1)
        canvas1.draw()
        canvas1.get_tk_widget().pack(fill="both", expand=True, padx=12, pady=(0, 12))

        # Chart 2: Category Distribution (Doughnut / Pie)
        card2 = ctk.CTkFrame(self.charts_frame, fg_color=Theme.BG_CARD, border_color=Theme.BORDER, border_width=1, corner_radius=12)
        card2.grid(row=0, column=1, padx=6, sticky="nsew")

        ctk.CTkLabel(card2, text="Book Collection by Category", font=Theme.FONT_SUBTITLE, text_color=Theme.TEXT_PRIMARY).pack(anchor="w", padx=16, pady=(14, 4))

        fig2 = Figure(figsize=(5.5, 3.2), dpi=90, facecolor=chart_bg)
        ax2 = fig2.add_subplot(111)
        ax2.set_facecolor(chart_bg)

        if cat_data:
            cat_labels = list(cat_data.keys())[:6]
            cat_vals = [cat_data[k] for k in cat_labels]
            colors = ["#0d9488", "#3b82f6", "#10b981", "#f59e0b", "#8b5cf6", "#ec4899"]
            wedges, texts, autotexts = ax2.pie(
                cat_vals,
                labels=cat_labels,
                autopct="%1.0f%%",
                startangle=140,
                colors=colors[:len(cat_vals)],
                textprops=dict(color=text_color, fontsize=8),
                wedgeprops=dict(width=0.4, edgecolor=chart_bg),
            )
            for autotext in autotexts:
                autotext.set_color("#ffffff")
                autotext.set_fontsize(7)
                autotext.set_weight("bold")
        else:
            ax2.text(0.5, 0.5, "No category data available", ha="center", va="center", color=text_color)

        fig2.tight_layout()
        canvas2 = FigureCanvasTkAgg(fig2, master=card2)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def _render_activity_tables(self):
        # Left: Recently Added Books
        act_card1 = ctk.CTkFrame(self.activity_frame, fg_color=Theme.BG_CARD, border_color=Theme.BORDER, border_width=1, corner_radius=12)
        act_card1.grid(row=0, column=0, padx=6, sticky="nsew")

        h1 = ctk.CTkFrame(act_card1, fg_color="transparent")
        h1.pack(fill="x", padx=16, pady=(14, 8))
        ctk.CTkLabel(h1, text="Recently Cataloged Books", font=Theme.FONT_SUBTITLE, text_color=Theme.TEXT_PRIMARY).pack(side="left")

        recent_books = ReportService.get_recently_added_books(limit=4)
        if not recent_books:
            ctk.CTkLabel(act_card1, text="No books cataloged yet.", font=Theme.FONT_BODY, text_color=Theme.TEXT_MUTED).pack(pady=20)
        else:
            for b in recent_books:
                item = ctk.CTkFrame(act_card1, fg_color=Theme.BG_CARD_HOVER, corner_radius=8)
                item.pack(fill="x", padx=12, pady=3)

                info = ctk.CTkFrame(item, fg_color="transparent")
                info.pack(side="left", padx=10, pady=6)
                ctk.CTkLabel(info, text=b["title"][:34], font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_PRIMARY, anchor="w").pack(anchor="w")
                ctk.CTkLabel(info, text=f"{b['author']} • {b['category']}", font=Theme.FONT_CAPTION, text_color=Theme.TEXT_SECONDARY, anchor="w").pack(anchor="w")

                copies_txt = f"{b['available_copies']}/{b['total_copies']} Avail"
                StatusBadge(item, text=copies_txt, status_type="Available" if b["available_copies"] > 0 else "Out of Stock").pack(side="right", padx=10)

        # Right: Urgent Overdue Items
        act_card2 = ctk.CTkFrame(self.activity_frame, fg_color=Theme.BG_CARD, border_color=Theme.BORDER, border_width=1, corner_radius=12)
        act_card2.grid(row=0, column=1, padx=6, sticky="nsew")

        h2 = ctk.CTkFrame(act_card2, fg_color="transparent")
        h2.pack(fill="x", padx=16, pady=(14, 8))
        ctk.CTkLabel(h2, text="Urgent Overdue Items", font=Theme.FONT_SUBTITLE, text_color=Theme.TEXT_PRIMARY).pack(side="left")

        overdue_items = ReportService.get_overdue_report()[:4]
        if not overdue_items:
            ctk.CTkLabel(act_card2, text="Great! No overdue books at the moment.", font=Theme.FONT_BODY, text_color=Theme.SUCCESS_TEXT).pack(pady=20)
        else:
            for o in overdue_items:
                item = ctk.CTkFrame(act_card2, fg_color=Theme.BG_CARD_HOVER, corner_radius=8)
                item.pack(fill="x", padx=12, pady=3)

                info = ctk.CTkFrame(item, fg_color="transparent")
                info.pack(side="left", padx=10, pady=6)
                ctk.CTkLabel(info, text=o["title"][:30], font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_PRIMARY, anchor="w").pack(anchor="w")
                ctk.CTkLabel(info, text=f"Borrower: {o['full_name']} • Due: {o['due_date']}", font=Theme.FONT_CAPTION, text_color=Theme.DANGER_TEXT, anchor="w").pack(anchor="w")

                StatusBadge(item, text=f"${o['fine_amount']:.2f} Fine", status_type="Overdue").pack(side="right", padx=10)
