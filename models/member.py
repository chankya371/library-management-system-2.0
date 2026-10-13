from dataclasses import dataclass
from typing import Optional


@dataclass
class Member:
    id: Optional[int]
    member_code: str
    full_name: str
    email: str
    phone: str
    address: Optional[str] = ""
    membership_type: str = "Standard"  # 'Student', 'Faculty', 'Standard', 'Premium'
    status: str = "Active"  # 'Active', 'Inactive', 'Suspended'
    created_at: Optional[str] = None

    @classmethod
    def from_row(cls, row) -> "Member":
        if row is None:
            return None
        return cls(
            id=row["id"],
            member_code=row["member_code"],
            full_name=row["full_name"],
            email=row["email"],
            phone=row["phone"],
            address=row["address"] if row["address"] else "",
            membership_type=row["membership_type"],
            status=row["status"],
            created_at=row["created_at"] if "created_at" in row.keys() else None,
        )

    @property
    def is_active(self) -> bool:
        return self.status == "Active"
