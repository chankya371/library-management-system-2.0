import sqlite3
from typing import List, Optional, Tuple, Dict, Any
from database.db_connection import get_db_cursor
from models.member import Member
from models.issue import IssueRecord
from utils.validators import validate_email, validate_phone, validate_non_empty


class MemberService:
    """Manages member registration, status, profile records, and validations."""

    @staticmethod
    def get_all_members() -> List[Member]:
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("SELECT * FROM members ORDER BY id DESC;")
            return [Member.from_row(r) for r in cursor.fetchall()]

    @staticmethod
    def get_member_by_id(member_id: int) -> Optional[Member]:
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("SELECT * FROM members WHERE id = ?;", (member_id,))
            row = cursor.fetchone()
            return Member.from_row(row) if row else None

    @staticmethod
    def get_member_by_code(code: str) -> Optional[Member]:
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("SELECT * FROM members WHERE member_code = ? COLLATE NOCASE;", (code.strip(),))
            row = cursor.fetchone()
            return Member.from_row(row) if row else None

    @staticmethod
    def get_member_by_email(email: str) -> Optional[Member]:
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("SELECT * FROM members WHERE email = ? COLLATE NOCASE;", (email.strip(),))
            row = cursor.fetchone()
            return Member.from_row(row) if row else None

    @staticmethod
    def generate_next_member_code() -> str:
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("SELECT member_code FROM members ORDER BY id DESC LIMIT 1;")
            row = cursor.fetchone()
            if row and row["member_code"].startswith("MEM-"):
                try:
                    num = int(row["member_code"].replace("MEM-", ""))
                    return f"MEM-{num + 1}"
                except ValueError:
                    pass
            cursor.execute("SELECT COUNT(*) FROM members;")
            cnt = cursor.fetchone()[0]
            return f"MEM-{1001 + cnt}"

    @staticmethod
    def register_member(
        full_name: str,
        email: str,
        phone: str,
        address: str = "",
        membership_type: str = "Standard",
        status: str = "Active",
        member_code: Optional[str] = None,
    ) -> Tuple[bool, str, Optional[int]]:
        valid_name, err = validate_non_empty(full_name, "Full Name")
        if not valid_name:
            return False, err, None

        valid_mail, err = validate_email(email)
        if not valid_mail:
            return False, err, None

        valid_ph, err = validate_phone(phone)
        if not valid_ph:
            return False, err, None

        if membership_type not in ("Student", "Faculty", "Standard", "Premium"):
            membership_type = "Standard"
        if status not in ("Active", "Inactive", "Suspended"):
            status = "Active"

        code = member_code if member_code else MemberService.generate_next_member_code()
        clean_name = full_name.strip()
        clean_email = email.strip()
        clean_phone = phone.strip()
        clean_address = address.strip() if address else ""

        try:
            with get_db_cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO members (member_code, full_name, email, phone, address, membership_type, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?);
                    """,
                    (code, clean_name, clean_email, clean_phone, clean_address, membership_type, status),
                )
                new_id = cursor.lastrowid
            return True, "Member registered successfully.", new_id
        except sqlite3.IntegrityError as e:
            if "email" in str(e).lower():
                return False, f"A member with email '{clean_email}' already exists.", None
            if "member_code" in str(e).lower():
                return False, f"A member with code '{code}' already exists.", None
            return False, "Duplicate member details found.", None
        except Exception as e:
            return False, f"Database error: {str(e)}", None

    @staticmethod
    def update_member(
        member_id: int,
        full_name: str,
        email: str,
        phone: str,
        address: str = "",
        membership_type: str = "Standard",
        status: str = "Active",
    ) -> Tuple[bool, str]:
        valid_name, err = validate_non_empty(full_name, "Full Name")
        if not valid_name:
            return False, err

        valid_mail, err = validate_email(email)
        if not valid_mail:
            return False, err

        valid_ph, err = validate_phone(phone)
        if not valid_ph:
            return False, err

        clean_name = full_name.strip()
        clean_email = email.strip()
        clean_phone = phone.strip()
        clean_address = address.strip() if address else ""

        try:
            with get_db_cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE members
                    SET full_name = ?, email = ?, phone = ?, address = ?, membership_type = ?, status = ?
                    WHERE id = ?;
                    """,
                    (clean_name, clean_email, clean_phone, clean_address, membership_type, status, member_id),
                )
            return True, "Member information updated successfully."
        except sqlite3.IntegrityError:
            return False, f"Another member is already registered with email '{clean_email}'."
        except Exception as e:
            return False, f"Database error: {str(e)}"

    @staticmethod
    def delete_member(member_id: int) -> Tuple[bool, str]:
        # Safety checks:
        with get_db_cursor() as cursor:
            # 1. Unreturned books check
            cursor.execute(
                """
                SELECT COUNT(*) FROM issue_records 
                WHERE member_id = ? AND status IN ('Issued', 'Overdue');
                """,
                (member_id,),
            )
            active_loans = cursor.fetchone()[0]
            if active_loans > 0:
                return (
                    False,
                    f"Cannot delete member: Member has {active_loans} unreturned book(s) on loan.",
                )

            # 2. Unpaid fines check
            cursor.execute(
                """
                SELECT COUNT(*) FROM issue_records 
                WHERE member_id = ? AND fine_amount > 0 AND fine_paid = 0;
                """,
                (member_id,),
            )
            unpaid_fines = cursor.fetchone()[0]
            if unpaid_fines > 0:
                return (
                    False,
                    "Cannot delete member: Member has pending unpaid fines. Please clear fines first.",
                )

            # 3. Check historical records
            cursor.execute(
                "SELECT COUNT(*) FROM issue_records WHERE member_id = ?;",
                (member_id,),
            )
            has_history = cursor.fetchone()[0]
            if has_history > 0:
                return (
                    False,
                    "Cannot delete member: Member has historical borrowing records. You can set status to 'Inactive' instead.",
                )

            cursor.execute("DELETE FROM members WHERE id = ?;", (member_id,))
            return True, "Member deleted successfully."

    @staticmethod
    def get_member_profile(member_id: int) -> Dict[str, Any]:
        """Returns comprehensive profile metrics and history for a member."""
        member = MemberService.get_member_by_id(member_id)
        if not member:
            return {}

        with get_db_cursor(commit=False) as cursor:
            # Current active issues
            cursor.execute(
                """
                SELECT ir.*, b.title as book_title, b.isbn as book_isbn 
                FROM issue_records ir
                JOIN books b ON ir.book_id = b.id
                WHERE ir.member_id = ? AND ir.status IN ('Issued', 'Overdue')
                ORDER BY ir.due_date ASC;
                """,
                (member_id,),
            )
            active_loans = [IssueRecord.from_row(r) for r in cursor.fetchall()]

            # Historical issues
            cursor.execute(
                """
                SELECT ir.*, b.title as book_title, b.isbn as book_isbn 
                FROM issue_records ir
                JOIN books b ON ir.book_id = b.id
                WHERE ir.member_id = ? AND ir.status = 'Returned'
                ORDER BY ir.return_date DESC LIMIT 20;
                """,
                (member_id,),
            )
            past_loans = [IssueRecord.from_row(r) for r in cursor.fetchall()]

            # Pending fines
            cursor.execute(
                """
                SELECT COALESCE(SUM(fine_amount), 0.0) 
                FROM issue_records 
                WHERE member_id = ? AND fine_amount > 0 AND fine_paid = 0;
                """,
                (member_id,),
            )
            pending_fines = cursor.fetchone()[0]

            # Paid fines
            cursor.execute(
                """
                SELECT COALESCE(SUM(amount_paid), 0.0) 
                FROM fine_payments 
                WHERE member_id = ?;
                """,
                (member_id,),
            )
            paid_fines = cursor.fetchone()[0]

            return {
                "member": member,
                "active_loans": active_loans,
                "past_loans": past_loans,
                "active_loans_count": len(active_loans),
                "total_borrowed_count": len(active_loans) + len(past_loans),
                "pending_fines": pending_fines,
                "paid_fines": paid_fines,
            }

    @staticmethod
    def search_members(
        query: str = "",
        membership_type: str = "All",
        status: str = "All",
    ) -> List[Member]:
        sql = "SELECT * FROM members WHERE 1=1"
        params = []

        if query and query.strip():
            term = f"%{query.strip()}%"
            sql += " AND (full_name LIKE ? OR email LIKE ? OR phone LIKE ? OR member_code LIKE ?)"
            params.extend([term, term, term, term])

        if membership_type and membership_type != "All":
            sql += " AND membership_type = ?"
            params.append(membership_type)

        if status and status != "All":
            sql += " AND status = ?"
            params.append(status)

        sql += " ORDER BY full_name ASC;"

        with get_db_cursor(commit=False) as cursor:
            cursor.execute(sql, params)
            return [Member.from_row(r) for r in cursor.fetchall()]
