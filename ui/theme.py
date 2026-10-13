"""
Centralized Design System and Theme Tokens for Alexandria Library Management System.
"""

class Theme:
    # Fonts
    FONT_FAMILY = "Segoe UI"
    FONT_TITLE = ("Segoe UI", 20, "bold")
    FONT_SUBTITLE = ("Segoe UI", 14, "bold")
    FONT_BODY = ("Segoe UI", 12)
    FONT_BODY_BOLD = ("Segoe UI", 12, "bold")
    FONT_CAPTION = ("Segoe UI", 10)
    FONT_CAPTION_BOLD = ("Segoe UI", 10, "bold")
    FONT_STAT_VAL = ("Segoe UI", 24, "bold")

    # Colors - Dual theme (light_color, dark_color) tuple format for CustomTkinter
    BG_MAIN = ("#f8fafc", "#0f172a")         # Main content background
    BG_SIDEBAR = ("#0f172a", "#090d16")      # Sidebar navy background
    BG_CARD = ("#ffffff", "#1e293b")         # Card background
    BG_CARD_HOVER = ("#f1f5f9", "#273549")   # Hover state
    BG_INPUT = ("#f8fafc", "#172033")        # Form input fields
    
    BORDER = ("#e2e8f0", "#334155")          # Subtle border
    BORDER_FOCUSED = ("#0d9488", "#14b8a6")  # Active border
    
    TEXT_PRIMARY = ("#0f172a", "#f8fafc")    # Headings and primary text
    TEXT_SECONDARY = ("#475569", "#94a3b8")  # Subtitles and table text
    TEXT_MUTED = ("#94a3b8", "#64748b")      # Hints and disabled text
    TEXT_WHITE = "#ffffff"

    # Accents & Semantics
    PRIMARY = ("#0d9488", "#14b8a6")         # Teal accent
    PRIMARY_HOVER = ("#0f766e", "#0d9488")
    PRIMARY_TEXT = "#ffffff"
    
    SECONDARY = ("#e2e8f0", "#334155")
    SECONDARY_HOVER = ("#cbd5e1", "#475569")
    SECONDARY_TEXT = ("#1e293b", "#f8fafc")

    SUCCESS = ("#10b981", "#059669")
    SUCCESS_BG = ("#d1fae5", "#064e3b")
    SUCCESS_TEXT = ("#065f46", "#34d399")

    DANGER = ("#ef4444", "#dc2626")
    DANGER_HOVER = ("#dc2626", "#b91c1c")
    DANGER_BG = ("#fee2e2", "#7f1d1d")
    DANGER_TEXT = ("#991b1b", "#f87171")

    WARNING = ("#f59e0b", "#d97706")
    WARNING_BG = ("#fef3c7", "#78350f")
    WARNING_TEXT = ("#92400e", "#fbbf24")

    INFO = ("#3b82f6", "#2563eb")
    INFO_BG = ("#dbeafe", "#1e3a8a")
    INFO_TEXT = ("#1e40af", "#60a5fa")

    # Corner radiuses
    RADIUS_CARD = 12
    RADIUS_BUTTON = 8
    RADIUS_INPUT = 8
    RADIUS_BADGE = 14
