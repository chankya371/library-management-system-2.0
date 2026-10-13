import datetime
import customtkinter as ctk
from tkinter import filedialog
from typing import Optional, Callable
from ui.theme import Theme
from ui.components.badge import StatusBadge
from ui.components.notification import AlertDialog, ReceiptDialog
from utils.icon_factory import IconFactory
from utils.receipt_generator import ReceiptGenerator
from services.book_service import BookService
from services.member_service import MemberService
from services.circulation_service import CirculationService
from services.fine_service import FineService
from services.settings_service import SettingsService


class BaseModal(ctk.CTkToplevel):
    """Base class for clean, centered dialogs."""

    def __init__(self, parent, title: str, width: int = 560, height: int = 620):
        super().__init__(parent)
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        self.configure(fg_color=Theme.BG_CARD)
        self.transient(parent)
        self.grab_set()

        self.update_idletasks()
        try:
            x = parent.winfo_x() + (parent.winfo_width() // 2) - (width // 2)
            y = parent.winfo_y() + (parent.winfo_height() // 2) - (height // 2)
            self.geometry(f"+{max(0, x)}+{max(0, y)}")
        except Exception:
            pass

        # Main wrapper
        self.wrapper = ctk.CTkFrame(self, fg_color="transparent")
        self.wrapper.pack(fill="both", expand=True, padx=24, pady=20)

        # Header
        header = ctk.CTkFrame(self.wrapper, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))

        title_lbl = ctk.CTkLabel(header, text=title, font=Theme.FONT_TITLE, text_color=Theme.TEXT_PRIMARY)
        title_lbl.pack(side="left")

        close_btn = ctk.CTkButton(
            header,
            text="✕",
            font=("Segoe UI", 14, "bold"),
            fg_color="transparent",
            hover_color=Theme.BG_CARD_HOVER,
            text_color=Theme.TEXT_MUTED,
            width=32,
            height=32,
            command=self.destroy,
        )
        close_btn.pack(side="right")


class BookFormModal(BaseModal):
    """Modal dialog for adding or editing a book."""

    def __init__(self, parent, book=None, on_success: Optional[Callable] = None):
        title = "Edit Book" if book else "Add New Book"
        super().__init__(parent, title=title, width=580, height=680)
        self.book = book
        self.on_success = on_success

        scroll = ctk.CTkScrollableFrame(self.wrapper, fg_color="transparent")
        scroll.pack(fill="both", expand=True, pady=(0, 16))

        # ISBN
        ctk.CTkLabel(scroll, text="ISBN *", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(4, 2))
        self.isbn_entry = ctk.CTkEntry(scroll, placeholder_text="e.g. 978-0132350884", fg_color=Theme.BG_INPUT)
        self.isbn_entry.pack(fill="x", pady=(0, 10))

        # Title
        ctk.CTkLabel(scroll, text="Book Title *", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(4, 2))
        self.title_entry = ctk.CTkEntry(scroll, placeholder_text="Full title of the book", fg_color=Theme.BG_INPUT)
        self.title_entry.pack(fill="x", pady=(0, 10))

        # Author
        ctk.CTkLabel(scroll, text="Author(s) *", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(4, 2))
        self.author_entry = ctk.CTkEntry(scroll, placeholder_text="Author names", fg_color=Theme.BG_INPUT)
        self.author_entry.pack(fill="x", pady=(0, 10))

        # Category & Publisher row
        row1 = ctk.CTkFrame(scroll, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 10))

        cat_col = ctk.CTkFrame(row1, fg_color="transparent")
        cat_col.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkLabel(cat_col, text="Category *", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(0, 2))
        categories = ["Computer Science", "Fiction", "Science", "History", "Business", "Self-Help", "Philosophy", "Art", "Other"]
        self.cat_menu = ctk.CTkComboBox(cat_col, values=categories, fg_color=Theme.BG_INPUT)
        self.cat_menu.pack(fill="x")

        pub_col = ctk.CTkFrame(row1, fg_color="transparent")
        pub_col.pack(side="left", fill="x", expand=True, padx=(8, 0))
        ctk.CTkLabel(pub_col, text="Publisher", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(0, 2))
        self.pub_entry = ctk.CTkEntry(pub_col, placeholder_text="Publisher name", fg_color=Theme.BG_INPUT)
        self.pub_entry.pack(fill="x")

        # Year, Copies & Shelf row
        row2 = ctk.CTkFrame(scroll, fg_color="transparent")
        row2.pack(fill="x", pady=(0, 10))

        yr_col = ctk.CTkFrame(row2, fg_color="transparent")
        yr_col.pack(side="left", fill="x", expand=True, padx=(0, 6))
        ctk.CTkLabel(yr_col, text="Year", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(0, 2))
        self.year_entry = ctk.CTkEntry(yr_col, placeholder_text="e.g. 2021", fg_color=Theme.BG_INPUT)
        self.year_entry.pack(fill="x")

        copies_col = ctk.CTkFrame(row2, fg_color="transparent")
        copies_col.pack(side="left", fill="x", expand=True, padx=(6, 6))
        ctk.CTkLabel(copies_col, text="Total Copies *", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(0, 2))
        self.copies_entry = ctk.CTkEntry(copies_col, placeholder_text="e.g. 5", fg_color=Theme.BG_INPUT)
        self.copies_entry.pack(fill="x")

        shelf_col = ctk.CTkFrame(row2, fg_color="transparent")
        shelf_col.pack(side="left", fill="x", expand=True, padx=(6, 0))
        ctk.CTkLabel(shelf_col, text="Shelf No.", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(0, 2))
        self.shelf_entry = ctk.CTkEntry(shelf_col, placeholder_text="e.g. CS-A1-04", fg_color=Theme.BG_INPUT)
        self.shelf_entry.pack(fill="x")

        # Description
        ctk.CTkLabel(scroll, text="Description", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(4, 2))
        self.desc_entry = ctk.CTkTextbox(scroll, height=70, fg_color=Theme.BG_INPUT)
        self.desc_entry.pack(fill="x", pady=(0, 10))

        # Pre-fill if editing
        if self.book:
            self.isbn_entry.insert(0, self.book.isbn)
            self.title_entry.insert(0, self.book.title)
            self.author_entry.insert(0, self.book.author)
            self.cat_menu.set(self.book.category)
            self.pub_entry.insert(0, self.book.publisher or "")
            if self.book.publication_year:
                self.year_entry.insert(0, str(self.book.publication_year))
            self.copies_entry.insert(0, str(self.book.total_copies))
            self.shelf_entry.insert(0, self.book.shelf_number or "")
            if self.book.description:
                self.desc_entry.insert("1.0", self.book.description)
        else:
            self.copies_entry.insert(0, "3")

        # Buttons
        btn_box = ctk.CTkFrame(self.wrapper, fg_color="transparent")
        btn_box.pack(fill="x", side="bottom")

        cancel_btn = ctk.CTkButton(
            btn_box,
            text="Cancel",
            fg_color=Theme.SECONDARY,
            hover_color=Theme.SECONDARY_HOVER,
            text_color=Theme.SECONDARY_TEXT,
            width=100,
            height=36,
            command=self.destroy,
        )
        cancel_btn.pack(side="right", padx=(8, 0))

        save_btn = ctk.CTkButton(
            btn_box,
            text="Save Book",
            font=Theme.FONT_BODY_BOLD,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            text_color=Theme.TEXT_WHITE,
            width=120,
            height=36,
            command=self._save_book,
        )
        save_btn.pack(side="right")

    def _save_book(self):
        isbn = self.isbn_entry.get().strip()
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        category = self.cat_menu.get().strip()
        publisher = self.pub_entry.get().strip()
        year = self.year_entry.get().strip() or None
        copies = self.copies_entry.get().strip()
        shelf = self.shelf_entry.get().strip()
        desc = self.desc_entry.get("1.0", "end-1c").strip()

        if self.book:
            ok, msg = BookService.update_book(
                book_id=self.book.id,
                isbn=isbn,
                title=title,
                author=author,
                category=category,
                publisher=publisher,
                publication_year=year,
                total_copies=copies,
                shelf_number=shelf,
                description=desc,
            )
        else:
            ok, msg, _ = BookService.add_book(
                isbn=isbn,
                title=title,
                author=author,
                category=category,
                publisher=publisher,
                publication_year=year,
                total_copies=copies,
                shelf_number=shelf,
                description=desc,
            )

        if ok:
            AlertDialog(self.master, "Success", msg, level="success")
            self.destroy()
            if self.on_success:
                self.on_success()
        else:
            AlertDialog(self, "Validation Error", msg, level="error")


