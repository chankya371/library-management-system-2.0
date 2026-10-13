from dataclasses import dataclass
from typing import Optional


@dataclass
class FinePayment:
    id: Optional[int]
    issue_id: int
    member_id: int
    amount_paid: float
    payment_date: str
    payment_method: str  # 'Cash', 'Card', 'UPI/Online', 'Other'
    receipt_number: str
    notes: Optional[str] = ""

    # Joined fields
    member_name: Optional[str] = None
    member_code: Optional[str] = None
    book_title: Optional[str] = None

    @classmethod
    def from_row(cls, row) -> "FinePayment":
        if row is None:
            return None
        keys = row.keys()
        return cls(
            id=row["id"],
            issue_id=row["issue_id"],
            member_id=row["member_id"],
            amount_paid=float(row["amount_paid"]),
            payment_date=row["payment_date"],
            payment_method=row["payment_method"],
            receipt_number=row["receipt_number"],
            notes=row["notes"] if row["notes"] else "",
            member_name=row["member_name"] if "member_name" in keys else None,
            member_code=row["member_code"] if "member_code" in keys else None,
            book_title=row["book_title"] if "book_title" in keys else None,
        )
