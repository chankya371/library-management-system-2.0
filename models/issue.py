from dataclasses import dataclass
from typing import Optional
import datetime


@dataclass
class IssueRecord:
    id: Optional[int]
    book_id: int
    member_id: int
    issue_date: str
    due_date: str
    return_date: Optional[str] = None
    status: str = "Issued"  # 'Issued', 'Returned', 'Overdue'
    notes: Optional[str] = ""
    fine_amount: float = 0.0
    fine_paid: int = 0
    created_at: Optional[str] = None

    # Joined fields for convenience
    book_title: Optional[str] = None
    book_isbn: Optional[str] = None
    member_name: Optional[str] = None
    member_code: Optional[str] = None

    @classmethod
    def from_row(cls, row) -> "IssueRecord":
        if row is None:
            return None
        keys = row.keys()
        return cls(
            id=row["id"],
            book_id=row["book_id"],
            member_id=row["member_id"],
            issue_date=row["issue_date"],
            due_date=row["due_date"],
            return_date=row["return_date"],
            status=row["status"],
            notes=row["notes"] if row["notes"] else "",
            fine_amount=float(row["fine_amount"]) if row["fine_amount"] else 0.0,
            fine_paid=int(row["fine_paid"]) if row["fine_paid"] else 0,
            created_at=row["created_at"] if "created_at" in keys else None,
            book_title=row["book_title"] if "book_title" in keys else None,
            book_isbn=row["book_isbn"] if "book_isbn" in keys else None,
            member_name=row["member_name"] if "member_name" in keys else None,
            member_code=row["member_code"] if "member_code" in keys else None,
        )

    @property
    def is_overdue(self) -> bool:
        if self.status == "Returned":
            return False
        today = datetime.date.today()
        due = datetime.date.fromisoformat(self.due_date)
        return today > due

    @property
    def overdue_days(self) -> int:
        if self.status == "Returned" and self.return_date:
            ret = datetime.date.fromisoformat(self.return_date.split()[0])
            due = datetime.date.fromisoformat(self.due_date)
            return max(0, (ret - due).days)
        else:
            today = datetime.date.today()
            due = datetime.date.fromisoformat(self.due_date)
            return max(0, (today - due).days)
