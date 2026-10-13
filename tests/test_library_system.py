import os
import sys
import unittest
import tempfile
import datetime

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_connection import set_db_path, get_connection
from database.schema import initialize_database
from database.seed_data import seed_database
from services.auth_service import AuthService
from services.book_service import BookService
from services.member_service import MemberService
from services.circulation_service import CirculationService
from services.fine_service import FineService
from services.report_service import ReportService
from services.backup_service import BackupService
from services.settings_service import SettingsService
from utils.validators import validate_isbn, validate_email, validate_phone


class LibrarySystemTestSuite(unittest.TestCase):
    """Comprehensive test suite verifying business logic, constraints, and data integrity."""

    @classmethod
    def setUpClass(cls):
        # Create an isolated temporary test database
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.test_db_path = os.path.join(cls.temp_dir.name, "test_library.db")
        set_db_path(cls.test_db_path)
        initialize_database(cls.test_db_path)
        seed_database(cls.test_db_path)

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    # --- 1. Authentication Tests ---
    def test_auth_success(self):
        admin = AuthService.authenticate("admin", "admin123")
        self.assertIsNotNone(admin)
        self.assertEqual(admin.username, "admin")
        self.assertEqual(admin.role, "admin")

        librarian = AuthService.authenticate("librarian", "lib123")
        self.assertIsNotNone(librarian)
        self.assertEqual(librarian.role, "librarian")

    def test_auth_failure(self):
        self.assertIsNone(AuthService.authenticate("admin", "wrongpassword"))
        self.assertIsNone(AuthService.authenticate("nonexistent", "admin123"))

    def test_user_creation_and_password_change(self):
        ok, msg = AuthService.create_user("staff_clerk", "clerk123", "Alice Clerk", "librarian")
        self.assertTrue(ok)

        # Cannot create duplicate username
        ok2, _ = AuthService.create_user("staff_clerk", "clerk123", "Alice Clerk", "librarian")
        self.assertFalse(ok2)

        user = AuthService.authenticate("staff_clerk", "clerk123")
        self.assertIsNotNone(user)

        # Change password
        ok_chg, _ = AuthService.change_password(user.id, "clerk123", "newpassword123")
        self.assertTrue(ok_chg)
        self.assertIsNotNone(AuthService.authenticate("staff_clerk", "newpassword123"))

    # --- 2. Validation Tests ---
    def test_isbn_validation(self):
        self.assertTrue(validate_isbn("978-0132350884")[0]) # Valid 13-digit
        self.assertTrue(validate_isbn("0451524934")[0])     # Valid 10-digit
        self.assertFalse(validate_isbn("12345")[0])         # Too short
        self.assertFalse(validate_isbn("978-0132350885")[0]) # Invalid checksum

    def test_email_and_phone_validation(self):
        self.assertTrue(validate_email("test.user@library.org")[0])
        self.assertFalse(validate_email("invalid-email-format")[0])

        self.assertTrue(validate_phone("+1 (555) 901-2341")[0])
        self.assertFalse(validate_phone("abc12")[0])

    # --- 3. Book Management Tests ---
    def test_add_and_update_book(self):
        isbn = "978-0321125217"
        ok, msg, book_id = BookService.add_book(
            isbn=isbn,
            title="Refactoring: Improving the Design of Existing Code",
            author="Martin Fowler",
            category="Computer Science",
            publisher="Addison-Wesley",
            publication_year=1999,
            total_copies=4,
            shelf_number="CS-F-01",
        )
        self.assertTrue(ok, msg)
        self.assertIsNotNone(book_id)

        book = BookService.get_book_by_id(book_id)
        self.assertEqual(book.title, "Refactoring: Improving the Design of Existing Code")
        self.assertEqual(book.available_copies, 4)

        # Update total copies
        ok_upd, msg_upd = BookService.update_book(
            book_id=book_id,
            isbn=isbn,
            title="Refactoring: 2nd Edition",
            author="Martin Fowler",
            category="Computer Science",
            total_copies=5,
        )
        self.assertTrue(ok_upd, msg_upd)
        updated = BookService.get_book_by_id(book_id)
        self.assertEqual(updated.title, "Refactoring: 2nd Edition")
        self.assertEqual(updated.total_copies, 5)
        self.assertEqual(updated.available_copies, 5)

    def test_delete_book_protection(self):
        # Clean Code (ID 1) has active loans in seed data
        ok, msg = BookService.delete_book(1)
        self.assertFalse(ok)
        self.assertIn("active", msg.lower())

    # --- 4. Member Management Tests ---
    def test_member_registration_and_duplicate_prevention(self):
        ok, msg, m_id = MemberService.register_member(
            full_name="Jonathan Archer",
            email="j.archer@enterprise.org",
            phone="+1 (555) 170-1701",
            membership_type="Faculty",
        )
        self.assertTrue(ok, msg)

        # Duplicate email prevention
        ok_dup, msg_dup, _ = MemberService.register_member(
            full_name="Jonathan Duplicate",
            email="j.archer@enterprise.org",
            phone="+1 (555) 170-1702",
        )
        self.assertFalse(ok_dup)
        self.assertIn("already exists", msg_dup)

    def test_member_delete_protection(self):
        # Member 1 (Sophia Chen) has active loan in seed data
        ok, msg = MemberService.delete_member(1)
        self.assertFalse(ok)
        self.assertIn("unreturned", msg.lower())

    # --- 5. Circulation & Inventory Tests ---
    def test_issue_and_return_book(self):
        # Add a fresh book
        isbn = "978-0134494166"
        ok_b, _, b_id = BookService.add_book(
            isbn=isbn,
            title="Clean Architecture",
            author="Robert C. Martin",
            category="Computer Science",
            total_copies=2,
        )
        self.assertTrue(ok_b)

        # Register a member
        ok_m, _, m_id = MemberService.register_member(
            full_name="Grace Hopper",
            email="grace.hopper@navy.mil",
            phone="+1 (555) 444-1234",
            status="Active",
        )
        self.assertTrue(ok_m)

        # 1. Issue book
        ok_iss, msg_iss, iss_id = CirculationService.issue_book(
            book_id=b_id,
            member_id=m_id,
            notes="Initial checkout",
        )
        self.assertTrue(ok_iss, msg_iss)

        # Verify book copy decreased
        b_after = BookService.get_book_by_id(b_id)
        self.assertEqual(b_after.available_copies, 1)

        # 2. Cannot issue duplicate copy to same member
        ok_dup, msg_dup, _ = CirculationService.issue_book(
            book_id=b_id,
            member_id=m_id,
        )
        self.assertFalse(ok_dup)

        # 3. Return book
        ok_ret, msg_ret, summary = CirculationService.return_book(
            issue_id=iss_id,
            return_date=datetime.date.today().isoformat(),
        )
        self.assertTrue(ok_ret, msg_ret)
        self.assertEqual(summary["fine_amount"], 0.0) # On time

        # Verify book copy restored
        b_restored = BookService.get_book_by_id(b_id)
        self.assertEqual(b_restored.available_copies, 2)

    def test_overdue_fine_calculation(self):
        # Add book and member
        _, _, b_id = BookService.add_book(
            isbn="978-0131103627",
            title="The C Programming Language",
            author="Brian W. Kernighan, Dennis M. Ritchie",
            category="Computer Science",
            total_copies=1,
        )
        _, _, m_id = MemberService.register_member(
            full_name="Ken Thompson",
            email="ken@bell-labs.com",
            phone="+1 (555) 777-8888",
        )

        today = datetime.date.today()
        past_issue = (today - datetime.timedelta(days=20)).isoformat()
        past_due = (today - datetime.timedelta(days=6)).isoformat()

        # Issue with past due date (6 days overdue)
        ok_iss, _, iss_id = CirculationService.issue_book(
            book_id=b_id,
            member_id=m_id,
            issue_date=past_issue,
            due_date=past_due,
        )
        self.assertTrue(ok_iss)

        # Return today -> 6 days overdue, at $1.00/day = $6.00 fine
        ok_ret, _, summary = CirculationService.return_book(
            issue_id=iss_id,
            return_date=today.isoformat(),
        )
        self.assertTrue(ok_ret)
        self.assertEqual(summary["overdue_days"], 6)
        self.assertEqual(summary["fine_amount"], 6.00)

        # Settle fine payment
        ok_pay, msg_pay, receipt_no = FineService.pay_fine(
            issue_id=iss_id,
            member_id=m_id,
            amount=6.00,
            payment_method="Cash",
        )
        self.assertTrue(ok_pay, msg_pay)
        self.assertTrue(receipt_no.startswith("REC-"))

    # --- 6. Reports & Export Tests ---
    def test_reports_and_export(self):
        summary = ReportService.get_dashboard_summary()
        self.assertGreater(summary["total_books"], 0)
        self.assertGreater(summary["total_members"], 0)

        # Export CSV
        csv_file = os.path.join(self.temp_dir.name, "test_export.csv")
        ok_csv, msg_csv = ReportService.export_to_csv(
            csv_file,
            ["Col1", "Col2"],
            [["Val1", "Val2"], ["Val3", "Val4"]],
        )
        self.assertTrue(ok_csv, msg_csv)
        self.assertTrue(os.path.exists(csv_file))

        # Export Excel
        xlsx_file = os.path.join(self.temp_dir.name, "test_export.xlsx")
        ok_xlsx, msg_xlsx = ReportService.export_to_excel(
            xlsx_file,
            "SheetTest",
            ["Col1", "Col2"],
            [["Val1", "Val2"], ["Val3", "Val4"]],
        )
        self.assertTrue(ok_xlsx, msg_xlsx)
        self.assertTrue(os.path.exists(xlsx_file))

    # --- 7. Backup and Restore Tests ---
    def test_backup_and_restore(self):
        ok_bk, msg_bk, path = BackupService.create_backup()
        self.assertTrue(ok_bk, msg_bk)
        self.assertTrue(os.path.exists(path))

        # Verify backup list
        backups = BackupService.list_backups()
        self.assertGreater(len(backups), 0)

        # Test restore
        ok_res, msg_res = BackupService.restore_backup(path)
        self.assertTrue(ok_res, msg_res)


if __name__ == "__main__":
    unittest.main(verbosity=2)
