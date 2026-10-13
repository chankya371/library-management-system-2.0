import datetime
import random
from typing import List, Optional, Tuple, Dict, Any
from database.db_connection import get_db_cursor
from models.fine import FinePayment
from services.circulation_service import CirculationService


class FineService:
    """Manages fine computation, payment collections, and receipt tracking."""

    @staticmethod
    def generate_receipt_number() -> str:
        date_str = datetime.date.today().strftime("%Y%m%d")
        rand_suffix = random.randint(1000, 9999)
        return f"REC-{date_str}-{rand_suffix}"

    @staticmethod
    def get_all_fine_records(filter_status: str = "All", query: str = "") -> List[Dict[str, Any]]:
        """
        Returns combined records of both pending fines from active/returned issues
        and paid fines.
        """
        CirculationService.sync_overdue_statuses()

        sql = """
            SELECT ir.id as issue_id, ir.fine_amount, ir.fine_paid, ir.due_date, ir.return_date, ir.status as issue_status,
                   m.id as member_id, m.full_name as member_name, m.member_code,
                   b.title as book_title,
                   fp.receipt_number, fp.payment_date, fp.payment_method
            FROM issue_records ir
            JOIN members m ON ir.member_id = m.id
            JOIN books b ON ir.book_id = b.id
            LEFT JOIN fine_payments fp ON ir.id = fp.issue_id
            WHERE ir.fine_amount > 0
        """
        params = []

        if filter_status == "Pending":
            sql += " AND ir.fine_paid = 0"
        elif filter_status == "Paid":
            sql += " AND ir.fine_paid = 1"

        if query and query.strip():
            term = f"%{query.strip()}%"
            sql += " AND (m.full_name LIKE ? OR m.member_code LIKE ? OR b.title LIKE ? OR fp.receipt_number LIKE ?)"
            params.extend([term, term, term, term])

        sql += " ORDER BY ir.fine_paid ASC, ir.id DESC;"

        with get_db_cursor(commit=False) as cursor:
            cursor.execute(sql, params)
            return [dict(r) for r in cursor.fetchall()]

    @staticmethod
    def pay_fine(
        issue_id: int,
        member_id: int,
        amount: float,
        payment_method: str = "Cash",
        notes: str = "",
    ) -> Tuple[bool, str, Optional[str]]:
        if amount <= 0:
            return False, "Payment amount must be greater than zero.", None

        receipt_no = FineService.generate_receipt_number()

        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT id, fine_amount, fine_paid FROM issue_records WHERE id = ?;",
                (issue_id,),
            )
            issue = cursor.fetchone()
            if not issue:
                return False, "Issue record not found.", None

            if issue["fine_paid"] == 1:
                return False, "This fine has already been marked as paid.", None

            # Insert payment
            cursor.execute(
                """
                INSERT INTO fine_payments (issue_id, member_id, amount_paid, payment_method, receipt_number, notes)
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                (issue_id, member_id, amount, payment_method, receipt_no, notes.strip() if notes else "Full fine payment"),
            )

            # Mark issue fine as paid
            cursor.execute(
                "UPDATE issue_records SET fine_paid = 1 WHERE id = ?;",
                (issue_id,),
            )

        return True, f"Fine payment of ${amount:.2f} processed successfully. Receipt #{receipt_no}", receipt_no

    @staticmethod
    def get_fine_totals() -> Tuple[float, float]:
        """Returns (total_fines_collected, total_fines_pending)."""
        CirculationService.sync_overdue_statuses()
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("SELECT COALESCE(SUM(amount_paid), 0.0) FROM fine_payments;")
            collected = float(cursor.fetchone()[0])

            cursor.execute("SELECT COALESCE(SUM(fine_amount), 0.0) FROM issue_records WHERE fine_paid = 0;")
            pending = float(cursor.fetchone()[0])

            return collected, pending
