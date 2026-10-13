import datetime
from typing import Dict, Any


class ReceiptGenerator:
    """Generates clean, professional textual and printable receipts for library transactions."""

    @staticmethod
    def generate_issue_receipt(
        issue_id: int,
        member_name: str,
        member_code: str,
        book_title: str,
        book_isbn: str,
        issue_date: str,
        due_date: str,
        library_name: str = "Alexandria Modern Library",
    ) -> str:
        border = "=" * 46
        divider = "-" * 46
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return f"""{border}
          {library_name.upper()}
               CIRCULATION RECEIPT
{border}
Date Issued   : {now}
Transaction ID: #ISS-{issue_id:06d}

BORROWER DETAILS:
  Name        : {member_name}
  Member ID   : {member_code}

BOOK DETAILS:
  Title       : {book_title[:32]}
  ISBN        : {book_isbn}

TERMS:
  Issue Date  : {issue_date}
  Due Date    : {due_date}

{divider}
* Please return on or before the due date.
* Daily overdue fines apply for late returns.
{border}
"""

    @staticmethod
    def generate_return_receipt(
        summary: Dict[str, Any],
        library_name: str = "Alexandria Modern Library",
    ) -> str:
        border = "=" * 46
        divider = "-" * 46
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        fine = summary.get("fine_amount", 0.0)
        overdue_days = summary.get("overdue_days", 0)

        fine_status = f"${fine:.2f} (PAID)" if fine > 0 else "$0.00 (NONE)"

        return f"""{border}
          {library_name.upper()}
                BOOK RETURN RECEIPT
{border}
Processed On  : {now}
Issue ID      : #ISS-{summary.get('issue_id', 0):06d}

BORROWER:
  Name        : {summary.get('member_name', '')}
  
ITEM RETURNED:
  Title       : {str(summary.get('book_title', ''))[:32]}
  Due Date    : {summary.get('due_date', '')}
  Return Date : {summary.get('return_date', '')}

CIRCULATION AUDIT:
  Overdue Days: {overdue_days} days
  Fine Accrued: {fine_status}

{divider}
Thank you for returning your library material.
{border}
"""

    @staticmethod
    def generate_fine_receipt(
        receipt_number: str,
        member_name: str,
        member_code: str,
        amount_paid: float,
        payment_method: str,
        book_title: str,
        notes: str = "",
        library_name: str = "Alexandria Modern Library",
    ) -> str:
        border = "=" * 46
        divider = "-" * 46
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return f"""{border}
          {library_name.upper()}
              OFFICIAL PAYMENT RECEIPT
{border}
Receipt No    : {receipt_number}
Date & Time   : {now}
Payment Mode  : {payment_method.upper()}

PAYEE DETAILS:
  Member Name : {member_name}
  Member ID   : {member_code}

SETTLEMENT SUMMARY:
  Description : Overdue Library Loan Fine
  Book Title  : {book_title[:30]}
  Amount Paid : ${amount_paid:.2f} USD
  Notes       : {notes or 'Full settlement'}

Status        : COMPLETED & CLEARED
{divider}
This is an authorized computer-generated receipt.
{border}
"""
