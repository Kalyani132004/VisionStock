# validation.py - rules for name, email and password
# The register API and the create_admin command both use these functions,
# so the rules are the same everywhere.

import re

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def clean_name(name: str) -> str:
    name = " ".join(name.split())          # remove extra spaces
    if len(name) < 2:
        raise ValueError("Name must have at least 2 characters")
    if len(name) > 100:
        raise ValueError("Name is too long (maximum 100 characters)")
    return name


def clean_email(email: str) -> str:
    # Emails are saved in small letters, so Test@x.com and test@x.com are the same user
    email = email.strip().lower()
    if len(email) > 120 or not EMAIL_PATTERN.match(email):
        raise ValueError("Please enter a valid email address")
    return email


def check_password_rules(password: str) -> str:
    if len(password) < 8:
        raise ValueError("Password must have at least 8 characters")
    # bcrypt can only use the first 72 bytes, so longer passwords are not allowed
    if len(password.encode("utf-8")) > 72:
        raise ValueError("Password is too long (maximum 72 characters)")
    if not re.search(r"[A-Za-z]", password) or not re.search(r"[0-9]", password):
        raise ValueError("Password must contain at least one letter and one number")
    return password
