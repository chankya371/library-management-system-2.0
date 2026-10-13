from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    id: Optional[int]
    username: str
    full_name: str
    role: str  # 'admin' or 'librarian'
    created_at: Optional[str] = None

    @classmethod
    def from_row(cls, row) -> "User":
        if row is None:
            return None
        return cls(
            id=row["id"],
            username=row["username"],
            full_name=row["full_name"],
            role=row["role"],
            created_at=row["created_at"] if "created_at" in row.keys() else None,
        )
