# Alexandria - Modern Library Management System 2.0

A commercial-grade, desktop **Library Management System** built in Python with a SaaS-inspired administrative interface powered by **CustomTkinter**, persistent **SQLite**, and **Matplotlib** analytics.

---

## 🏛️ System Overview

Alexandria is an end-to-end library circulation and inventory platform designed with modern UI/UX aesthetics (dark navy theme, teal accents, rounded cards, live statistics, and vector iconography). It delivers real-world database constraints, transactional book stock decrement/increment, automatic overdue calculation, fine collection, receipt generation, and report exports.

---

## ✨ Features

- **Executive Dashboard:** Real-time metrics for inventory, active loans, registered patrons, overdue items, fine revenues, 7-day circulation trend chart, category breakdown chart, and quick-action triggers.
- **Book Catalog Management:** Add, edit, catalog, filter (category & stock availability), sort, multi-copy inventory tracking, and deletion protection against books with active loans.
- **Member Registry:** Patron registration, tier types (`Student`, `Faculty`, `Standard`, `Premium`), status toggles (`Active`, `Inactive`, `Suspended`), borrowing history audits, profile inspection modal, and delete safety against unreturned books.
- **Circulation Desk:** Atomic book checkouts, copy reservation, configurable borrowing periods, maximum loan constraints, automated overdue penalties, and one-click return processing.
- **Fine Management:** Real-time overdue computation based on daily fine rates, payment processing (`Cash`, `Card`, `UPI/Online`), and official printable payment receipts.
- **Reports & Analytics:** Inventory summaries, top borrowed books, most active patrons, overdue audit logs, and one-click exports to **CSV** and **Excel (.xlsx)**.
- **Security & RBAC:** PBKDF2-HMAC-SHA256 salted password hashing, password visibility toggles, session state management, and role-based permissions (`Admin` and `Librarian`).
- **Settings & Maintenance:** Dynamic fine policy adjustments, branch info, hotkeys, and automated SQLite backup/restore with integrity checks.

---

## 🛠️ Technology Stack

- **Language:** Python 3.10+ (tested on Python 3.14)
- **GUI Framework:** [CustomTkinter](https://customtkinter.tomschimansky.com/) (modern responsive UI)
- **Database:** SQLite3 with Foreign Keys (`PRAGMA foreign_keys = ON`) and transactional context managers
- **Charts:** Matplotlib (`FigureCanvasTkAgg` integration)
- **Image & Iconography:** Pillow (PIL) high-resolution anti-aliased vector icon rendering
- **Spreadsheet Engine:** `openpyxl` & standard `csv`

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure Python 3.10 or higher is installed and available in your environment:
```bash
python --version
```

### 2. Virtual Environment Setup (Recommended)
```bash
# Create a virtual environment
python -m venv venv

# Activate on Windows:
venv\Scripts\activate

# Activate on macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python main.py
```

*Upon first launch, the application automatically initializes the SQLite database schema and seeds realistic demonstration data.*

---

## 🔑 Demo Login Credentials

The system comes pre-configured with two user accounts:

| Role | Username | Password | Permissions |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `admin123` | Full access (System settings, user management, backup/restore, inventory, circulation) |
| **Librarian** | `librarian` | `lib123` | Operational access (Books, members, issues, returns, fines, reports) |

---

## ⌨️ Global Keyboard Shortcuts

| Shortcut | Action |
| :--- | :--- |
| `Ctrl + 1` | Switch to Dashboard |
| `Ctrl + 2` | Switch to Books Catalog |
| `Ctrl + 3` | Switch to Members Registry |
| `Ctrl + 4` | Switch to Circulation Desk |
| `Ctrl + 5` | Switch to Fines & Payments |
| `Ctrl + 6` | Switch to Reports & Analytics |
| `Ctrl + 7` | Switch to Settings |
| `Ctrl + B` | Open "Add Book" Dialog |
| `Ctrl + M` | Open "Register Member" Dialog |
| `Ctrl + I` | Open "Issue Book" Checkout Dialog |
| `Ctrl + R` | Open "Return Book" Dialog |

---

## 🗄️ Database Architecture & Storage

- **Database File:** `library_system.db` in the project root directory.
- **Relational Tables:**
  - `users`: Staff credentials, salts, and roles.
  - `books`: ISBN, title, author, category, total copies, available copies, shelf.
  - `members`: Member code, contact info, membership type, status.
  - `issue_records`: Loan tracking, issue date, due date, return date, fines.
  - `fine_payments`: Settled fine transactions, payment methods, receipt numbers.
  - `settings`: Key-value application configurations.

### Database Backup & Restore
- **Backup:** Navigate to **Settings** > **Database Maintenance** > click **Create Backup Snapshot**. Backups are saved in the `backups/` directory as `library_backup_YYYYMMDD_HHMMSS.sqlite`.
- **Restore:** Click **Restore from Backup File...**, select a valid `.sqlite` or `.db` snapshot, and confirm. The system performs an integrity check (`PRAGMA integrity_check`) before restoring.

---

## 🧪 Running Automated Tests

Run the full automated test suite covering authentication, stock transitions, validations, fine calculations, and exports:

```bash
python -m unittest tests/test_library_system.py
```

Expected output:
```text
Ran 13 tests in 0.98s
OK
```

---

## 🔧 Troubleshooting Common Issues

1. **`ModuleNotFoundError: No module named 'customtkinter'`**
   - Run `pip install -r requirements.txt`.
2. **Missing `tkinter` on Linux:**
   - On Ubuntu/Debian: `sudo apt-get install python3-tk`
   - On Fedora: `sudo dnf install python3-tkinter`
3. **High-DPI / Blurry Fonts on Windows:**
   - CustomTkinter natively handles scaling. Ensure Windows display scaling is set between 100% and 150%.
