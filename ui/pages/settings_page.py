import customtkinter as ctk
from tkinter import filedialog
from ui.theme import Theme
from ui.components.badge import StatusBadge
from ui.components.notification import ConfirmDialog, AlertDialog
from utils.icon_factory import IconFactory
from services.settings_service import SettingsService
from services.backup_service import BackupService
from services.auth_service import AuthService


class SettingsPage(ctk.CTkScrollableFrame):
    """
    System configuration, database backup/restore operations,
    theme customization, and user role management.
    """

    def __init__(self, master, current_user, on_navigate, **kwargs):
        super().__init__(master, fg_color="transparent", corner_radius=0, **kwargs)
        self.current_user = current_user
        self.on_navigate = on_navigate

        self._render_view()

    def _render_view(self):
        # 1. General Library Info Card
        card1 = ctk.CTkFrame(self, fg_color=Theme.BG_CARD, border_color=Theme.BORDER, border_width=1, corner_radius=12)
        card1.pack(fill="x", padx=16, pady=(16, 16))

        h1 = ctk.CTkFrame(card1, fg_color="transparent")
        h1.pack(fill="x", padx=20, pady=(16, 12))
        ctk.CTkLabel(h1, text="Organization & Branch Settings", font=Theme.FONT_SUBTITLE, text_color=Theme.TEXT_PRIMARY).pack(side="left")

        f1 = ctk.CTkFrame(card1, fg_color="transparent")
        f1.pack(fill="x", padx=20, pady=(0, 20))

        # Library Name
        ctk.CTkLabel(f1, text="Library Name", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(0, 2))
        self.name_entry = ctk.CTkEntry(f1, fg_color=Theme.BG_INPUT, height=36)
        self.name_entry.insert(0, SettingsService.get_setting("library_name", "Alexandria Modern Library"))
        self.name_entry.pack(fill="x", pady=(0, 10))

        # Email & Phone row
        row_ep = ctk.CTkFrame(f1, fg_color="transparent")
        row_ep.pack(fill="x", pady=(0, 10))

        em_col = ctk.CTkFrame(row_ep, fg_color="transparent")
        em_col.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkLabel(em_col, text="Contact Email", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(0, 2))
        self.email_entry = ctk.CTkEntry(em_col, fg_color=Theme.BG_INPUT, height=36)
        self.email_entry.insert(0, SettingsService.get_setting("library_email", "contact@alexandrialib.org"))
        self.email_entry.pack(fill="x")

        ph_col = ctk.CTkFrame(row_ep, fg_color="transparent")
        ph_col.pack(side="left", fill="x", expand=True, padx=(8, 0))
        ctk.CTkLabel(ph_col, text="Contact Phone", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(0, 2))
        self.phone_entry = ctk.CTkEntry(ph_col, fg_color=Theme.BG_INPUT, height=36)
        self.phone_entry.insert(0, SettingsService.get_setting("library_phone", "+1 (555) 234-5678"))
        self.phone_entry.pack(fill="x")

        # Address
        ctk.CTkLabel(f1, text="Branch Physical Address", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(0, 2))
        self.addr_entry = ctk.CTkEntry(f1, fg_color=Theme.BG_INPUT, height=36)
        self.addr_entry.insert(0, SettingsService.get_setting("library_address", "450 Innovation Parkway, Suite 100"))
        self.addr_entry.pack(fill="x", pady=(0, 16))

        save_gen_btn = ctk.CTkButton(
            f1,
            text="Save Library Info",
            font=Theme.FONT_BODY_BOLD,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            text_color=Theme.TEXT_WHITE,
            height=36,
            command=self._save_general_settings,
        )
        save_gen_btn.pack(anchor="w")

        # 2. Circulation & Policy Rules Card
        card2 = ctk.CTkFrame(self, fg_color=Theme.BG_CARD, border_color=Theme.BORDER, border_width=1, corner_radius=12)
        card2.pack(fill="x", padx=16, pady=(0, 16))

        h2 = ctk.CTkFrame(card2, fg_color="transparent")
        h2.pack(fill="x", padx=20, pady=(16, 12))
        ctk.CTkLabel(h2, text="Circulation Policies & Penalty Rates", font=Theme.FONT_SUBTITLE, text_color=Theme.TEXT_PRIMARY).pack(side="left")

        f2 = ctk.CTkFrame(card2, fg_color="transparent")
        f2.pack(fill="x", padx=20, pady=(0, 20))

        row_rules = ctk.CTkFrame(f2, fg_color="transparent")
        row_rules.pack(fill="x", pady=(0, 16))

        fine_col = ctk.CTkFrame(row_rules, fg_color="transparent")
        fine_col.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkLabel(fine_col, text="Daily Overdue Fine ($)", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(0, 2))
        self.fine_entry = ctk.CTkEntry(fine_col, fg_color=Theme.BG_INPUT, height=36)
        self.fine_entry.insert(0, SettingsService.get_setting("daily_fine_rate", "1.00"))
        self.fine_entry.pack(fill="x")

        period_col = ctk.CTkFrame(row_rules, fg_color="transparent")
        period_col.pack(side="left", fill="x", expand=True, padx=(8, 8))
        ctk.CTkLabel(period_col, text="Default Loan Period (Days)", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(0, 2))
        self.period_entry = ctk.CTkEntry(period_col, fg_color=Theme.BG_INPUT, height=36)
        self.period_entry.insert(0, SettingsService.get_setting("borrowing_period_days", "14"))
        self.period_entry.pack(fill="x")

        limit_col = ctk.CTkFrame(row_rules, fg_color="transparent")
        limit_col.pack(side="left", fill="x", expand=True, padx=(8, 0))
        ctk.CTkLabel(limit_col, text="Max Books Per Member", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(0, 2))
        self.limit_entry = ctk.CTkEntry(limit_col, fg_color=Theme.BG_INPUT, height=36)
        self.limit_entry.insert(0, SettingsService.get_setting("max_books_per_member", "5"))
        self.limit_entry.pack(fill="x")

        save_rules_btn = ctk.CTkButton(
            f2,
            text="Save Policy Rules",
            font=Theme.FONT_BODY_BOLD,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            text_color=Theme.TEXT_WHITE,
            height=36,
            command=self._save_rules_settings,
        )
        save_rules_btn.pack(anchor="w")

        # 3. Database Backup & Restore Card
        card3 = ctk.CTkFrame(self, fg_color=Theme.BG_CARD, border_color=Theme.BORDER, border_width=1, corner_radius=12)
        card3.pack(fill="x", padx=16, pady=(0, 16))

        h3 = ctk.CTkFrame(card3, fg_color="transparent")
        h3.pack(fill="x", padx=20, pady=(16, 12))
        ctk.CTkLabel(h3, text="Database Maintenance & Disaster Recovery", font=Theme.FONT_SUBTITLE, text_color=Theme.TEXT_PRIMARY).pack(side="left")

        f3 = ctk.CTkFrame(card3, fg_color="transparent")
        f3.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkLabel(
            f3,
            text="Take immediate snapshots of all library data or restore from a previous verified backup file.",
            font=Theme.FONT_BODY,
            text_color=Theme.TEXT_SECONDARY,
        ).pack(anchor="w", pady=(0, 14))

        b_row = ctk.CTkFrame(f3, fg_color="transparent")
        b_row.pack(fill="x")

        backup_now_btn = ctk.CTkButton(
            b_row,
            text="Create Backup Snapshot",
            font=Theme.FONT_BODY_BOLD,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            text_color=Theme.TEXT_WHITE,
            height=36,
            command=self._create_backup,
        )
        backup_now_btn.pack(side="left", padx=(0, 12))

        restore_btn = ctk.CTkButton(
            b_row,
            text="Restore from Backup File...",
            font=Theme.FONT_BODY_BOLD,
            fg_color=Theme.SECONDARY,
            hover_color=Theme.SECONDARY_HOVER,
            text_color=Theme.SECONDARY_TEXT,
            height=36,
            command=self._restore_backup,
        )
        restore_btn.pack(side="left")

        # 4. User Security & Password Change
        card4 = ctk.CTkFrame(self, fg_color=Theme.BG_CARD, border_color=Theme.BORDER, border_width=1, corner_radius=12)
        card4.pack(fill="x", padx=16, pady=(0, 24))

        h4 = ctk.CTkFrame(card4, fg_color="transparent")
        h4.pack(fill="x", padx=20, pady=(16, 12))
        ctk.CTkLabel(h4, text="Account Security & Access Control", font=Theme.FONT_SUBTITLE, text_color=Theme.TEXT_PRIMARY).pack(side="left")

        f4 = ctk.CTkFrame(card4, fg_color="transparent")
        f4.pack(fill="x", padx=20, pady=(0, 20))

        # Current user summary
        ctk.CTkLabel(
            f4,
            text=f"Logged in as: {self.current_user.full_name} ({self.current_user.username}) • Role: {self.current_user.role.upper()}",
            font=Theme.FONT_BODY_BOLD,
            text_color=Theme.PRIMARY,
        ).pack(anchor="w", pady=(0, 12))

        # Change Password Form
        pw_row = ctk.CTkFrame(f4, fg_color="transparent")
        pw_row.pack(fill="x", pady=(0, 12))

        old_col = ctk.CTkFrame(pw_row, fg_color="transparent")
        old_col.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkLabel(old_col, text="Current Password", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(0, 2))
        self.old_pw_entry = ctk.CTkEntry(old_col, show="•", fg_color=Theme.BG_INPUT, height=36)
        self.old_pw_entry.pack(fill="x")

        new_col = ctk.CTkFrame(pw_row, fg_color="transparent")
        new_col.pack(side="left", fill="x", expand=True, padx=(8, 0))
        ctk.CTkLabel(new_col, text="New Password", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(0, 2))
        self.new_pw_entry = ctk.CTkEntry(new_col, show="•", fg_color=Theme.BG_INPUT, height=36)
        self.new_pw_entry.pack(fill="x")

        chg_pw_btn = ctk.CTkButton(
            f4,
            text="Update Password",
            font=Theme.FONT_BODY_BOLD,
            fg_color=Theme.SECONDARY,
            hover_color=Theme.SECONDARY_HOVER,
            text_color=Theme.SECONDARY_TEXT,
            height=36,
            command=self._change_password,
        )
        chg_pw_btn.pack(anchor="w")

        # If Admin, show Add User box
        if self.current_user.role == "admin":
            admin_card = ctk.CTkFrame(f4, fg_color=Theme.BG_INPUT, corner_radius=8)
            admin_card.pack(fill="x", pady=(16, 0))

            ctk.CTkLabel(admin_card, text="Admin: Create New Staff Account", font=Theme.FONT_BODY_BOLD, text_color=Theme.TEXT_PRIMARY).pack(anchor="w", padx=16, pady=(12, 8))

            u_row = ctk.CTkFrame(admin_card, fg_color="transparent")
            u_row.pack(fill="x", padx=16, pady=(0, 12))

            self.new_username_entry = ctk.CTkEntry(u_row, placeholder_text="Username", height=34, width=140)
            self.new_username_entry.pack(side="left", padx=(0, 8))

            self.new_name_entry = ctk.CTkEntry(u_row, placeholder_text="Full Name", height=34, width=160)
            self.new_name_entry.pack(side="left", padx=(0, 8))

            self.new_user_pw = ctk.CTkEntry(u_row, placeholder_text="Password", show="•", height=34, width=140)
            self.new_user_pw.pack(side="left", padx=(0, 8))

            self.new_role_menu = ctk.CTkComboBox(u_row, values=["librarian", "admin"], height=34, width=110)
            self.new_role_menu.set("librarian")
            self.new_role_menu.pack(side="left", padx=(0, 8))

            create_u_btn = ctk.CTkButton(
                u_row,
                text="Create Staff",
                font=Theme.FONT_BODY_BOLD,
                fg_color=Theme.PRIMARY,
                hover_color=Theme.PRIMARY_HOVER,
                text_color=Theme.TEXT_WHITE,
                height=34,
                command=self._create_staff_user,
            )
            create_u_btn.pack(side="left")

    def _save_general_settings(self):
        SettingsService.update_settings({
            "library_name": self.name_entry.get().strip(),
            "library_email": self.email_entry.get().strip(),
            "library_phone": self.phone_entry.get().strip(),
            "library_address": self.addr_entry.get().strip(),
        })
        AlertDialog(self.winfo_toplevel(), "Saved", "General organization settings saved.", level="success")

    def _save_rules_settings(self):
        try:
            fine = float(self.fine_entry.get().strip())
            period = int(self.period_entry.get().strip())
            limit = int(self.limit_entry.get().strip())
            if fine < 0 or period <= 0 or limit <= 0:
                raise ValueError()
        except ValueError:
            AlertDialog(self.winfo_toplevel(), "Invalid Values", "Please enter positive numerical values for policies.", level="error")
            return

        SettingsService.update_settings({
            "daily_fine_rate": f"{fine:.2f}",
            "borrowing_period_days": str(period),
            "max_books_per_member": str(limit),
        })
        AlertDialog(self.winfo_toplevel(), "Saved", "Circulation rules updated successfully.", level="success")

    def _create_backup(self):
        ok, msg, path = BackupService.create_backup()
        if ok:
            AlertDialog(self.winfo_toplevel(), "Backup Created", msg, level="success")
        else:
            AlertDialog(self.winfo_toplevel(), "Backup Failed", msg, level="error")

    def _restore_backup(self):
        path = filedialog.askopenfilename(
            parent=self.winfo_toplevel(),
            filetypes=[("SQLite Databases", "*.sqlite *.db"), ("All files", "*.*")],
            title="Select Backup File to Restore",
        )
        if not path:
            return

        def do_restore():
            ok, msg = BackupService.restore_backup(path)
            if ok:
                AlertDialog(self.winfo_toplevel(), "Restored", f"{msg}\nPlease restart the application to reflect full restored data.", level="success")
            else:
                AlertDialog(self.winfo_toplevel(), "Restore Failed", msg, level="error")

        ConfirmDialog(
            self.winfo_toplevel(),
            title="Restore Confirmation",
            message=f"Are you sure you want to restore database from:\n{path}?\n\nCurrent database will be overwritten with the backup state.",
            on_confirm=do_restore,
            confirm_text="Restore Now",
            danger=True,
        )

    def _change_password(self):
        old_p = self.old_pw_entry.get().strip()
        new_p = self.new_pw_entry.get().strip()
        if not old_p or not new_p:
            AlertDialog(self.winfo_toplevel(), "Error", "Please fill in both password fields.", level="error")
            return

        ok, msg = AuthService.change_password(self.current_user.id, old_p, new_p)
        if ok:
            AlertDialog(self.winfo_toplevel(), "Password Updated", msg, level="success")
            self.old_pw_entry.delete(0, "end")
            self.new_pw_entry.delete(0, "end")
        else:
            AlertDialog(self.winfo_toplevel(), "Error", msg, level="error")

    def _create_staff_user(self):
        u = self.new_username_entry.get().strip()
        name = self.new_name_entry.get().strip()
        p = self.new_user_pw.get().strip()
        r = self.new_role_menu.get()

        ok, msg = AuthService.create_user(u, p, name, r)
        if ok:
            AlertDialog(self.winfo_toplevel(), "Staff Created", msg, level="success")
            self.new_username_entry.delete(0, "end")
            self.new_name_entry.delete(0, "end")
            self.new_user_pw.delete(0, "end")
        else:
            AlertDialog(self.winfo_toplevel(), "Error", msg, level="error")
