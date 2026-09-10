import os
import threading
import time
from contextlib import asynccontextmanager
from typing import Annotated

import bcrypt
import requests
import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from pydantic import BaseModel, ConfigDict, field_validator
from psycopg import errors as psycopg_errors
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from starlette.middleware.sessions import SessionMiddleware

from auth_security import hash_password, normalize_username, validate_password

load_dotenv()

UVICORN_HOST = os.getenv("UVICORN_HOST", "127.0.0.1")
UVICORN_PORT = int(os.getenv("UVICORN_PORT", "8000"))

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWD = os.getenv("DB_PASSWD")

TMDB_URL = os.getenv("TMDB_URL")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

SESSION_SECRET = os.getenv("SESSION_SECRET")
SESSION_HTTPS_ONLY = os.getenv("SESSION_HTTPS_ONLY", "false").lower() in {
    "1",
    "true",
    "yes",
    "on",
}
SESSION_MAX_AGE_SECONDS = 8 * 60 * 60

if not SESSION_SECRET:
    raise RuntimeError(
        "SESSION_SECRET fehlt. Bitte einen langen, zufaelligen Wert in der .env-Datei setzen."
    )

DBConnectionPool: ConnectionPool | None = None


class Credentials(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str
    password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        normalized = normalize_username(value)
        if not 3 <= len(normalized) <= 50:
            raise ValueError("Der Benutzername muss zwischen 3 und 50 Zeichen lang sein.")
        return normalized

    @field_validator("password")
    @classmethod
    def validate_password_value(cls, value: str) -> str:
        validate_password(value)
        return value


class PublicUser(BaseModel):
    user_id: int
    username: str


class UsernameAlreadyExistsError(Exception):
    pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    createDBConnectionPool()
    print("Anwendung startet: Synchroner Connection Pool initialisiert.")

    background_thread = threading.Thread(target=MainThread, daemon=True)
    background_thread.start()

    yield

    background_thread.join(timeout=5.0)
    print("Anwendung schliesst: Alle Pool-Verbindungen werden getrennt.")
    closeDBConnectionPool()


app = FastAPI(title="FilmeSerienTracker", lifespan=lifespan)
app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    session_cookie="dhsn_session",
    max_age=SESSION_MAX_AGE_SECONDS,
    same_site="lax",
    https_only=SESSION_HTTPS_ONLY,
)


def MainThread():
    while True:
        try:
            print("Fuehre periodischen DB-Check im Hintergrund-Thread aus...")
            time.sleep(10)
        except Exception as exception:
            print(f"Fehler im Hintergrund-Task: {exception}")
            break


def createDBConnectionPool():
    """Erstellt und oeffnet den synchronen Connection Pool."""
    global DBConnectionPool
    try:
        DBConnectionPool = ConnectionPool(
            conninfo=(
                f"postgresql://{DB_USER}:{DB_PASSWD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
            ),
            min_size=1,
            max_size=100,
            timeout=5.0,
        )
        DBConnectionPool.open(wait=True, timeout=5.0)
        print("Synchroner Connection Pool erstellt.")
    except Exception as exception:
        DBConnectionPool = None
        raise RuntimeError("Datenbankverbindung konnte nicht hergestellt werden") from exception


def closeDBConnectionPool():
    """Schliesst den synchronen Connection Pool."""
    global DBConnectionPool
    if DBConnectionPool:
        try:
            DBConnectionPool.close()
            print("DB Connection Pool wurde geschlossen")
        except Exception as exception:
            print(f"Fehler beim Schliessen des Connection Pools: {exception}")


def require_database_pool() -> ConnectionPool:
    if DBConnectionPool is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Datenbank ist nicht verfuegbar",
        )
    return DBConnectionPool


def insert_user(username: str, password_hash: str) -> dict:
    pool = require_database_pool()
    try:
        with pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    INSERT INTO users (username, password)
                    VALUES (%s, %s)
                    RETURNING user_id, username
                    """,
                    (username, password_hash),
                )
                return cursor.fetchone()
    except psycopg_errors.UniqueViolation as exception:
        raise UsernameAlreadyExistsError from exception
    except HTTPException:
        raise
    except Exception as exception:
        print(f"Fehler beim Anlegen eines Benutzers: {type(exception).__name__}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Datenbank ist voruebergehend nicht verfuegbar",
        ) from exception


def find_user_for_login(username: str) -> dict | None:
    pool = require_database_pool()
    try:
        with pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    SELECT user_id, username, password
                    FROM users
                    WHERE lower(username) = %s
                    """,
                    (username,),
                )
                return cursor.fetchone()
    except HTTPException:
        raise
    except Exception as exception:
        print(f"Fehler bei der Benutzerabfrage: {type(exception).__name__}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Datenbank ist voruebergehend nicht verfuegbar",
        ) from exception


def find_public_user_by_id(user_id: int) -> dict | None:
    pool = require_database_pool()
    try:
        with pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    SELECT user_id, username
                    FROM users
                    WHERE user_id = %s
                    """,
                    (user_id,),
                )
                return cursor.fetchone()
    except HTTPException:
        raise
    except Exception as exception:
        print(f"Fehler bei der Sitzungspruefung: {type(exception).__name__}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Datenbank ist voruebergehend nicht verfuegbar",
        ) from exception


def verify_stored_password(password: str, stored_password: object) -> bool:
    """Akzeptiert nur bcrypt-Hashes und damit keine alten Klartextwerte."""
    if not isinstance(stored_password, str) or not stored_password.startswith(
        ("$2a$", "$2b$", "$2y$")
    ):
        return False
    try:
        return bcrypt.checkpw(password.encode("utf-8"), stored_password.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def get_current_user(request: Request) -> dict:
    user_id = request.session.get("user_id")
    if not isinstance(user_id, int):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Anmeldung erforderlich",
        )

    user = find_public_user_by_id(user_id)
    if user is None:
        request.session.clear()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Anmeldung erforderlich",
        )
    return user


CurrentUser = Annotated[dict, Depends(get_current_user)]


@app.post("/auth/register", response_model=PublicUser, status_code=status.HTTP_201_CREATED)
def register(credentials: Credentials):
    try:
        return insert_user(credentials.username, hash_password(credentials.password))
    except UsernameAlreadyExistsError as exception:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Benutzername ist bereits vergeben",
        ) from exception


@app.post("/auth/login", response_model=PublicUser)
def login(credentials: Credentials, request: Request):
    user = find_user_for_login(credentials.username)
    if user is None or not verify_stored_password(credentials.password, user.get("password")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Benutzername oder Passwort ist falsch",
        )

    request.session.clear()
    request.session["user_id"] = user["user_id"]
    return {"user_id": user["user_id"], "username": user["username"]}


@app.get("/auth/me", response_model=PublicUser)
def me(current_user: CurrentUser):
    return current_user


@app.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request):
    request.session.clear()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/hello")
def hello():
    return {"message": "Hello World"}


@app.get("/movie/search")
def searchMovie(query: str):
    if not TMDB_URL or not TMDB_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="TMDB ist nicht konfiguriert",
        )

    try:
        response = requests.get(
            TMDB_URL + "/search/movie",
            params={
                "api_key": TMDB_API_KEY,
                "query": query,
                "language": "de-DE",
            },
            timeout=10.0,
        )
    except requests.RequestException as exception:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="TMDB-Anfrage fehlgeschlagen",
        ) from exception

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail="TMDB-Anfrage fehlgeschlagen",
        )
    return response.json()


if __name__ == "__main__":
    uvicorn.run(app, host=UVICORN_HOST, port=UVICORN_PORT, log_level="info")
