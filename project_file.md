# Alexandria - Modern Library Management System 2.0
## Complete Technical Documentation & Visual Reference Guide

---

## 📋 Executive Overview

**Alexandria 2.0** is an enterprise-grade desktop Library Circulation and Resource Planning platform built with **Python 3**, featuring a modern administrative interface styled with **CustomTkinter**, persistent **SQLite** with strict relational integrity, and embedded **Matplotlib** visual analytics.

The application delivers an end-to-end management experience for librarians and administrative staff, featuring transactional inventory increment/decrement, automated overdue penalty audits, cash/UPI fine payments, member management across multiple tiers, receipt issuance, and multi-format data exports (CSV and Microsoft Excel `.xlsx`).

---

## 📸 Interface Showcase & Visual Tour

Below are original system screenshots captured directly from the live Alexandria 2.0 operational runtime.

---

### 1. Staff Authentication & Login Portal

A secure, centralized access gateway featuring credential verification with PBKDF2 salted hash comparison, password visibility toggling, error alerts, and demo profile access hints.

![Alexandria Staff Login Portal](assets/screenshots/01_login_portal.png)

- **Authentication Protocol:** PBKDF2-HMAC-SHA256 with cryptographically generated 16-byte random salts per account.
- **Roles:** Administrator (Full system privileges) and Librarian (Operational daily circulation privileges).
- **Default Test Accounts:**
  - `admin` / `admin123`
  - `librarian` / `lib123`

---

### 2. Executive System Dashboard

The executive nerve center of the library, displaying real-time aggregated metrics, live inventory gauges, circulation trends, and quick-action shortcuts.

![Executive System Dashboard](assets/screenshots/02_executive_dashboard.png)

- **Metric Cards (Live KPIs):**
  - **Total Books:** Total collection volume across all cataloged titles and individual copies.
  - **Available Books:** Instant real-time checkout readiness.
  - **Issued Books:** Copies currently in borrower circulation.
  - **Registered Patrons:** Total active and registered member profiles.
  - **Overdue Penalties:** Active overdue book count triggering fine computation.
  - **Total Fines:** Historical collected fines vs. pending accruals.
- **Interactive Matplotlib Visualizations:**
  - **7-Day Circulation Flow:** Daily issue vs. return trends dynamically plotted.
  - **Collection Category Breakdown:** Donut chart highlighting collection distribution across Fiction, Science, Computer Science, Business, and Self-Help.
- **Quick Action Bar:** Direct triggers for adding books, onboarding patrons, checking out copies, and processing returns.

---

### 3. Book Inventory & Catalog

A comprehensive search, filter, cataloging, and inventory management screen with instant updates and multi-column sorting.

![Book Inventory & Catalog](assets/screenshots/03_book_catalog.png)

- **Real-Time Search:** Search by ISBN, Title, Author, or Category with debounced instant table filtering.
- **Filtering & Facets:**
  - Category selector (e.g. *Computer Science*, *Fiction*, *Science*, *Business*, *History*).
  - Availability status filter (*All*, *Available*, *Low Stock*, *Out of Stock*).
  - Sorting criteria (*Title*, *Author*, *Copies Available*, *Category*).
- **Safety Constraints:** Built-in deletion protections prevent removal of book records with active circulating loans.

---

### 4. Book Cataloging Dialog

A streamlined modal dialog for entering or updating book metadata, ISBN codes, authors, genres, and stock quantities.

![Add New Book Dialog](assets/screenshots/04_add_book_dialog.png)

- **Form Fields:** ISBN code, book title, author, category classification dropdown, and initial copy quantity.
- **Transactional Consistency:** New entries immediately synchronize across all database indices and active dashboard metrics.

---

### 5. Member Registry & Patron Management

A complete directory of all registered library patrons, displaying membership classifications, contact channels, and real-time status indicators.

![Member Registry & Patron Directory](assets/screenshots/05_member_registry.png)

- **Patron Tiers:** Supported categories include `Student`, `Faculty`, `Standard`, and `Premium`.
- **Status Management:** Quick toggling between `Active`, `Inactive`, and `Suspended` states.
- **Patron Profiles:** Detailed profile inspector displaying borrowing history, active loans, and fine settlements.

---

### 6. Patron Registration Dialog

A fast onboarding dialog for enrolling students, faculty members, and public borrowers.

![Register Member Dialog](assets/screenshots/06_register_member_dialog.png)

