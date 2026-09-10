import bcrypt


def normalize_username(username: str) -> str:
    return username.strip().lower()


def validate_password(password: str) -> None:
    password_length = len(password.encode("utf-8"))
    if not 8 <= password_length <= 72:
        raise ValueError("Das Passwort muss zwischen 8 und 72 UTF-8-Bytes lang sein.")


def hash_password(password: str) -> str:
    validate_password(password)
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
