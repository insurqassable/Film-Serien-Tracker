import argparse
import getpass
import os
import sys

import psycopg
from dotenv import load_dotenv

from auth_security import hash_password, normalize_username, validate_password


def parse_args():
    parser = argparse.ArgumentParser(
        description="Setzt das Passwort eines vorhandenen Testnutzers als bcrypt-Hash."
    )
    parser.add_argument("username", help="Benutzername des vorhandenen Kontos")
    return parser.parse_args()


def main() -> int:
    load_dotenv()
    args = parse_args()
    username = normalize_username(args.username)

    password = getpass.getpass("Neues Passwort: ")
    confirmation = getpass.getpass("Passwort wiederholen: ")
    if password != confirmation:
        print("Die Passwoerter stimmen nicht ueberein.", file=sys.stderr)
        return 1

    try:
        validate_password(password)
    except ValueError as exception:
        print(str(exception), file=sys.stderr)
        return 1

    required_variables = ("DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWD")
    missing = [name for name in required_variables if not os.getenv(name)]
    if missing:
        print(f"Fehlende Umgebungsvariablen: {', '.join(missing)}", file=sys.stderr)
        return 1

    try:
        with psycopg.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWD"),
        ) as connection:
            result = connection.execute(
                """
                UPDATE users
                SET password = %s
                WHERE lower(username) = %s
                RETURNING user_id
                """,
                (hash_password(password), username),
            ).fetchone()
    except psycopg.Error as exception:
        print(f"Datenbankfehler: {exception.sqlstate or 'unbekannt'}", file=sys.stderr)
        return 1

    if result is None:
        print(f"Benutzer '{username}' wurde nicht gefunden.", file=sys.stderr)
        return 1

    print(f"Passwort fuer '{username}' wurde als bcrypt-Hash gespeichert.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
