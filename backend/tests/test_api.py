import os
import time
from typing import Iterator

import httpx
import pytest

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


@pytest.fixture(scope="session")
def client() -> Iterator[httpx.Client]:
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as c:
        yield c


def test_health(client: httpx.Client) -> None:
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"


def test_user_flow(client: httpx.Client) -> None:
    # create user
    email = "user@example.com"
    r = client.post("/api/v1/users/", json={"email": email, "password": "secret", "full_name": "User One"})
    assert r.status_code in (200, 201, 400)  # 400 if already created

    # login
    r = client.post("/api/v1/auth/login", json={"email": email, "password": "secret"})
    assert r.status_code == 200
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # list users
    r = client.get("/api/v1/users/", headers=headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_accounting_flow(client: httpx.Client) -> None:
    # Create basic accounts
    r = client.post("/api/v1/accounts", json={"code": "1000", "name": "Cash", "type": "asset"})
    assert r.status_code in (200, 201, 400)
    r = client.post("/api/v1/accounts", json={"code": "2000", "name": "Revenue", "type": "revenue"})
    assert r.status_code in (200, 201, 400)

    # Create balanced journal
    r = client.post(
        "/api/v1/journals",
        json={
            "date": "2024-01-01",
            "reference": "INV-1",
            "description": "Sale",
            "lines": [
                {"account_id": 1, "debit": 100.0, "credit": 0.0},
                {"account_id": 2, "debit": 0.0, "credit": 100.0},
            ],
        },
    )
    assert r.status_code in (200, 201)
    entry_id = r.json()["id"]

    # Post entry
    r = client.post(f"/api/v1/journals/{entry_id}/post")
    assert r.status_code == 200

    # Trial balance
    r = client.get("/api/v1/reports/trial-balance")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
