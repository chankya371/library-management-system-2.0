import sqlite3
from typing import List, Optional, Tuple, Dict, Any
from database.db_connection import get_db_cursor
from models.book import Book
from utils.validators import validate_isbn, validate_non_empty, validate_publication_year, validate_positive_int


class BookService:
    """Manages book inventory, search, filters, and validation."""

    @staticmethod
    def get_all_books() -> List[Book]:
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("SELECT * FROM books ORDER BY title ASC;")
            return [Book.from_row(r) for r in cursor.fetchall()]

    @staticmethod
    def get_book_by_id(book_id: int) -> Optional[Book]:
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("SELECT * FROM books WHERE id = ?;", (book_id,))
            row = cursor.fetchone()
            return Book.from_row(row) if row else None

    @staticmethod
    def get_book_by_isbn(isbn: str) -> Optional[Book]:
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("SELECT * FROM books WHERE isbn = ?;", (isbn.strip(),))
            row = cursor.fetchone()
            return Book.from_row(row) if row else None

    @staticmethod
    def get_categories() -> List[str]:
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("SELECT DISTINCT category FROM books ORDER BY category ASC;")
            return [r[0] for r in cursor.fetchall() if r[0]]

    @staticmethod
    def add_book(
        isbn: str,
        title: str,
        author: str,
        category: str,
        publisher: str = "",
        publication_year: Optional[int] = None,
        total_copies: int = 1,
        shelf_number: str = "",
        cover_image: Optional[str] = None,
        description: str = "",
    ) -> Tuple[bool, str, Optional[int]]:
        # Validations
        valid_isbn, err = validate_isbn(isbn)
        if not valid_isbn:
            return False, err, None

        valid_title, err = validate_non_empty(title, "Title")
        if not valid_title:
            return False, err, None

        valid_author, err = validate_non_empty(author, "Author")
        if not valid_author:
            return False, err, None

        valid_cat, err = validate_non_empty(category, "Category")
        if not valid_cat:
            return False, err, None

        valid_year, err = validate_publication_year(publication_year)
        if not valid_year:
            return False, err, None

        valid_copies, err = validate_positive_int(total_copies, "Total copies")
        if not valid_copies:
            return False, err, None

        clean_isbn = isbn.strip()
        clean_title = title.strip()
        clean_author = author.strip()
        clean_cat = category.strip()
        year_val = int(publication_year) if publication_year else None
        copies_val = int(total_copies)

        try:
            with get_db_cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO books (isbn, title, author, category, publisher, publication_year, 
                                       total_copies, available_copies, shelf_number, cover_image, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        clean_isbn,
                        clean_title,
                        clean_author,
                        clean_cat,
                        publisher.strip() if publisher else "",
                        year_val,
                        copies_val,
                        copies_val,  # initially all copies available
                        shelf_number.strip() if shelf_number else "",
                        cover_image,
                        description.strip() if description else "",
                    ),
                )
                new_id = cursor.lastrowid
            return True, "Book added successfully.", new_id
        except sqlite3.IntegrityError:
            return False, f"A book with ISBN '{clean_isbn}' already exists.", None
        except Exception as e:
            return False, f"Database error: {str(e)}", None

    @staticmethod
    def update_book(
        book_id: int,
        isbn: str,
        title: str,
        author: str,
        category: str,
        publisher: str = "",
        publication_year: Optional[int] = None,
        total_copies: int = 1,
        shelf_number: str = "",
        cover_image: Optional[str] = None,
        description: str = "",
    ) -> Tuple[bool, str]:
        current_book = BookService.get_book_by_id(book_id)
        if not current_book:
            return False, "Book not found."

        valid_isbn, err = validate_isbn(isbn)
        if not valid_isbn:
            return False, err

        valid_title, err = validate_non_empty(title, "Title")
        if not valid_title:
            return False, err

        valid_author, err = validate_non_empty(author, "Author")
        if not valid_author:
            return False, err

        valid_cat, err = validate_non_empty(category, "Category")
        if not valid_cat:
            return False, err

        valid_year, err = validate_publication_year(publication_year)
        if not valid_year:
            return False, err

        valid_copies, err = validate_positive_int(total_copies, "Total copies")
        if not valid_copies:
            return False, err

        new_total = int(total_copies)
        currently_issued = current_book.total_copies - current_book.available_copies
        if new_total < currently_issued:
            return (
                False,
                f"Cannot set total copies to {new_total}. Currently {currently_issued} copies are issued on loan.",
            )

        new_available = new_total - currently_issued
        clean_isbn = isbn.strip()
        clean_title = title.strip()
        clean_author = author.strip()
        clean_cat = category.strip()
        year_val = int(publication_year) if publication_year else None

        # Keep existing cover image if not provided
        img_to_save = cover_image if cover_image is not None else current_book.cover_image

        try:
            with get_db_cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE books
                    SET isbn = ?, title = ?, author = ?, category = ?, publisher = ?, 
                        publication_year = ?, total_copies = ?, available_copies = ?, 
                        shelf_number = ?, cover_image = ?, description = ?
                    WHERE id = ?;
                    """,
                    (
                        clean_isbn,
                        clean_title,
                        clean_author,
                        clean_cat,
                        publisher.strip() if publisher else "",
                        year_val,
                        new_total,
                        new_available,
                        shelf_number.strip() if shelf_number else "",
                        img_to_save,
                        description.strip() if description else "",
                        book_id,
                    ),
                )
            return True, "Book updated successfully."
        except sqlite3.IntegrityError:
            return False, f"Another book with ISBN '{clean_isbn}' already exists."
        except Exception as e:
            return False, f"Database error: {str(e)}"

    @staticmethod
    def delete_book(book_id: int) -> Tuple[bool, str]:
        # Critical rule: Prevent deleting books that have active issue records
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*) FROM issue_records 
                WHERE book_id = ? AND status IN ('Issued', 'Overdue');
                """,
                (book_id,),
            )
            active_loans = cursor.fetchone()[0]
            if active_loans > 0:
                return (
                    False,
                    f"Cannot delete book: There are {active_loans} active loans currently issued for this book.",
                )

            # Check if there are historical issue records
            cursor.execute(
                "SELECT COUNT(*) FROM issue_records WHERE book_id = ?;",
                (book_id,),
            )
            total_history = cursor.fetchone()[0]
            if total_history > 0:
                return (
                    False,
                    "Cannot delete book: Historical borrowing records exist. Consider setting copies to 0 instead to preserve records.",
                )

            cursor.execute("DELETE FROM books WHERE id = ?;", (book_id,))
            return True, "Book deleted successfully."

    @staticmethod
    def search_books(
        query: str = "",
        category: str = "All",
        availability: str = "All",
        sort_by: str = "title",
        sort_order: str = "ASC",
    ) -> List[Book]:
        sql = "SELECT * FROM books WHERE 1=1"
        params = []

        if query and query.strip():
            term = f"%{query.strip()}%"
            sql += " AND (title LIKE ? OR author LIKE ? OR isbn LIKE ? OR category LIKE ? OR publisher LIKE ?)"
            params.extend([term, term, term, term, term])

        if category and category != "All":
            sql += " AND category = ?"
            params.append(category)

        if availability == "Available":
            sql += " AND available_copies > 0"
        elif availability == "Out of Stock":
            sql += " AND available_copies = 0"
        elif availability == "Low Stock":
            sql += " AND available_copies > 0 AND available_copies <= 2"

        allowed_sort = {
            "title": "title",
            "author": "author",
            "publication_year": "publication_year",
            "available_copies": "available_copies",
            "created_at": "created_at",
        }
        order_col = allowed_sort.get(sort_by.lower(), "title")
        direction = "DESC" if sort_order.upper() == "DESC" else "ASC"
        sql += f" ORDER BY {order_col} {direction}"

        with get_db_cursor(commit=False) as cursor:
            cursor.execute(sql, params)
            return [Book.from_row(r) for r in cursor.fetchall()]
