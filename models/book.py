from dataclasses import dataclass
from typing import Optional


@dataclass
class Book:
    id: Optional[int]
    isbn: str
    title: str
    author: str
    category: str
    publisher: Optional[str] = ""
    publication_year: Optional[int] = None
    total_copies: int = 1
    available_copies: int = 1
    shelf_number: Optional[str] = ""
    cover_image: Optional[str] = None
    description: Optional[str] = ""
    created_at: Optional[str] = None

    @classmethod
    def from_row(cls, row) -> "Book":
        if row is None:
            return None
        return cls(
            id=row["id"],
            isbn=row["isbn"],
            title=row["title"],
            author=row["author"],
            category=row["category"],
            publisher=row["publisher"] if row["publisher"] else "",
            publication_year=row["publication_year"],
            total_copies=row["total_copies"],
            available_copies=row["available_copies"],
            shelf_number=row["shelf_number"] if row["shelf_number"] else "",
            cover_image=row["cover_image"],
            description=row["description"] if row["description"] else "",
            created_at=row["created_at"] if "created_at" in row.keys() else None,
        )

    @property
    def is_available(self) -> bool:
        return self.available_copies > 0

    @property
    def status_label(self) -> str:
        if self.available_copies == 0:
            return "Out of Stock"
        elif self.available_copies <= 2:
            return "Low Stock"
        return "Available"
