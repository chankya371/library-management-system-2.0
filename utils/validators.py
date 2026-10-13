import re
import datetime
from typing import Tuple


def validate_isbn(isbn: str) -> Tuple[bool, str]:
    """
    Validates ISBN-10 or ISBN-13 format.
    Allows hyphens and spaces.
    """
    if not isbn or not isbn.strip():
        return False, "ISBN is required."

    cleaned = re.sub(r"[\s-]", "", isbn.strip()).upper()
    if len(cleaned) == 10:
        if not re.match(r"^\d{9}[\dX]$", cleaned):
            return False, "ISBN-10 must contain 9 digits followed by a digit or 'X'."
        # Validate checksum for ISBN-10
        total = 0
        for i in range(9):
            total += int(cleaned[i]) * (10 - i)
        last_char = 10 if cleaned[9] == 'X' else int(cleaned[9])
        total += last_char
        if total % 11 != 0:
            return False, "Invalid ISBN-10 check digit."
        return True, ""
    elif len(cleaned) == 13:
        if not re.match(r"^\d{13}$", cleaned):
            return False, "ISBN-13 must contain exactly 13 digits."
        # Validate checksum for ISBN-13
        total = 0
        for i in range(12):
            total += int(cleaned[i]) * (1 if i % 2 == 0 else 3)
        check = (10 - (total % 10)) % 10
        if check != int(cleaned[12]):
            return False, "Invalid ISBN-13 check digit."
        return True, ""
    else:
        return False, "ISBN must be either 10 or 13 digits long."


def validate_email(email: str) -> Tuple[bool, str]:
    """Validates standard email address structure."""
    if not email or not email.strip():
        return False, "Email address is required."
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email.strip()):
        return False, "Please enter a valid email address (e.g., user@example.com)."
    return True, ""


def validate_phone(phone: str) -> Tuple[bool, str]:
    """Validates phone number format."""
    if not phone or not phone.strip():
        return False, "Phone number is required."
    cleaned = re.sub(r"[\s\-\(\)\+\.]", "", phone.strip())
    if not cleaned.isdigit() or len(cleaned) < 7 or len(cleaned) > 15:
        return False, "Phone number must contain between 7 and 15 digits."
    return True, ""


def validate_publication_year(year: any) -> Tuple[bool, str]:
    """Validates publication year within reasonable historical and future bounds."""
    if year is None or str(year).strip() == "":
        return True, ""  # Optional
    try:
        y = int(year)
        current_year = datetime.date.today().year
        if y < 1000 or y > current_year + 2:
            return False, f"Publication year must be between 1000 and {current_year + 2}."
        return True, ""
    except (ValueError, TypeError):
        return False, "Publication year must be a valid 4-digit number."


def validate_positive_int(value: any, field_name: str = "Value", allow_zero: bool = False) -> Tuple[bool, str]:
    """Validates integer numbers."""
    try:
        val = int(value)
        if allow_zero and val < 0:
            return False, f"{field_name} cannot be negative."
        elif not allow_zero and val <= 0:
            return False, f"{field_name} must be greater than zero."
        return True, ""
    except (ValueError, TypeError):
        return False, f"{field_name} must be a valid whole number."


def validate_non_empty(value: str, field_name: str) -> Tuple[bool, str]:
    """Validates required text fields."""
    if not value or not str(value).strip():
        return False, f"{field_name} is required."
    return True, ""
