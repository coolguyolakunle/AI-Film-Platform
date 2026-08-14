import re

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def is_valid_email(email: str) -> bool:
    return bool(email) and bool(EMAIL_RE.match(email))


def is_valid_password(password: str) -> tuple[bool, str]:
    """Return (is_valid, error_message)."""
    if not password or len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number."
    if not any(c.isalpha() for c in password):
        return False, "Password must contain at least one letter."
    return True, ""


def validate_registration_payload(data: dict) -> tuple[bool, str]:
    if not data:
        return False, "Request body is required."

    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not name:
        return False, "Name is required."
    if not is_valid_email(email):
        return False, "A valid email is required."

    valid_pw, pw_error = is_valid_password(password)
    if not valid_pw:
        return False, pw_error

    return True, ""
