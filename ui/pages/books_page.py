import customtkinter as ctk
from ui.theme import Theme
from ui.components.badge import StatusBadge
from ui.components.table import ModernTable
from ui.components.notification import ConfirmDialog, AlertDialog
from ui.components.modals import BookFormModal, IssueBookModal
from utils.icon_factory import IconFactory
from services.book_service import BookService


class BooksPage(ctk.CTkFrame):
    """
    Inventory management screen for cataloging, searching,
    filtering, updating, and safely deleting books.
    """

    def __init__(self, master, current_user, on_navigate, **kwargs):
        super().__init__(master, fg_color="transparent", corner_radius=0, **kwargs)
        self.current_user = current_user
        self.on_navigate = on_navigate

        self._render_view()

    def _render_view(self):
        # 1. Top Controls Bar: Search, Category Filter, Availability Filter, Sort, Add Button
        ctrl_frame = ctk.CTkFrame(self, fg_color=Theme.BG_CARD, border_color=Theme.BORDER, border_width=1, corner_radius=Theme.RADIUS_CARD)
        ctrl_frame.pack(fill="x", padx=16, pady=(16, 12))

        box = ctk.CTkFrame(ctrl_frame, fg_color="transparent")
        box.pack(fill="x", padx=16, pady=12)

        # Search input
        search_icon = IconFactory.get_icon("search", size=(16, 16))
        self.search_entry = ctk.CTkEntry(
            box,
            placeholder_text="Search by title, author, ISBN, category...",
            fg_color=Theme.BG_INPUT,
            height=36,
            width=280,
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_books())

        # Category Filter
        cats = ["All"] + BookService.get_categories()
        self.cat_menu = ctk.CTkComboBox(
            box,
            values=cats,
            height=36,
            width=150,
            fg_color=Theme.BG_INPUT,
            command=lambda _: self.load_books(),
        )
        self.cat_menu.set("All")
        self.cat_menu.pack(side="left", padx=(0, 10))

        # Availability Filter
        avail_opts = ["All", "Available", "Low Stock", "Out of Stock"]
        self.avail_menu = ctk.CTkComboBox(
            box,
            values=avail_opts,
            height=36,
            width=130,
            fg_color=Theme.BG_INPUT,
            command=lambda _: self.load_books(),
        )
        self.avail_menu.set("All")
        self.avail_menu.pack(side="left", padx=(0, 10))

        # Sort Dropdown
        sort_opts = ["Title", "Author", "Year", "Copies"]
        self.sort_menu = ctk.CTkComboBox(
            box,
            values=sort_opts,
            height=36,
            width=110,
            fg_color=Theme.BG_INPUT,
            command=lambda _: self.load_books(),
        )
        self.sort_menu.set("Title")
        self.sort_menu.pack(side="left", padx=(0, 10))

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

        # Add Book Button
        add_btn = ctk.CTkButton(
            box,
            text="+ Add New Book",
            font=Theme.FONT_BODY_BOLD,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            text_color=Theme.TEXT_WHITE,
            height=36,
            corner_radius=8,
            command=lambda: BookFormModal(self.winfo_toplevel(), on_success=self.load_books),
        )
        add_btn.pack(side="right")

        # 2. Books Table
        columns = [
            {"key": "isbn", "label": "ISBN", "width": 130, "anchor": "w"},
            {"key": "title", "label": "Title", "width": 260, "anchor": "w"},
            {"key": "author", "label": "Author", "width": 180, "anchor": "w"},
            {"key": "category", "label": "Category", "width": 130, "anchor": "w"},
            {"key": "copies", "label": "Copies", "width": 90, "anchor": "center"},
            {"key": "status", "label": "Status", "width": 110, "anchor": "center", "renderer": self._render_status_badge},
            {"key": "_actions", "label": "Actions", "width": 170, "anchor": "center"},
        ]

        self.table = ModernTable(self, columns=columns, empty_message="No books found matching criteria.")
        self.table.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        self.load_books()

    def _render_status_badge(self, container, value):
        StatusBadge(container, text=value).pack(anchor="center")

    def _reset_filters(self):
        self.search_entry.delete(0, "end")
        self.cat_menu.set("All")
        self.avail_menu.set("All")
        self.sort_menu.set("Title")
        self.load_books()

    def load_books(self):
        q = self.search_entry.get().strip()
        cat = self.cat_menu.get()
        avail = self.avail_menu.get()
        sort_choice = self.sort_menu.get().lower()

        sort_map = {
            "title": "title",
            "author": "author",
            "year": "publication_year",
            "copies": "available_copies",
        }
        sort_by = sort_map.get(sort_choice, "title")

        books = BookService.search_books(
            query=q,
            category=cat,
            availability=avail,
            sort_by=sort_by,
        )

        rows = []
        for b in books:
            rows.append({
                "id": b.id,
                "isbn": b.isbn,
                "title": b.title,
                "author": b.author,
                "category": b.category,
                "copies": f"{b.available_copies} / {b.total_copies}",
                "status": b.status_label,
                "raw_book": b,
            })

        self.table.set_data(rows, render_actions=self._render_row_actions)

    def _render_row_actions(self, container, row_data):
        raw_b = row_data["raw_book"]

        # Issue shortcut button (if copies available)
        if raw_b.available_copies > 0:
            issue_btn = ctk.CTkButton(
                container,
                text="Loan",
                font=Theme.FONT_CAPTION_BOLD,
                fg_color=Theme.INFO,
                hover_color=Theme.PRIMARY_HOVER,
                text_color=Theme.TEXT_WHITE,
                width=46,
                height=26,
                corner_radius=6,
                command=lambda: IssueBookModal(self.winfo_toplevel(), preselected_book_id=raw_b.id, on_success=self.load_books),
            )
            issue_btn.pack(side="left", padx=2)

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
            command=lambda: BookFormModal(self.winfo_toplevel(), book=raw_b, on_success=self.load_books),
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
            width=42,
            height=26,
            corner_radius=6,
            command=lambda: self._confirm_delete(raw_b),
        )
        del_btn.pack(side="left", padx=2)

    def _confirm_delete(self, book):
        def do_delete():
            ok, msg = BookService.delete_book(book.id)
            if ok:
                AlertDialog(self.winfo_toplevel(), "Deleted", msg, level="success")
                self.load_books()
            else:
                AlertDialog(self.winfo_toplevel(), "Delete Protected", msg, level="error")

        ConfirmDialog(
            self.winfo_toplevel(),
            title="Delete Book",
            message=f"Are you sure you want to permanently delete '{book.title}'?\n\nNote: Books with active loans or history cannot be deleted.",
            on_confirm=do_delete,
            confirm_text="Delete Book",
            danger=True,
        )
