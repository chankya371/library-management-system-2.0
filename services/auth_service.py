import sqlite3
from typing import Optional, List, Tuple
from database.db_connection import get_db_cursor
from models.user import User
from utils.security import hash_password, verify_password


class AuthService:
    """Handles user authentication, password management, and user administration."""

    @staticmethod
    def authenticate(username: str, password: str) -> Optional[User]:
        if not username or not password:
            return None
        with get_db_cursor(commit=False) as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE username = ? COLLATE NOCASE;",
                (username.strip(),),
            )
            row = cursor.fetchone()
            if not row:
                return None

            if verify_password(password, row["salt"], row["password_hash"]):
                return User.from_row(row)
            return None

    @staticmethod
    def create_user(username: str, password: str, full_name: str, role: str) -> Tuple[bool, str]:
        username = username.strip()
        full_name = full_name.strip()
        if len(username) < 3:
            return False, "Username must be at least 3 characters."
        if len(password) < 6:
            return False, "Password must be at least 6 characters."
        if role not in ("admin", "librarian"):
            return False, "Role must be either 'admin' or 'librarian'."

        pw_hash, salt = hash_password(password)
        try:
            with get_db_cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO users (username, password_hash, salt, full_name, role)
                    VALUES (?, ?, ?, ?, ?);
                    """,
                    (username, pw_hash, salt, full_name, role),
                )
            return True, "User created successfully."
        except sqlite3.IntegrityError:
            return False, f"Username '{username}' already exists."
        except Exception as e:
            return False, f"Error creating user: {str(e)}"

    @staticmethod
    def change_password(user_id: int, old_password: str, new_password: str) -> Tuple[bool, str]:
        if len(new_password) < 6:
            return False, "New password must be at least 6 characters long."

        with get_db_cursor() as cursor:
            cursor.execute("SELECT password_hash, salt FROM users WHERE id = ?;", (user_id,))
            row = cursor.fetchone()
            if not row:
                return False, "User not found."

            if not verify_password(old_password, row["salt"], row["password_hash"]):
                return False, "Current password is incorrect."

            new_hash, new_salt = hash_password(new_password)
            cursor.execute(
                "UPDATE users SET password_hash = ?, salt = ? WHERE id = ?;",
                (new_hash, new_salt, user_id),
            )
        return True, "Password updated successfully."

    @staticmethod
    def list_users() -> List[User]:
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("SELECT id, username, full_name, role, created_at FROM users ORDER BY id;")
            return [User.from_row(r) for r in cursor.fetchall()]

    @staticmethod
    def delete_user(user_id: int, current_user_id: int) -> Tuple[bool, str]:
        if user_id == current_user_id:
            return False, "You cannot delete your own account."

        with get_db_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM users;")
            count = cursor.fetchone()[0]
            if count <= 1:
                return False, "Cannot delete the last remaining user."

            cursor.execute("DELETE FROM users WHERE id = ?;", (user_id,))
            return True, "User deleted successfully."
