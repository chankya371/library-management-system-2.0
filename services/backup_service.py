import os
import shutil
import datetime
import sqlite3
from typing import List, Dict, Any, Tuple
from database.db_connection import get_db_path, set_db_path


class BackupService:
    """Handles automated SQLite backup creation and database restore operations."""

    @staticmethod
    def get_backup_dir() -> str:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        backup_dir = os.path.join(base_dir, "backups")
        os.makedirs(backup_dir, exist_ok=True)
        return backup_dir

    @staticmethod
    def create_backup(notes: str = "") -> Tuple[bool, str, str]:
        """Creates an online backup using SQLite's backup API to guarantee zero corruption."""
        try:
            backup_dir = BackupService.get_backup_dir()
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"library_backup_{timestamp}.sqlite"
            dest_path = os.path.join(backup_dir, filename)

            src_path = get_db_path()
            src_conn = sqlite3.connect(src_path)
            dest_conn = sqlite3.connect(dest_path)

            with dest_conn:
                src_conn.backup(dest_conn, pages=100)

            src_conn.close()
            dest_conn.close()

            file_size_kb = round(os.path.getsize(dest_path) / 1024, 2)
            return True, f"Backup created: {filename} ({file_size_kb} KB)", dest_path
        except Exception as e:
            return False, f"Failed to create backup: {str(e)}", ""

    @staticmethod
    def list_backups() -> List[Dict[str, Any]]:
        backup_dir = BackupService.get_backup_dir()
        if not os.path.exists(backup_dir):
            return []

        backups = []
        for f in os.listdir(backup_dir):
            if f.endswith((".sqlite", ".db")):
                full_path = os.path.join(backup_dir, f)
                stat = os.stat(full_path)
                backups.append({
                    "filename": f,
                    "filepath": full_path,
                    "size_kb": round(stat.st_size / 1024, 2),
                    "created_at": datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                })

        backups.sort(key=lambda x: x["created_at"], reverse=True)
        return backups

    @staticmethod
    def restore_backup(backup_filepath: str) -> Tuple[bool, str]:
        """
        Validates the backup file and restores it to the active database location.
        """
        if not os.path.exists(backup_filepath):
            return False, "Selected backup file does not exist."

        # Verify sqlite file integrity
        try:
            test_conn = sqlite3.connect(backup_filepath)
            cursor = test_conn.cursor()
            cursor.execute("PRAGMA integrity_check;")
            res = cursor.fetchone()
            if not res or res[0] != "ok":
                test_conn.close()
                return False, "Corrupted backup file: integrity check failed."

            cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='books';")
            if cursor.fetchone()[0] == 0:
                test_conn.close()
                return False, "Invalid backup: Missing expected database tables."
            test_conn.close()
        except Exception as e:
            return False, f"Verification error: {str(e)}"

        try:
            active_db_path = get_db_path()

            # Create an automatic pre-restore safety snapshot
            safety_backup = active_db_path + ".pre_restore"
            if os.path.exists(active_db_path):
                shutil.copy2(active_db_path, safety_backup)

            shutil.copy2(backup_filepath, active_db_path)
            return True, f"Database restored successfully from {os.path.basename(backup_filepath)}."
        except Exception as e:
            return False, f"Restore failed: {str(e)}"
