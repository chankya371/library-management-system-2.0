from typing import Dict, Any, Optional
from database.db_connection import get_db_cursor


class SettingsService:
    """Provides configuration retrieval and persistent updates."""

    @staticmethod
    def get_setting(key: str, default: str = "") -> str:
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("SELECT value FROM settings WHERE key = ?;", (key,))
            row = cursor.fetchone()
            return row["value"] if row else default

    @staticmethod
    def get_all_settings() -> Dict[str, str]:
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("SELECT key, value FROM settings;")
            rows = cursor.fetchall()
            return {r["key"]: r["value"] for r in rows}

    @staticmethod
    def update_settings(settings_dict: Dict[str, str]) -> None:
        with get_db_cursor() as cursor:
            for key, val in settings_dict.items():
                cursor.execute(
                    """
                    INSERT INTO settings (key, value)
                    VALUES (?, ?)
                    ON CONFLICT(key) DO UPDATE SET value = excluded.value;
                    """,
                    (key, str(val)),
                )

    @staticmethod
    def get_daily_fine_rate() -> float:
        try:
            return float(SettingsService.get_setting("daily_fine_rate", "1.00"))
        except ValueError:
            return 1.00

    @staticmethod
    def get_borrowing_period_days() -> int:
        try:
            return int(SettingsService.get_setting("borrowing_period_days", "14"))
        except ValueError:
            return 14

    @staticmethod
    def get_max_books_per_member() -> int:
        try:
            return int(SettingsService.get_setting("max_books_per_member", "5"))
        except ValueError:
            return 5

    @staticmethod
    def get_currency_symbol() -> str:
        return SettingsService.get_setting("currency_symbol", "$")
