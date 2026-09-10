import os
import uuid

import pytest
from fastapi.testclient import TestClient
from psycopg_pool import ConnectionPool

os.environ.setdefault("SESSION_SECRET", "test-secret-only-for-automated-tests")

import DHSNServer as server


TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")


@pytest.mark.skipif(
    not TEST_DATABASE_URL,
    reason="TEST_DATABASE_URL ist nicht gesetzt; PostgreSQL-Integrationstest wird uebersprungen.",
)
def test_complete_auth_flow_against_test_database(monkeypatch):
    pool = ConnectionPool(conninfo=TEST_DATABASE_URL, min_size=1, max_size=2, open=True)
    monkeypatch.setattr(server, "DBConnectionPool", pool)
    username = f"auth-test-{uuid.uuid4().hex[:12]}"
    client = TestClient(server.app)

    try:
        register_response = client.post(
            "/auth/register",
            json={"username": username, "password": "sicheres-passwort"},
        )
        assert register_response.status_code == 201
        user_id = register_response.json()["user_id"]

        with pool.connection() as connection:
            stored_password = connection.execute(
                "SELECT password FROM users WHERE user_id = %s", (user_id,)
            ).fetchone()[0]
        assert stored_password.startswith("$2")
        assert stored_password != "sicheres-passwort"

        assert client.post(
            "/auth/login",
            json={"username": username, "password": "sicheres-passwort"},
        ).status_code == 200
        assert client.get("/auth/me").json() == {
            "user_id": user_id,
            "username": username,
        }
        assert client.post("/auth/logout").status_code == 204
        assert client.get("/auth/me").status_code == 401
    finally:
        with pool.connection() as connection:
            connection.execute("DELETE FROM users WHERE username = %s", (username,))
        pool.close()