- **Fields:** Full legal name, university/personal email address, contact phone number, initial tier, and operational status.
- **Automatic ID Generation:** Generates unique sequential patron codes (`MEM-XXXX`).

---

### 7. Circulation Desk (Issues & Active Loans)

The primary operational desk for issuing books, tracking return deadlines, and auditing overdue loans.

![Circulation Desk Active Loans](assets/screenshots/07_circulation_desk.png)

- **Live Loan Tracking:** Displays Loan ID, Book Title, Borrower Name, Issue Date, Due Date, and Status.
- **Overdue Badges:** Dynamic red warning pills highlight loans that have passed their contractual return deadline.
- **One-Click Returns:** Direct `Return` action button to inspect loan duration, compute overdue fines, and update shelf stock.

---

### 8. Book Checkout & Loan Issuance Dialog

A checkout transaction dialog linking available book inventory to verified registered members.

![Issue Book Checkout Dialog](assets/screenshots/08_issue_book_dialog.png)

- **Dynamic Selectors:**
  - Member selector with live search and tier display.
  - Book title selector displaying real-time available stock count.
  - Loan duration dropdown (7, 14, 21, or 30 days).
- **Concurrency Guards:** Atomic copy availability decrement protects against double-booking and out-of-stock loans.

---

### 9. Fine Management & Financial Audit

A dedicated revenue and penalty auditing dashboard tracking pending overdue debts and settled payments.

![Fine Management & Financial Audit](assets/screenshots/09_fine_management.png)

- **Audit Statistics:**
  - **Total Fines Collected:** Settled revenue recorded in system ledger.
  - **Pending Overdue Fines:** Accumulated uncollected penalty balance.
  - **Daily Fine Rate:** Active policy rate (configurable in Settings).
- **Settlement Workflow:** Mark individual overdue penalties as paid via Cash, Card, or UPI with automatic receipt generation.

---

### 10. Reports & Analytics Center

Business intelligence and circulation analytics hub with visual breakdown and one-click data export facilities.

![Reports and Visual Analytics Center](assets/screenshots/10_reports_analytics.png)

- **Report Datasets:**
  - *Total Inventory Catalog Report*
  - *Most Borrowed Books Ranking*
  - *Most Active Members Ranking*
  - *Overdue Loans Audit Report*
  - *Fines Collection Ledger*
- **Export Formats:**
  - **Microsoft Excel (`.xlsx`):** Formatted spreadsheets with header styling generated via `openpyxl`.
  - **Comma-Separated Values (`.csv`):** Universal data format for external data pipelines.

---

### 11. System Settings & Database Maintenance

Administrative configuration panel for library policies, visual themes, and disaster recovery backup snapshots.

![System Settings & Maintenance](assets/screenshots/11_system_settings.png)

- **Organization & Branch Info:** Library name, administrative email, support phone, and address.
- **Circulation Policies:**
  - Configurable daily overdue fine rate (e.g. `$1.00 / day`).
  - Default loan period in days (e.g. `14 days`).
  - Maximum allowed borrowing limit per patron.
- **Disaster Recovery & Backups:**
  - **Create Backup Snapshot:** Creates a timestamped `.sqlite` snapshot in `backups/`.
  - **Restore from Backup File:** Validates file integrity (`PRAGMA integrity_check`) before safely restoring.

---

## 🏗️ Architecture & Technology Stack

```mermaid
graph TD
    A[User Interface Layer] -->|CustomTkinter + PIL| B[UI Pages & Modals]
    B -->|Navigation & State| C[Main Controller / MainWindow]
    C -->|Service Calls| D[Service Layer]
    
    subgraph Services
        D1[AuthService]
        D2[BookService]
        D3[MemberService]
        D4[CirculationService]
        D5[FineService]
        D6[ReportService]
        D7[SettingsService]
    end
    
    D --> D1
    D --> D2
    D --> D3
    D --> D4
    D --> D5
    D --> D6
    D --> D7
    
    D1 & D2 & D3 & D4 & D5 & D6 & D7 -->|DB Connection Pool| E[(SQLite Database: library_system.db)]
    D6 -->|Chart Rendering| F[Matplotlib Canvas]
    D6 -->|Export Pipelines| G[Excel openpyxl / CSV Engine]
```

