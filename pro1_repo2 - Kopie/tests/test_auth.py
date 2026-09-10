import json
import os
import time
from base64 import b64encode

import pytest
from fastapi.testclient import TestClient
from itsdangerous import TimestampSigner

os.environ.setdefault("SESSION_SECRET", "test-secret-only-for-automated-tests")

import DHSNServer as server


@pytest.fixture
def user_store(monkeypatch):
    users: dict[int, dict] = {}
    next_user_id = 1

    def insert_user(username: str, password_hash: str) -> dict:
        nonlocal next_user_id
        if any(user["username"].lower() == username.lower() for user in users.values()):
            raise server.UsernameAlreadyExistsError
        user = {
            "user_id": next_user_id,
            "username": username,
            "password": password_hash,
        }
        users[next_user_id] = user
        next_user_id += 1
        return {"user_id": user["user_id"], "username": user["username"]}

    def find_user_for_login(username: str) -> dict | None:
        return next(
            (user.copy() for user in users.values() if user["username"].lower() == username),
            None,
        )

    def find_public_user_by_id(user_id: int) -> dict | None:
        user = users.get(user_id)
        if user is None:
            return None
        return {"user_id": user["user_id"], "username": user["username"]}

    monkeypatch.setattr(server, "insert_user", insert_user)
    monkeypatch.setattr(server, "find_user_for_login", find_user_for_login)
    monkeypatch.setattr(server, "find_public_user_by_id", find_public_user_by_id)
    return users


def register(client: TestClient, username: str, password: str = "sicheres-passwort"):
    return client.post(
        "/auth/register", json={"username": username, "password": password}
    )


def login(client: TestClient, username: str, password: str = "sicheres-passwort"):
    return client.post("/auth/login", json={"username": username, "password": password})


def test_registration_stores_bcrypt_hash_and_never_returns_password(user_store):
    client = TestClient(server.app)

    response = register(client, "  Alice  ")

    assert response.status_code == 201
    assert response.json() == {"user_id": 1, "username": "alice"}
    assert "password" not in response.text
    assert user_store[1]["password"].startswith("$2")
    assert user_store[1]["password"] != "sicheres-passwort"
    assert server.verify_stored_password("sicheres-passwort", user_store[1]["password"])


def test_registration_rejects_case_insensitive_duplicate(user_store):
    client = TestClient(server.app)
    assert register(client, "Alice").status_code == 201

    response = register(client, "ALICE")

    assert response.status_code == 409
    assert response.json()["detail"] == "Benutzername ist bereits vergeben"


@pytest.mark.parametrize(
    ("username", "password"),
    [
        ("ab", "sicheres-passwort"),
        ("alice", "zu-kurz"),
        ("alice", "x" * 73),
    ],
)
def test_registration_validates_credentials(user_store, username, password):
    response = register(TestClient(server.app), username, password)
    assert response.status_code == 422


def test_login_rejects_wrong_and_legacy_plaintext_passwords(user_store):
    client = TestClient(server.app)
    assert register(client, "alice").status_code == 201
    user_store[2] = {
        "user_id": 2,
        "username": "legacy",
        "password": "altes-klartextpasswort",
    }

    wrong_password = login(client, "alice", "falsches-passwort")
    legacy_password = login(client, "legacy", "altes-klartextpasswort")
    missing_user = login(client, "niemand", "falsches-passwort")

    assert wrong_password.status_code == 401
    assert legacy_password.status_code == 401
    assert missing_user.status_code == 401
    assert wrong_password.json() == legacy_password.json() == missing_user.json()


def test_two_sessions_keep_their_own_identity_and_logout_is_isolated(user_store):
    alice_client = TestClient(server.app)
    bob_client = TestClient(server.app)
    assert register(alice_client, "alice").status_code == 201
    assert register(bob_client, "bob").status_code == 201
    assert login(alice_client, "alice").status_code == 200
    assert login(bob_client, "bob").status_code == 200

    alice_me = alice_client.get("/auth/me", params={"user_id": 2})
    bob_me = bob_client.get("/auth/me", params={"user_id": 1})

    assert alice_me.json() == {"user_id": 1, "username": "alice"}
    assert bob_me.json() == {"user_id": 2, "username": "bob"}
    assert alice_client.post("/auth/logout").status_code == 204
    assert alice_client.get("/auth/me").status_code == 401
    assert bob_client.get("/auth/me").status_code == 200


def test_login_rejects_client_supplied_user_id(user_store):
    client = TestClient(server.app)
    assert register(client, "alice").status_code == 201

    response = client.post(
        "/auth/login",
        json={
            "username": "alice",
            "password": "sicheres-passwort",
            "user_id": 999,
        },
    )

    assert response.status_code == 422


def test_missing_tampered_and_expired_sessions_are_rejected(user_store):
    client = TestClient(server.app)
    assert client.get("/auth/me").status_code == 401

    client.cookies.set("dhsn_session", "manipuliertes-cookie")
    assert client.get("/auth/me").status_code == 401

    payload = b64encode(json.dumps({"user_id": 1}).encode("utf-8"))
    signer = TimestampSigner(os.environ["SESSION_SECRET"])
    signer.get_timestamp = lambda: int(time.time()) - server.SESSION_MAX_AGE_SECONDS - 1
    expired_cookie = signer.sign(payload).decode("utf-8")
    client.cookies.clear()
    client.cookies.set("dhsn_session", expired_cookie)
    assert client.get("/auth/me").status_code == 401


def test_session_cookie_security_attributes(user_store):
    client = TestClient(server.app)
    assert register(client, "alice").status_code == 201

    response = login(client, "alice")

    cookie_header = response.headers["set-cookie"].lower()
    assert "dhsn_session=" in cookie_header
    assert "httponly" in cookie_header
    assert "samesite=lax" in cookie_header
    assert f"max-age={server.SESSION_MAX_AGE_SECONDS}" in cookie_header


def test_removed_user_endpoint_and_public_endpoints(user_store, monkeypatch):
    client = TestClient(server.app)
    assert client.get("/users/1").status_code == 404
    assert client.get("/hello").status_code == 200

    class MovieResponse:
        status_code = 200

        @staticmethod
        def json():
            return {"results": []}

    monkeypatch.setattr(server.requests, "get", lambda *args, **kwargs: MovieResponse())
    assert client.get("/movie/search", params={"query": "Matrix"}).status_code == 200
