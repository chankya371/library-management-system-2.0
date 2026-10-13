import datetime
from typing import List, Optional, Tuple, Dict, Any
from database.db_connection import get_db_cursor
from models.issue import IssueRecord
from services.settings_service import SettingsService


class CirculationService:
    """Handles book checkout, check-in, loan extensions, and fine computations."""

    @staticmethod
    def sync_overdue_statuses() -> int:
        """
        Updates active loan records that have passed due date to 'Overdue' status
        and calculates accrued fines. Returns count of updated records.
        """
        today = datetime.date.today().isoformat()
        daily_rate = SettingsService.get_daily_fine_rate()
        updated_count = 0

        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT id, due_date, fine_amount, fine_paid 
                FROM issue_records 
                WHERE status IN ('Issued', 'Overdue') AND due_date < ?;
                """,
                (today,),
            )
            rows = cursor.fetchall()
            for r in rows:
                due = datetime.date.fromisoformat(r["due_date"])
                overdue_days = (datetime.date.today() - due).days
                current_fine = round(max(0, overdue_days * daily_rate), 2)

                cursor.execute(
                    """
                    UPDATE issue_records 
                    SET status = 'Overdue', fine_amount = ? 
                    WHERE id = ?;
                    """,
                    (current_fine, r["id"]),
                )
                updated_count += 1

        return updated_count

    @staticmethod
    def issue_book(
        book_id: int,
        member_id: int,
        issue_date: Optional[str] = None,
        due_date: Optional[str] = None,
        notes: str = "",
    ) -> Tuple[bool, str, Optional[int]]:
        """
        Issues a book to a member using an atomic SQLite transaction.
        Checks:
        - Member exists & is Active
        - Book exists & has available copies > 0
        - Member has not reached max borrowing limit
        - Member does not already have this exact book currently issued
        """
        today = datetime.date.today()
        iss_date = issue_date if issue_date else today.isoformat()

        if not due_date:
            period = SettingsService.get_borrowing_period_days()
            due_date = (today + datetime.timedelta(days=period)).isoformat()

        max_allowed = SettingsService.get_max_books_per_member()

        with get_db_cursor() as cursor:
            # 1. Member check
            cursor.execute("SELECT id, full_name, status FROM members WHERE id = ?;", (member_id,))
            member = cursor.fetchone()
            if not member:
                return False, "Selected member not found.", None
            if member["status"] != "Active":
                return False, f"Cannot issue book: Member '{member['full_name']}' status is '{member['status']}'.", None

            # 2. Member active loans limit check
            cursor.execute(
                """
                SELECT COUNT(*) FROM issue_records 
                WHERE member_id = ? AND status IN ('Issued', 'Overdue');
                """,
                (member_id,),
            )
            active_count = cursor.fetchone()[0]
            if active_count >= max_allowed:
                return (
                    False,
                    f"Member '{member['full_name']}' has reached the maximum borrowing limit of {max_allowed} books.",
                    None,
                )

            # 3. Check if member already has an active loan of the same book
            cursor.execute(
                """
                SELECT COUNT(*) FROM issue_records 
                WHERE member_id = ? AND book_id = ? AND status IN ('Issued', 'Overdue');
                """,
                (member_id, book_id),
            )
            if cursor.fetchone()[0] > 0:
                return False, "This member already has an active copy of this book on loan.", None

            # 4. Book availability check
            cursor.execute("SELECT id, title, available_copies FROM books WHERE id = ?;", (book_id,))
            book = cursor.fetchone()
            if not book:
                return False, "Selected book not found.", None
            if book["available_copies"] <= 0:
                return False, f"No copies available for '{book['title']}'.", None

            # 5. Atomic Transaction: Decrement available_copies and insert issue_record
            cursor.execute(
                """
                UPDATE books 
                SET available_copies = available_copies - 1 
                WHERE id = ? AND available_copies > 0;
                """,
                (book_id,),
            )
            if cursor.rowcount == 0:
                return False, "Book copy became unavailable. Transaction aborted.", None

            cursor.execute(
                """
                INSERT INTO issue_records (book_id, member_id, issue_date, due_date, status, notes, fine_amount, fine_paid)
                VALUES (?, ?, ?, ?, 'Issued', ?, 0.0, 0);
                """,
                (book_id, member_id, iss_date, due_date, notes.strip() if notes else ""),
            )
            new_issue_id = cursor.lastrowid

        return True, f"Book '{book['title']}' issued successfully to {member['full_name']}.", new_issue_id

    @staticmethod
    def return_book(
        issue_id: int,
        return_date: Optional[str] = None,
        notes: str = "",
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Processes a book return transaction:
        - Validates record is active
        - Calculates overdue fine if returned after due date
        - Updates issue_records status to 'Returned'
        - Increments book available_copies atomically
        """
        CirculationService.sync_overdue_statuses()
        ret_date = return_date if return_date else datetime.date.today().isoformat()
        daily_rate = SettingsService.get_daily_fine_rate()

        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT ir.*, b.title as book_title, b.id as b_id, m.full_name as member_name, m.id as m_id
                FROM issue_records ir
                JOIN books b ON ir.book_id = b.id
                JOIN members m ON ir.member_id = m.id
                WHERE ir.id = ?;
                """,
                (issue_id,),
            )
            record = cursor.fetchone()
            if not record:
                return False, "Circulation record not found.", {}

            if record["status"] == "Returned":
                return False, "This book has already been returned.", {}

            due_dt = datetime.date.fromisoformat(record["due_date"])
            ret_dt = datetime.date.fromisoformat(ret_date.split()[0])
            overdue_days = max(0, (ret_dt - due_dt).days)
            fine_amount = round(overdue_days * daily_rate, 2) if overdue_days > 0 else 0.0

            # Atomic transaction: update issue record and increment book stock
            cursor.execute(
                """
                UPDATE issue_records
                SET return_date = ?, status = 'Returned', fine_amount = ?, notes = CASE 
                    WHEN notes IS NULL OR notes = '' THEN ? 
                    ELSE notes || ' | ' || ? 
                END
                WHERE id = ?;
                """,
                (
                    ret_date,
                    fine_amount,
                    notes.strip() if notes else f"Returned on {ret_date}",
                    notes.strip() if notes else f"Returned on {ret_date}",
                    issue_id,
                ),
            )

            cursor.execute(
                """
                UPDATE books
                SET available_copies = available_copies + 1
                WHERE id = ?;
                """,
                (record["b_id"],),
            )

            summary = {
                "issue_id": issue_id,
                "book_id": record["b_id"],
                "book_title": record["book_title"],
                "member_id": record["m_id"],
                "member_name": record["member_name"],
                "issue_date": record["issue_date"],
                "due_date": record["due_date"],
                "return_date": ret_date,
                "overdue_days": overdue_days,
                "fine_amount": fine_amount,
            }

        msg = f"Book '{record['book_title']}' returned successfully."
        if fine_amount > 0:
            msg += f" Overdue by {overdue_days} days. Fine calculated: ${fine_amount:.2f}."

        return True, msg, summary

    @staticmethod
    def get_issue_by_id(issue_id: int) -> Optional[IssueRecord]:
        with get_db_cursor(commit=False) as cursor:
            cursor.execute(
                """
                SELECT ir.*, b.title as book_title, b.isbn as book_isbn,
                       m.full_name as member_name, m.member_code as member_code
                FROM issue_records ir
                JOIN books b ON ir.book_id = b.id
                JOIN members m ON ir.member_id = m.id
                WHERE ir.id = ?;
                """,
                (issue_id,),
            )
            row = cursor.fetchone()
            return IssueRecord.from_row(row) if row else None

    @staticmethod
    def search_issues(
        status: str = "All",
        query: str = "",
        member_id: Optional[int] = None,
        book_id: Optional[int] = None,
    ) -> List[IssueRecord]:
        CirculationService.sync_overdue_statuses()

        sql = """
            SELECT ir.*, b.title as book_title, b.isbn as book_isbn,
                   m.full_name as member_name, m.member_code as member_code
            FROM issue_records ir
            JOIN books b ON ir.book_id = b.id
            JOIN members m ON ir.member_id = m.id
            WHERE 1=1
        """
        params = []

        if status and status != "All":
            sql += " AND ir.status = ?"
            params.append(status)

        if member_id:
            sql += " AND ir.member_id = ?"
            params.append(member_id)

        if book_id:
            sql += " AND ir.book_id = ?"
            params.append(book_id)

        if query and query.strip():
            term = f"%{query.strip()}%"
            sql += " AND (b.title LIKE ? OR b.isbn LIKE ? OR m.full_name LIKE ? OR m.member_code LIKE ? OR ir.id LIKE ?)"
            params.extend([term, term, term, term, term])

        sql += " ORDER BY CASE ir.status WHEN 'Overdue' THEN 1 WHEN 'Issued' THEN 2 ELSE 3 END, ir.id DESC;"

        with get_db_cursor(commit=False) as cursor:
            cursor.execute(sql, params)
            return [IssueRecord.from_row(r) for r in cursor.fetchall()]
