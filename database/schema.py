import sqlite3
import logging
from database.db_connection import get_db_cursor

logger = logging.getLogger(__name__)

CREATE_TABLES_SQL = """
-- Users table for Authentication and Role-based access
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL COLLATE NOCASE,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'librarian')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Books inventory table
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    isbn TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    category TEXT NOT NULL,
    publisher TEXT,
    publication_year INTEGER,
    total_copies INTEGER NOT NULL DEFAULT 1 CHECK(total_copies >= 0),
    available_copies INTEGER NOT NULL DEFAULT 1 CHECK(available_copies >= 0 AND available_copies <= total_copies),
    shelf_number TEXT,
    cover_image TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Members registry table
CREATE TABLE IF NOT EXISTS members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_code TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL COLLATE NOCASE,
    phone TEXT NOT NULL,
    address TEXT,
    membership_type TEXT NOT NULL DEFAULT 'Standard' CHECK(membership_type IN ('Student', 'Faculty', 'Standard', 'Premium')),
    status TEXT NOT NULL DEFAULT 'Active' CHECK(status IN ('Active', 'Inactive', 'Suspended')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Circulation / Issue records table
CREATE TABLE IF NOT EXISTS issue_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE RESTRICT,
    member_id INTEGER NOT NULL REFERENCES members(id) ON DELETE RESTRICT,
    issue_date DATE NOT NULL,
    due_date DATE NOT NULL,
    return_date DATE,
    status TEXT NOT NULL DEFAULT 'Issued' CHECK(status IN ('Issued', 'Returned', 'Overdue')),
    notes TEXT,
    fine_amount REAL DEFAULT 0.0 CHECK(fine_amount >= 0),
    fine_paid INTEGER DEFAULT 0 CHECK(fine_paid IN (0, 1)),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fine payments audit table
CREATE TABLE IF NOT EXISTS fine_payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    issue_id INTEGER NOT NULL REFERENCES issue_records(id) ON DELETE RESTRICT,
    member_id INTEGER NOT NULL REFERENCES members(id) ON DELETE RESTRICT,
    amount_paid REAL NOT NULL CHECK(amount_paid > 0),
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payment_method TEXT DEFAULT 'Cash' CHECK(payment_method IN ('Cash', 'Card', 'UPI/Online', 'Other')),
    receipt_number TEXT UNIQUE NOT NULL,
    notes TEXT
);

-- Global application configuration table
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    description TEXT
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_books_title ON books(title);
CREATE INDEX IF NOT EXISTS idx_books_author ON books(author);
CREATE INDEX IF NOT EXISTS idx_books_isbn ON books(isbn);
CREATE INDEX IF NOT EXISTS idx_books_category ON books(category);

CREATE INDEX IF NOT EXISTS idx_members_code ON members(member_code);
CREATE INDEX IF NOT EXISTS idx_members_email ON members(email);
CREATE INDEX IF NOT EXISTS idx_members_name ON members(full_name);

CREATE INDEX IF NOT EXISTS idx_issues_status ON issue_records(status);
CREATE INDEX IF NOT EXISTS idx_issues_member ON issue_records(member_id);
CREATE INDEX IF NOT EXISTS idx_issues_book ON issue_records(book_id);
CREATE INDEX IF NOT EXISTS idx_issues_due_date ON issue_records(due_date);
"""

DEFAULT_SETTINGS = [
    ("library_name", "Alexandria Modern Library", "Official organization name"),
    ("library_email", "contact@alexandrialib.org", "Library support email"),
    ("library_phone", "+1 (555) 234-5678", "Library front desk phone"),
    ("library_address", "450 Innovation Parkway, Suite 100", "Physical branch address"),
    ("daily_fine_rate", "1.00", "Overdue fine amount charged per calendar day"),
    ("borrowing_period_days", "14", "Standard loan duration in days"),
    ("max_books_per_member", "5", "Maximum active loans permitted simultaneously"),
    ("currency_symbol", "$", "Currency indicator symbol"),
    ("appearance_mode", "Dark", "Visual theme: Dark, Light, or System"),
]


def initialize_database(db_path: str = None) -> None:
    """Creates database tables and default configuration if they do not exist."""
    with get_db_cursor(db_path) as cursor:
        cursor.executescript(CREATE_TABLES_SQL)

        # Insert default settings if missing
        for key, value, desc in DEFAULT_SETTINGS:
            cursor.execute(
                """
                INSERT INTO settings (key, value, description)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO NOTHING;
                """,
                (key, value, desc),
            )
    logger.info("Database initialized successfully.")