class MemberFormModal(BaseModal):
    """Modal for registering or editing a member."""

    def __init__(self, parent, member=None, on_success: Optional[Callable] = None):
        title = "Edit Member" if member else "Register New Member"
        super().__init__(parent, title=title, width=540, height=580)
        self.member = member
        self.on_success = on_success

        scroll = ctk.CTkScrollableFrame(self.wrapper, fg_color="transparent")
        scroll.pack(fill="both", expand=True, pady=(0, 16))

        # Full Name
        ctk.CTkLabel(scroll, text="Full Name *", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(4, 2))
        self.name_entry = ctk.CTkEntry(scroll, placeholder_text="e.g. Sarah Jenkins", fg_color=Theme.BG_INPUT)
        self.name_entry.pack(fill="x", pady=(0, 10))

        # Email
        ctk.CTkLabel(scroll, text="Email Address *", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(4, 2))
        self.email_entry = ctk.CTkEntry(scroll, placeholder_text="e.g. sarah.j@example.com", fg_color=Theme.BG_INPUT)
        self.email_entry.pack(fill="x", pady=(0, 10))

        # Phone
        ctk.CTkLabel(scroll, text="Phone Number *", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(4, 2))
        self.phone_entry = ctk.CTkEntry(scroll, placeholder_text="e.g. +1 (555) 019-2834", fg_color=Theme.BG_INPUT)
        self.phone_entry.pack(fill="x", pady=(0, 10))

        # Membership Type & Status
        row = ctk.CTkFrame(scroll, fg_color="transparent")
        row.pack(fill="x", pady=(0, 10))

        type_col = ctk.CTkFrame(row, fg_color="transparent")
        type_col.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkLabel(type_col, text="Membership Type", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(0, 2))
        types = ["Student", "Faculty", "Standard", "Premium"]
        self.type_menu = ctk.CTkComboBox(type_col, values=types, fg_color=Theme.BG_INPUT)
        self.type_menu.pack(fill="x")

        status_col = ctk.CTkFrame(row, fg_color="transparent")
        status_col.pack(side="left", fill="x", expand=True, padx=(8, 0))
        ctk.CTkLabel(status_col, text="Status", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(0, 2))
        statuses = ["Active", "Inactive", "Suspended"]
        self.status_menu = ctk.CTkComboBox(status_col, values=statuses, fg_color=Theme.BG_INPUT)
        self.status_menu.pack(fill="x")

        # Address
        ctk.CTkLabel(scroll, text="Physical Address", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(4, 2))
        self.addr_entry = ctk.CTkEntry(scroll, placeholder_text="e.g. 102 Beacon Hill Rd", fg_color=Theme.BG_INPUT)
        self.addr_entry.pack(fill="x", pady=(0, 10))

        # Pre-fill
        if self.member:
            self.name_entry.insert(0, self.member.full_name)
            self.email_entry.insert(0, self.member.email)
            self.phone_entry.insert(0, self.member.phone)
            self.type_menu.set(self.member.membership_type)
            self.status_menu.set(self.member.status)
            self.addr_entry.insert(0, self.member.address or "")
        else:
            self.type_menu.set("Standard")
            self.status_menu.set("Active")

        # Buttons
        btn_box = ctk.CTkFrame(self.wrapper, fg_color="transparent")
        btn_box.pack(fill="x", side="bottom")

        cancel_btn = ctk.CTkButton(
            btn_box,
            text="Cancel",
            fg_color=Theme.SECONDARY,
            hover_color=Theme.SECONDARY_HOVER,
            text_color=Theme.SECONDARY_TEXT,
            width=100,
            height=36,
            command=self.destroy,
        )
        cancel_btn.pack(side="right", padx=(8, 0))

        save_btn = ctk.CTkButton(
            btn_box,
            text="Save Member",
            font=Theme.FONT_BODY_BOLD,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            text_color=Theme.TEXT_WHITE,
            width=120,
            height=36,
            command=self._save_member,
        )
        save_btn.pack(side="right")

    def _save_member(self):
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        phone = self.phone_entry.get().strip()
        m_type = self.type_menu.get()
        status = self.status_menu.get()
        addr = self.addr_entry.get().strip()

        if self.member:
            ok, msg = MemberService.update_member(
                member_id=self.member.id,
                full_name=name,
                email=email,
                phone=phone,
                address=addr,
                membership_type=m_type,
                status=status,
            )
        else:
            ok, msg, _ = MemberService.register_member(
                full_name=name,
                email=email,
                phone=phone,
                address=addr,
                membership_type=m_type,
                status=status,
            )

        if ok:
            AlertDialog(self.master, "Success", msg, level="success")
            self.destroy()
            if self.on_success:
                self.on_success()
        else:
            AlertDialog(self, "Validation Error", msg, level="error")