### Core Technologies
| Component | Technology | Version / Specification |
| :--- | :--- | :--- |
| **Language** | Python | 3.10+ (Tested on 3.14) |
| **GUI Framework** | CustomTkinter | 5.2+ (Dark navy theme with teal accents) |
| **Database** | SQLite3 | Native with `PRAGMA foreign_keys = ON` |
| **Analytics Engine** | Matplotlib | 3.8+ (`FigureCanvasTkAgg` integration) |
| **Iconography** | Pillow (PIL) | Vector icon rendering & dynamic scaling |
| **Spreadsheets** | openpyxl | OpenXML Excel workbook generator |
| **Security** | hashlib / secrets | PBKDF2-HMAC-SHA256 salted hashes |

---

## 🗄️ Database Relational Design

The system is underpinned by 6 normalized tables with foreign key cascades and transactional consistency:

```mermaid
erDiagram
    USERS {
        int id PK
        string username
        string password_hash
        string salt
        string full_name
        string role
        timestamp created_at
    }
    BOOKS {
        int id PK
        string isbn UK
        string title
        string author
        string category
        int total_copies
        int available_copies
        string shelf_location
        timestamp created_at
    }
    MEMBERS {
        int id PK
        string member_code UK
        string name
        string email
        string phone
        string membership_type
        string status
        timestamp created_at
    }
    ISSUE_RECORDS {
        int id PK
        int book_id FK
        int member_id FK
        date issue_date
        date due_date
        date return_date
        string status
        float fine_amount
        string fine_status
    }
    FINE_PAYMENTS {
        int id PK
        int issue_id FK
        float amount_paid
        string payment_method
        string receipt_number UK
        timestamp payment_date
    }
    SETTINGS {
        string key PK
        string value
    }

    BOOKS ||--o{ ISSUE_RECORDS : "borrowed in"
    MEMBERS ||--o{ ISSUE_RECORDS : "issues"
    ISSUE_RECORDS ||--o{ FINE_PAYMENTS : "generates"
```

---

## ⚡ Circulation Business Logic

### Checkout Flowchart
```mermaid
flowchart TD
    Start([Patron requests book checkout]) --> CheckMember{Is Patron Status 'Active'?}
    CheckMember -- No --> RejectMember[Error: Patron account is Inactive or Suspended]
    CheckMember -- Yes --> CheckLimit{Active loans < Max Limit?}
    CheckLimit -- No --> RejectLimit[Error: Max book allowance reached for member]
    CheckLimit -- Yes --> CheckStock{Available Copies > 0?}
    CheckStock -- No --> RejectStock[Error: Book is currently out of stock]
    CheckStock -- Yes --> CreateLoan[Create Issue Record in Database]
    CreateLoan --> DecrementStock[Atomic Decrement available_copies by 1]
    DecrementStock --> Success([Print / Display Checkout Confirmation])
```

---

## ⌨️ Global Keyboard Shortcuts

| Shortcut Key | Action Performed |
| :--- | :--- |
| `Ctrl + 1` | Switch to **System Dashboard** |
| `Ctrl + 2` | Switch to **Book Inventory & Catalog** |
| `Ctrl + 3` | Switch to **Member Registry & Patrons** |
| `Ctrl + 4` | Switch to **Circulation Desk** |
| `Ctrl + 5` | Switch to **Fine Payments & Financial Audit** |
| `Ctrl + 6` | Switch to **Reports & Analytics Center** |
| `Ctrl + 7` | Switch to **System Settings & Maintenance** |
| `Ctrl + B` | Open **Add New Book** Dialog |
| `Ctrl + M` | Open **Register Member** Dialog |
| `Ctrl + I` | Open **Issue Book Checkout** Dialog |
| `Ctrl + R` | Open **Return Book** Dialog |

---

## 🚀 Installation & Rapid Deployment

### 1. Prerequisites
- Python 3.10, 3.11, 3.12, 3.13, or 3.14.

### 2. Dependency Installation
```bash
pip install -r requirements.txt
```

### 3. Launching Application
```bash
python main.py
```

*Note: On first startup, Alexandria automatically initializes the database schema and seeds sample books, members, circulation records, and administrative accounts.*

---

## 🧪 Verification & Automated Testing

The project includes an automated test suite verifying database foreign keys, stock atomic decrement/increment, overdue calculation routines, authentication validation, and report exports:

```bash
python -m unittest tests/test_library_system.py
```

Expected result:
```text
Ran 13 tests in 0.98s
OK
```

---
*Alexandria Library Management System 2.0 • Generated Technical Documentation with Original UI Captures.*
