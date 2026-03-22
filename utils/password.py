import bcrypt


def hash_password(password: str) -> str:
    """Hash a password for storage."""

    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(stored_password: str, provided_password: str) -> bool:
    """Verify a password against a stored hash."""

    return bcrypt.checkpw(
        provided_password.encode("utf-8"),
        stored_password.encode("utf-8"),
    )
