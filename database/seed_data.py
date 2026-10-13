import datetime
from database.db_connection import get_db_cursor
from utils.security import hash_password


def seed_database(db_path: str = None) -> None:
    """Seeds the database with rich, realistic demonstration data."""
    with get_db_cursor(db_path) as cursor:
        # Check if users already exist
        cursor.execute("SELECT COUNT(*) FROM users;")
        if cursor.fetchone()[0] > 0:
            return  # Already seeded

        # 1. Seed Users
        admin_hash, admin_salt = hash_password("admin123")
        lib_hash, lib_salt = hash_password("lib123")

        cursor.executemany(
            """
            INSERT INTO users (username, password_hash, salt, full_name, role)
            VALUES (?, ?, ?, ?, ?);
            """,
            [
                ("admin", admin_hash, admin_salt, "Dr. Eleanor Vance", "admin"),
                ("librarian", lib_hash, lib_salt, "Marcus Holloway", "librarian"),
            ],
        )

        # 2. Seed Books
        books = [
            ("978-0132350884", "Clean Code: A Handbook of Agile Software Craftsmanship", "Robert C. Martin", "Computer Science", "Prentice Hall", 2008, 6, 5, "CS-A1-04", None, "A handbook of agile craftsmanship."),
            ("978-0262033848", "Introduction to Algorithms, 3rd Edition", "Thomas H. Cormen, Charles E. Leiserson", "Computer Science", "MIT Press", 2009, 4, 3, "CS-A2-01", None, "The premier algorithms textbook."),
            ("978-0135957059", "The Pragmatic Programmer: 20th Anniversary Edition", "David Thomas, Andrew Hunt", "Computer Science", "Addison-Wesley", 2019, 5, 3, "CS-A1-09", None, "Essential guides for modern programmers."),
            ("978-1449373320", "Designing Data-Intensive Applications", "Martin Kleppmann", "Computer Science", "O'Reilly Media", 2017, 5, 4, "CS-B1-02", None, "The big ideas behind reliable, scalable systems."),
            ("978-0061120084", "To Kill a Mockingbird", "Harper Lee", "Fiction", "Harper Perennial", 1960, 6, 5, "FIC-L-12", None, "Classic Pulitzer Prize-winning novel."),
            ("978-0451524935", "1984", "George Orwell", "Fiction", "Signet Classic", 1949, 7, 5, "FIC-O-08", None, "The dystopian masterpiece on totalitarian control."),
            ("978-0743273565", "The Great Gatsby", "F. Scott Fitzgerald", "Fiction", "Scribner", 1925, 4, 4, "FIC-F-05", None, "The quintessential Jazz Age American classic."),
            ("978-0062316097", "Sapiens: A Brief History of Humankind", "Yuval Noah Harari", "History", "Harper", 2015, 6, 4, "HIST-H-01", None, "A narrative history of humanity's evolution."),
            ("978-0553380163", "A Brief History of Time", "Stephen Hawking", "Science", "Bantam", 1988, 4, 3, "SCI-H-03", None, "From the Big Bang to Black Holes."),
            ("978-0393609394", "Astrophysics for People in a Hurry", "Neil deGrasse Tyson", "Science", "W. W. Norton", 2017, 5, 5, "SCI-T-02", None, "Cosmic queries made accessible and witty."),
            ("978-0735211292", "Atomic Habits", "James Clear", "Self-Help", "Avery", 2018, 8, 6, "SELF-C-01", None, "Tiny changes, remarkable results."),
            ("978-0066620992", "Good to Great", "Jim Collins", "Business", "HarperBusiness", 2001, 5, 4, "BUS-C-04", None, "Why some companies make the leap and others don't."),
        ]

        cursor.executemany(
            """
            INSERT INTO books (isbn, title, author, category, publisher, publication_year, total_copies, available_copies, shelf_number, cover_image, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            books,
        )

        # 3. Seed Members
        members = [
            ("MEM-1001", "Sophia Chen", "sophia.chen@example.edu", "+1 (555) 901-2341", "12 University Ave, Apt 4B", "Student", "Active"),
            ("MEM-1002", "Liam Alexander", "liam.alex@example.com", "+1 (555) 872-9182", "742 Evergreen Terrace", "Standard", "Active"),
            ("MEM-1003", "Prof. Arthur Pendelton", "a.pendelton@university.edu", "+1 (555) 345-6789", "Faculty Tower 302", "Faculty", "Active"),
            ("MEM-1004", "Maya Rodriguez", "maya.r@startup.io", "+1 (555) 456-7890", "88 Silicon Blvd", "Premium", "Active"),
            ("MEM-1005", "Ethan Wright", "ethan.w@gmail.com", "+1 (555) 567-8901", "512 Pinecrest Way", "Standard", "Active"),
            ("MEM-1006", "Olivia Kim", "olivia.k@campus.edu", "+1 (555) 678-9012", "Dorm Quad 14", "Student", "Active"),
            ("MEM-1007", "Lucas Scott", "lucas.scott@outlook.com", "+1 (555) 789-0123", "903 Oak Valley Dr", "Standard", "Inactive"),
            ("MEM-1008", "Emma Watson", "emma.w@books.org", "+1 (555) 890-1234", "17 Baker Street", "Premium", "Active"),
        ]

        cursor.executemany(
            """
            INSERT INTO members (member_code, full_name, email, phone, address, membership_type, status)
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
            members,
        )

        # Fetch IDs for references
        cursor.execute("SELECT id, isbn FROM books ORDER BY id;")
        book_rows = cursor.fetchall()
        book_id_map = {row["isbn"]: row["id"] for row in book_rows}

        cursor.execute("SELECT id, member_code FROM members ORDER BY id;")
        member_rows = cursor.fetchall()
        mem_id_map = {row["member_code"]: row["id"] for row in member_rows}

        today = datetime.date.today()

        # 4. Seed Issue Records
        # Issue 1: Currently active issued (Clean Code to Sophia Chen)
        issue1_date = today - datetime.timedelta(days=4)
        due1_date = today + datetime.timedelta(days=10)

        # Issue 2: Currently active issued (Algorithms to Liam Alexander)
        issue2_date = today - datetime.timedelta(days=7)
        due2_date = today + datetime.timedelta(days=7)

        # Issue 3: Overdue issue (Pragmatic Programmer to Prof. Pendelton) - 5 days overdue
        issue3_date = today - datetime.timedelta(days=19)
        due3_date = today - datetime.timedelta(days=5)

        # Issue 4: Overdue issue (Atomic Habits to Maya Rodriguez) - 3 days overdue
        issue4_date = today - datetime.timedelta(days=17)
        due4_date = today - datetime.timedelta(days=3)

        # Issue 5: Currently active issued (Sapiens to Ethan Wright)
        issue5_date = today - datetime.timedelta(days=2)
        due5_date = today + datetime.timedelta(days=12)

        # Issue 6: Returned on time (1984 by Olivia Kim)
        issue6_date = today - datetime.timedelta(days=25)
        due6_date = today - datetime.timedelta(days=11)
        ret6_date = today - datetime.timedelta(days=12)

        # Issue 7: Returned late with fine paid (To Kill a Mockingbird by Emma Watson)
        issue7_date = today - datetime.timedelta(days=30)
        due7_date = today - datetime.timedelta(days=16)
        ret7_date = today - datetime.timedelta(days=12) # 4 days overdue, $4 fine paid

        # Issue 8: Active (Hawking to Sophia Chen)
        issue8_date = today - datetime.timedelta(days=5)
        due8_date = today + datetime.timedelta(days=9)

        issues = [
            (book_id_map["978-0132350884"], mem_id_map["MEM-1001"], issue1_date.isoformat(), due1_date.isoformat(), None, "Issued", "Standard loan", 0.0, 0),
            (book_id_map["978-0262033848"], mem_id_map["MEM-1002"], issue2_date.isoformat(), due2_date.isoformat(), None, "Issued", "Standard loan", 0.0, 0),
            (book_id_map["978-0135957059"], mem_id_map["MEM-1003"], issue3_date.isoformat(), due3_date.isoformat(), None, "Overdue", "First notice sent", 5.0, 0),
            (book_id_map["978-0735211292"], mem_id_map["MEM-1004"], issue4_date.isoformat(), due4_date.isoformat(), None, "Overdue", "Overdue notification emailed", 3.0, 0),
            (book_id_map["978-0062316097"], mem_id_map["MEM-1005"], issue5_date.isoformat(), due5_date.isoformat(), None, "Issued", "Standard loan", 0.0, 0),
            (book_id_map["978-0451524935"], mem_id_map["MEM-1006"], issue6_date.isoformat(), due6_date.isoformat(), ret6_date.isoformat(), "Returned", "Returned in pristine condition", 0.0, 0),
            (book_id_map["978-0061120084"], mem_id_map["MEM-1008"], issue7_date.isoformat(), due7_date.isoformat(), ret7_date.isoformat(), "Returned", "Returned with 4 days delay", 4.0, 1),
            (book_id_map["978-0553380163"], mem_id_map["MEM-1001"], issue8_date.isoformat(), due8_date.isoformat(), None, "Issued", "Course reference", 0.0, 0),
        ]

        cursor.executemany(
            """
            INSERT INTO issue_records (book_id, member_id, issue_date, due_date, return_date, status, notes, fine_amount, fine_paid)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            issues,
        )

        # 5. Seed Fine Payment for issue 7
        cursor.execute("SELECT id FROM issue_records WHERE fine_paid = 1 LIMIT 1;")
        paid_issue = cursor.fetchone()
        if paid_issue:
            paid_issue_id = paid_issue["id"]
            cursor.execute(
                """
                INSERT INTO fine_payments (issue_id, member_id, amount_paid, payment_date, payment_method, receipt_number, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (paid_issue_id, mem_id_map["MEM-1008"], 4.00, (today - datetime.timedelta(days=12)).isoformat() + " 14:30:00", "Card", "REC-20261001-001", "Overdue 4 days fine settled via Visa Card"),
            )
