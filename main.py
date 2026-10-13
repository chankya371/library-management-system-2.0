import sys
import logging
import customtkinter as ctk

from database.schema import initialize_database
from database.seed_data import seed_database
from services.settings_service import SettingsService
from ui.main_window import MainWindow

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("Alexandria")


def main():
    try:
        # 1. Initialize and seed database
        logger.info("Initializing database...")
        initialize_database()
        seed_database()

        # 2. Configure CustomTkinter themes
        saved_theme = SettingsService.get_setting("appearance_mode", "Dark")
        ctk.set_appearance_mode(saved_theme)
        ctk.set_default_color_theme("blue")

        logger.info("Starting Alexandria Library Management System...")
        app = MainWindow()
        app.mainloop()

    except KeyboardInterrupt:
        logger.info("Application closed by user.")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Fatal application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