class MemberProfileModal(BaseModal):
    """Modal displaying complete member profile, active loans, borrowing history, and fines."""

    def __init__(self, parent, member_id: int):
        profile = MemberService.get_member_profile(member_id)
        member = profile.get("member")
        title = f"Profile: {member.full_name}" if member else "Member Profile"
        super().__init__(parent, title=title, width=640, height=660)

        if not member:
            ctk.CTkLabel(self.wrapper, text="Member not found.").pack()
            return

        scroll = ctk.CTkScrollableFrame(self.wrapper, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        # Profile Card
        card = ctk.CTkFrame(scroll, fg_color=Theme.BG_CARD_HOVER, corner_radius=10)
        card.pack(fill="x", pady=(0, 14), padx=4)

        info_box = ctk.CTkFrame(card, fg_color="transparent")
        info_box.pack(fill="x", padx=16, pady=16)

        ctk.CTkLabel(info_box, text=member.full_name, font=Theme.FONT_TITLE, text_color=Theme.TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(info_box, text=f"ID: {member.member_code} • {member.membership_type} • {member.email} • {member.phone}", font=Theme.FONT_BODY, text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(2, 8))

        # Status & Metrics
        stat_row = ctk.CTkFrame(info_box, fg_color="transparent")
        stat_row.pack(fill="x")

        StatusBadge(stat_row, text=member.status).pack(side="left", padx=(0, 12))

        m1 = f"Active Loans: {profile.get('active_loans_count', 0)}"
        ctk.CTkLabel(stat_row, text=m1, font=Theme.FONT_BODY_BOLD, text_color=Theme.PRIMARY).pack(side="left", padx=8)

        pending = profile.get("pending_fines", 0.0)
        p_col = Theme.DANGER if pending > 0 else Theme.SUCCESS
        m2 = f"Pending Fines: ${pending:.2f}"
        ctk.CTkLabel(stat_row, text=m2, font=Theme.FONT_BODY_BOLD, text_color=p_col).pack(side="left", padx=8)

        # Active Loans Section
        ctk.CTkLabel(scroll, text="Currently Issued Books", font=Theme.FONT_SUBTITLE, text_color=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(12, 6))
        active_loans = profile.get("active_loans", [])
        if not active_loans:
            ctk.CTkLabel(scroll, text="No books currently on loan.", font=Theme.FONT_BODY, text_color=Theme.TEXT_MUTED).pack(anchor="w", padx=8, pady=(0, 8))
        else:
            for l in active_loans:
                item = ctk.CTkFrame(scroll, fg_color=Theme.BG_INPUT, corner_radius=8)
                item.pack(fill="x", pady=3)
                ctk.CTkLabel(item, text=l.book_title, font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_PRIMARY).pack(side="left", padx=12, pady=8)
                status_txt = "OVERDUE" if l.is_overdue else f"Due: {l.due_date}"
                StatusBadge(item, text=status_txt, status_type="Overdue" if l.is_overdue else "Issued").pack(side="right", padx=12)

        # History Section
        ctk.CTkLabel(scroll, text="Past Borrowing History", font=Theme.FONT_SUBTITLE, text_color=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(16, 6))
        past_loans = profile.get("past_loans", [])
        if not past_loans:
            ctk.CTkLabel(scroll, text="No historical loans recorded.", font=Theme.FONT_BODY, text_color=Theme.TEXT_MUTED).pack(anchor="w", padx=8)
        else:
            for l in past_loans:
                item = ctk.CTkFrame(scroll, fg_color=Theme.BG_INPUT, corner_radius=8)
                item.pack(fill="x", pady=3)
                ctk.CTkLabel(item, text=l.book_title, font=Theme.FONT_BODY, text_color=Theme.TEXT_PRIMARY).pack(side="left", padx=12, pady=6)
                ctk.CTkLabel(item, text=f"Returned {l.return_date}", font=Theme.FONT_CAPTION, text_color=Theme.TEXT_MUTED).pack(side="right", padx=12)


class IssueBookModal(BaseModal):
    """Modal for issuing a book with search, stock check, and limit validation."""

    def __init__(self, parent, preselected_book_id=None, preselected_member_id=None, on_success: Optional[Callable] = None):
        super().__init__(parent, title="Issue Book", width=560, height=580)
        self.on_success = on_success

        # Load available books and active members
        self.books = [b for b in BookService.get_all_books() if b.available_copies > 0]
        self.members = [m for m in MemberService.get_all_members() if m.status == "Active"]

        # 1. Member Selector
        ctk.CTkLabel(self.wrapper, text="Select Borrower (Active Members Only) *", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(4, 2))
        mem_options = [f"{m.full_name} ({m.member_code})" for m in self.members] or ["No active members found"]
        self.mem_menu = ctk.CTkComboBox(self.wrapper, values=mem_options, fg_color=Theme.BG_INPUT, height=36)
        self.mem_menu.pack(fill="x", pady=(0, 14))

        if preselected_member_id:
            for idx, m in enumerate(self.members):
                if m.id == preselected_member_id:
                    self.mem_menu.set(mem_options[idx])
                    break

        # 2. Book Selector
        ctk.CTkLabel(self.wrapper, text="Select Book to Issue (Available Copies Only) *", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(4, 2))
        book_options = [f"{b.title} [Avail: {b.available_copies}]" for b in self.books] or ["No available books"]
        self.book_menu = ctk.CTkComboBox(self.wrapper, values=book_options, fg_color=Theme.BG_INPUT, height=36)
        self.book_menu.pack(fill="x", pady=(0, 14))

        if preselected_book_id:
            for idx, b in enumerate(self.books):
                if b.id == preselected_book_id:
                    self.book_menu.set(book_options[idx])
                    break

        # 3. Loan Duration & Due Date calculation
        row = ctk.CTkFrame(self.wrapper, fg_color="transparent")
        row.pack(fill="x", pady=(0, 14))

        days_col = ctk.CTkFrame(row, fg_color="transparent")
        days_col.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkLabel(days_col, text="Loan Duration (Days)", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(0, 2))
        default_days = str(SettingsService.get_borrowing_period_days())
        self.days_entry = ctk.CTkEntry(days_col, fg_color=Theme.BG_INPUT)
        self.days_entry.insert(0, default_days)
        self.days_entry.pack(fill="x")

        due_col = ctk.CTkFrame(row, fg_color="transparent")
        due_col.pack(side="left", fill="x", expand=True, padx=(8, 0))
        ctk.CTkLabel(due_col, text="Calculated Due Date", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(0, 2))
        calc_due = (datetime.date.today() + datetime.timedelta(days=int(default_days))).isoformat()
        self.due_lbl = ctk.CTkLabel(due_col, text=calc_due, font=Theme.FONT_BODY_BOLD, text_color=Theme.PRIMARY)
        self.due_lbl.pack(anchor="w", pady=4)

        # 4. Remarks
        ctk.CTkLabel(self.wrapper, text="Notes / Remarks (Optional)", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(4, 2))
        self.notes_entry = ctk.CTkEntry(self.wrapper, placeholder_text="Special lending conditions or reference tags", fg_color=Theme.BG_INPUT)
        self.notes_entry.pack(fill="x", pady=(0, 20))

        # Action Buttons
        btn_box = ctk.CTkFrame(self.wrapper, fg_color="transparent")
        btn_box.pack(fill="x", side="bottom")

        cancel_btn = ctk.CTkButton(
            btn_box,
            text="Cancel",
            fg_color=Theme.SECONDARY,
            hover_color=Theme.SECONDARY_HOVER,
            text_color=Theme.SECONDARY_TEXT,
            width=100,
            height=36,
            command=self.destroy,
        )
        cancel_btn.pack(side="right", padx=(8, 0))

        issue_btn = ctk.CTkButton(
            btn_box,
            text="Complete Checkout",
            font=Theme.FONT_BODY_BOLD,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            text_color=Theme.TEXT_WHITE,
            width=150,
            height=36,
            command=self._handle_issue,
        )
        issue_btn.pack(side="right")

    def _handle_issue(self):
        mem_sel = self.mem_menu.get()
        book_sel = self.book_menu.get()

        selected_mem = None
        for m in self.members:
            if f"{m.full_name} ({m.member_code})" == mem_sel:
                selected_mem = m
                break

        selected_book = None
        for b in self.books:
            if f"{b.title} [Avail: {b.available_copies}]" == book_sel:
                selected_book = b
                break

        if not selected_mem or not selected_book:
            AlertDialog(self, "Invalid Selection", "Please choose a valid member and available book.", level="error")
            return

        try:
            loan_days = int(self.days_entry.get().strip())
            if loan_days <= 0:
                raise ValueError()
        except ValueError:
            AlertDialog(self, "Error", "Loan duration must be a positive integer number of days.", level="error")
            return

        issue_date = datetime.date.today().isoformat()
        due_date = (datetime.date.today() + datetime.timedelta(days=loan_days)).isoformat()
        notes = self.notes_entry.get().strip()

        ok, msg, new_id = CirculationService.issue_book(
            book_id=selected_book.id,
            member_id=selected_mem.id,
            issue_date=issue_date,
            due_date=due_date,
            notes=notes,
        )

        if ok:
            # Generate receipt
            receipt = ReceiptGenerator.generate_issue_receipt(
                issue_id=new_id,
                member_name=selected_mem.full_name,
                member_code=selected_mem.member_code,
                book_title=selected_book.title,
                book_isbn=selected_book.isbn,
                issue_date=issue_date,
                due_date=due_date,
                library_name=SettingsService.get_setting("library_name"),
            )
            self.destroy()
            if self.on_success:
                self.on_success()
            ReceiptDialog(self.master, "Issue Receipt", receipt)
        else:
            AlertDialog(self, "Issue Error", msg, level="error")


class ReturnBookModal(BaseModal):
    """Modal for returning a book, calculating overdue fines, and generating receipts."""

    def __init__(self, parent, issue_record=None, on_success: Optional[Callable] = None):
        super().__init__(parent, title="Process Book Return", width=560, height=520)
        self.issue_record = issue_record
        self.on_success = on_success

        CirculationService.sync_overdue_statuses()
        self.active_issues = CirculationService.search_issues(status="All")
        self.active_issues = [i for i in self.active_issues if i.status in ("Issued", "Overdue")]

        # Record selector
        ctk.CTkLabel(self.wrapper, text="Select Active Loan Record *", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(4, 2))
        options = [f"#{i.id} - '{i.book_title}' ({i.member_name}) [Due: {i.due_date}]" for i in self.active_issues] or ["No active loans"]
        self.rec_menu = ctk.CTkComboBox(self.wrapper, values=options, fg_color=Theme.BG_INPUT, height=36, command=self._on_record_selected)
        self.rec_menu.pack(fill="x", pady=(0, 14))

        if self.issue_record:
            for idx, i in enumerate(self.active_issues):
                if i.id == self.issue_record.id:
                    self.rec_menu.set(options[idx])
                    break

        # Audit Summary Card
        self.audit_card = ctk.CTkFrame(self.wrapper, fg_color=Theme.BG_CARD_HOVER, corner_radius=10)
        self.audit_card.pack(fill="x", pady=(0, 14))

        self.audit_lbl = ctk.CTkLabel(
            self.audit_card,
            text="Select an issue record to calculate fine details.",
            font=Theme.FONT_BODY,
            text_color=Theme.TEXT_PRIMARY,
            justify="left",
        )
        self.audit_lbl.pack(padx=16, pady=16, anchor="w")

        # Remarks
        ctk.CTkLabel(self.wrapper, text="Return Notes / Condition (Optional)", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(4, 2))
        self.notes_entry = ctk.CTkEntry(self.wrapper, placeholder_text="e.g. Good condition", fg_color=Theme.BG_INPUT)
        self.notes_entry.pack(fill="x", pady=(0, 20))

        # Action Buttons
        btn_box = ctk.CTkFrame(self.wrapper, fg_color="transparent")
        btn_box.pack(fill="x", side="bottom")

        cancel_btn = ctk.CTkButton(
            btn_box,
            text="Cancel",
            fg_color=Theme.SECONDARY,
            hover_color=Theme.SECONDARY_HOVER,
            text_color=Theme.SECONDARY_TEXT,
            width=100,
            height=36,
            command=self.destroy,
        )
        cancel_btn.pack(side="right", padx=(8, 0))

        ret_btn = ctk.CTkButton(
            btn_box,
            text="Confirm Return",
            font=Theme.FONT_BODY_BOLD,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            text_color=Theme.TEXT_WHITE,
            width=140,
            height=36,
            command=self._handle_return,
        )
        ret_btn.pack(side="right")

        # Initial trigger
        self._on_record_selected(self.rec_menu.get())

    def _get_selected_record(self):
        sel = self.rec_menu.get()
        for i in self.active_issues:
            if f"#{i.id} - '{i.book_title}' ({i.member_name}) [Due: {i.due_date}]" == sel:
                return i
        return None

    def _on_record_selected(self, _choice):
        rec = self._get_selected_record()
        if not rec:
            self.audit_lbl.configure(text="No loan selected.")
            return

        daily_rate = SettingsService.get_daily_fine_rate()
        due_dt = datetime.date.fromisoformat(rec.due_date)
        today = datetime.date.today()
        overdue_days = max(0, (today - due_dt).days)
        est_fine = round(overdue_days * daily_rate, 2)

        txt = f"Borrower: {rec.member_name} ({rec.member_code})\n"
        txt += f"Book: {rec.book_title}\n"
        txt += f"Due Date: {rec.due_date}  |  Today: {today.isoformat()}\n"
        if overdue_days > 0:
            txt += f"Status: OVERDUE by {overdue_days} days! Accrued Fine: ${est_fine:.2f}"
        else:
            txt += "Status: On Time (No fine applicable)"

        self.audit_lbl.configure(text=txt)

    def _handle_return(self):
        rec = self._get_selected_record()
        if not rec:
            AlertDialog(self, "Error", "Please select a valid loan record.", level="error")
            return

        notes = self.notes_entry.get().strip()
        ok, msg, summary = CirculationService.return_book(
            issue_id=rec.id,
            return_date=datetime.date.today().isoformat(),
            notes=notes,
        )

        if ok:
            receipt = ReceiptGenerator.generate_return_receipt(
                summary,
                library_name=SettingsService.get_setting("library_name"),
            )
            self.destroy()
            if self.on_success:
                self.on_success()
            ReceiptDialog(self.master, "Return Receipt", receipt)
        else:
            AlertDialog(self, "Return Error", msg, level="error")


class PayFineModal(BaseModal):
    """Modal dialog for settling an outstanding fine and issuing an official receipt."""

    def __init__(self, parent, fine_record: dict, on_success: Optional[Callable] = None):
        super().__init__(parent, title="Settle Fine Payment", width=520, height=480)
        self.fine_record = fine_record
        self.on_success = on_success

        # Info Card
        card = ctk.CTkFrame(self.wrapper, fg_color=Theme.BG_CARD_HOVER, corner_radius=10)
        card.pack(fill="x", pady=(0, 16))

        amount = fine_record.get("fine_amount", 0.0)
        txt = f"Borrower: {fine_record.get('member_name')}\n"
        txt += f"Book: {fine_record.get('book_title')}\n"
        txt += f"Outstanding Fine: ${amount:.2f}"
        ctk.CTkLabel(card, text=txt, font=Theme.FONT_BODY, text_color=Theme.TEXT_PRIMARY, justify="left").pack(padx=16, pady=16, anchor="w")

        # Amount to pay
        ctk.CTkLabel(self.wrapper, text="Payment Amount ($) *", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(4, 2))
        self.amt_entry = ctk.CTkEntry(self.wrapper, fg_color=Theme.BG_INPUT)
        self.amt_entry.insert(0, f"{amount:.2f}")
        self.amt_entry.pack(fill="x", pady=(0, 12))

        # Payment Method
        ctk.CTkLabel(self.wrapper, text="Payment Method *", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(4, 2))
        methods = ["Cash", "Card", "UPI/Online", "Other"]
        self.method_menu = ctk.CTkComboBox(self.wrapper, values=methods, fg_color=Theme.BG_INPUT)
        self.method_menu.pack(fill="x", pady=(0, 12))

        # Notes
        ctk.CTkLabel(self.wrapper, text="Payment Remarks", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(4, 2))
        self.notes_entry = ctk.CTkEntry(self.wrapper, placeholder_text="e.g. Cleared at counter", fg_color=Theme.BG_INPUT)
        self.notes_entry.pack(fill="x", pady=(0, 20))

        # Buttons
        btn_box = ctk.CTkFrame(self.wrapper, fg_color="transparent")
        btn_box.pack(fill="x", side="bottom")

        cancel_btn = ctk.CTkButton(
            btn_box,
            text="Cancel",
            fg_color=Theme.SECONDARY,
            hover_color=Theme.SECONDARY_HOVER,
            text_color=Theme.SECONDARY_TEXT,
            width=100,
            height=36,
            command=self.destroy,
        )
        cancel_btn.pack(side="right", padx=(8, 0))

        pay_btn = ctk.CTkButton(
            btn_box,
            text="Confirm Payment",
            font=Theme.FONT_BODY_BOLD,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            text_color=Theme.TEXT_WHITE,
            width=140,
            height=36,
            command=self._handle_payment,
        )
        pay_btn.pack(side="right")

    def _handle_payment(self):
        try:
            amt = float(self.amt_entry.get().strip())
            if amt <= 0:
                raise ValueError()
        except ValueError:
            AlertDialog(self, "Error", "Please enter a valid positive payment amount.", level="error")
            return

        method = self.method_menu.get()
        notes = self.notes_entry.get().strip()

        ok, msg, receipt_no = FineService.pay_fine(
            issue_id=self.fine_record["issue_id"],
            member_id=self.fine_record["member_id"],
            amount=amt,
            payment_method=method,
            notes=notes,
        )

        if ok:
            receipt = ReceiptGenerator.generate_fine_receipt(
                receipt_number=receipt_no,
                member_name=self.fine_record.get("member_name", ""),
                member_code=self.fine_record.get("member_code", ""),
                amount_paid=amt,
                payment_method=method,
                book_title=self.fine_record.get("book_title", ""),
                notes=notes,
                library_name=SettingsService.get_setting("library_name"),
            )
            self.destroy()
            if self.on_success:
                self.on_success()
            ReceiptDialog(self.master, "Official Payment Receipt", receipt)
        else:
            AlertDialog(self, "Payment Error", msg, level="error")
