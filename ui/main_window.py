import customtkinter as ctk
from ui.theme import Theme
from ui.sidebar import Sidebar
from ui.topbar import Topbar
from ui.login_view import LoginView
from ui.pages.dashboard_page import DashboardPage
from ui.pages.books_page import BooksPage
from ui.pages.members_page import MembersPage
from ui.pages.circulation_page import CirculationPage
from ui.pages.fines_page import FinesPage
from ui.pages.reports_page import ReportsPage
from ui.pages.settings_page import SettingsPage
from ui.components.modals import BookFormModal, MemberFormModal, IssueBookModal, ReturnBookModal


class MainWindow(ctk.CTk):
    """
    Unified application shell providing zero-flicker transitions between
    the Login portal and the full administrative library interface.
    """

    PAGE_TITLES = {
        "dashboard": "System Dashboard",
        "books": "Book Inventory & Catalog",
        "members": "Member Registry & Patrons",
        "circulation": "Circulation Desk (Issues & Returns)",
        "fines": "Fine Payments & Financial Audit",
        "reports": "Reports & Analytics Center",
        "settings": "System Settings & Configuration",
    }

    def __init__(self, current_user=None):
        super().__init__()
        self.current_user = current_user

        self.title("Alexandria - Modern Library Management System")
        self.geometry("1280x800")
        self.minsize(1080, 680)
        self.configure(fg_color=Theme.BG_MAIN)

        # Center on screen
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = max(0, (sw - 1280) // 2)
        y = max(0, (sh - 800) // 2)
        self.geometry(f"+{x}+{y}")

        # Bring window to front
        self.lift()
        self.attributes("-topmost", True)
        self.after(80, lambda: self.attributes("-topmost", False))

        self.pages = {}
        self.current_page_id = "dashboard"

        # Root container
        self.root_container = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.root_container.pack(fill="both", expand=True)

        if self.current_user:
            self.show_authenticated_ui(self.current_user)
        else:
            self.show_login()

    def show_login(self):
        """Displays the login portal."""
        self.current_user = None
        for child in self.root_container.winfo_children():
            child.destroy()

        login_view = LoginView(self.root_container, on_login_success=self.show_authenticated_ui)
        login_view.pack(fill="both", expand=True)

    def show_authenticated_ui(self, user):
        """Transitions into the full application interface."""
        self.current_user = user
        for child in self.root_container.winfo_children():
            child.destroy()

        # 1. Left Fixed Sidebar
        self.sidebar = Sidebar(
            self.root_container,
            current_user=self.current_user,
            on_navigate=self.navigate_to,
            on_logout=self.show_login,
        )
        self.sidebar.pack(side="left", fill="y")

        # 2. Right Container (Topbar + Content)
        self.right_container = ctk.CTkFrame(self.root_container, fg_color="transparent", corner_radius=0)
        self.right_container.pack(side="right", fill="both", expand=True)

        # Topbar
        self.topbar = Topbar(
            self.right_container,
            current_user=self.current_user,
            on_global_search=self._handle_global_search,
        )
        self.topbar.pack(fill="x", side="top")

        # Main Page View Container
        self.content_area = ctk.CTkFrame(self.right_container, fg_color=Theme.BG_MAIN, corner_radius=0)
        self.content_area.pack(fill="both", expand=True, side="top")

        # Bind keyboard shortcuts
        self._bind_keyboard_shortcuts()

        # Navigate to initial dashboard
        self.navigate_to("dashboard")

    def navigate_to(self, page_id: str):
        if page_id not in self.PAGE_TITLES:
            return

        self.current_page_id = page_id
        if hasattr(self, "sidebar"):
            self.sidebar.set_active(page_id)
        if hasattr(self, "topbar"):
            self.topbar.set_title(self.PAGE_TITLES[page_id])

        # Destroy old page in content area
        for child in self.content_area.winfo_children():
            child.destroy()

        # Instantiate selected page
        if page_id == "dashboard":
            page = DashboardPage(self.content_area, self.current_user, self.navigate_to)
        elif page_id == "books":
            page = BooksPage(self.content_area, self.current_user, self.navigate_to)
        elif page_id == "members":
            page = MembersPage(self.content_area, self.current_user, self.navigate_to)
        elif page_id == "circulation":
            page = CirculationPage(self.content_area, self.current_user, self.navigate_to)
        elif page_id == "fines":
            page = FinesPage(self.content_area, self.current_user, self.navigate_to)
        elif page_id == "reports":
            page = ReportsPage(self.content_area, self.current_user, self.navigate_to)
        elif page_id == "settings":
            page = SettingsPage(self.content_area, self.current_user, self.navigate_to)
        else:
            page = DashboardPage(self.content_area, self.current_user, self.navigate_to)

        page.pack(fill="both", expand=True)
        self.pages[page_id] = page

    def _handle_global_search(self, query: str):
        """Routes global search to the Books page and populates query."""
        self.navigate_to("books")
        curr_page = self.pages.get("books")
        if curr_page and hasattr(curr_page, "search_entry"):
            curr_page.search_entry.delete(0, "end")
            curr_page.search_entry.insert(0, query)
            curr_page.load_books()

    def _bind_keyboard_shortcuts(self):
        self.bind("<Control-Key-1>", lambda e: self.navigate_to("dashboard"))
        self.bind("<Control-Key-2>", lambda e: self.navigate_to("books"))
        self.bind("<Control-Key-3>", lambda e: self.navigate_to("members"))
        self.bind("<Control-Key-4>", lambda e: self.navigate_to("circulation"))
        self.bind("<Control-Key-5>", lambda e: self.navigate_to("fines"))
        self.bind("<Control-Key-6>", lambda e: self.navigate_to("reports"))
        self.bind("<Control-Key-7>", lambda e: self.navigate_to("settings"))

        self.bind("<Control-b>", lambda e: BookFormModal(self, on_success=self._refresh_current_page))
        self.bind("<Control-m>", lambda e: MemberFormModal(self, on_success=self._refresh_current_page))
        self.bind("<Control-i>", lambda e: IssueBookModal(self, on_success=self._refresh_current_page))
        self.bind("<Control-r>", lambda e: ReturnBookModal(self, on_success=self._refresh_current_page))

    def _refresh_current_page(self):
        curr = self.pages.get(self.current_page_id)
        if curr:
            if hasattr(curr, "load_books"):
                curr.load_books()
            elif hasattr(curr, "load_members"):
                curr.load_members()
            elif hasattr(curr, "load_records"):
                curr.load_records()
            elif hasattr(curr, "refresh_data"):
                curr.refresh_data()
