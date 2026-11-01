import os
import uuid

# Tests run against the configured DATABASE_URL (see README). They only create
# records carrying a unique prefix and delete exactly those records afterwards.
os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select, update

from app.database.connection import SessionLocal
from app.main import app
from app.models.application import Application
from app.models.company import Company
from app.models.round import Round
from app.models.user import User

PREFIX = f"pytest_{uuid.uuid4().hex[:10]}_"


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_records():
    yield
    db = SessionLocal()
    try:
        user_ids = select(User.id).where(User.email.like(PREFIX + "%"))
        company_ids = select(Company.id).where(Company.name.like(PREFIX + "%"))
        app_ids = select(Application.id).where(
            Application.user_id.in_(user_ids) | Application.company_id.in_(company_ids)
        )
        db.execute(delete(Round).where(Round.application_id.in_(app_ids)))
        db.execute(delete(Application).where(Application.id.in_(app_ids)))
        db.execute(delete(Company).where(Company.id.in_(company_ids)))
        db.execute(delete(User).where(User.id.in_(user_ids)))
        db.commit()
    finally:
        db.close()


def _register_and_login(client):
    email = f"{PREFIX}{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"
    r = client.post("/auth/register", json={"name": PREFIX + "user", "email": email, "password": password})
    assert r.status_code == 200, r.text
    r = client.post("/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return {"email": email, "password": password,
            "headers": {"Authorization": "Bearer " + r.json()["access_token"]}}


@pytest.fixture()
def user(client):
    return _register_and_login(client)


@pytest.fixture()
def other_user(client):
    return _register_and_login(client)


def _make_admin(client):
    """Register a prefixed test user, promote it with a direct DB update (never via the API)
    and log in again so the token carries the ADMIN role claim."""
    u = _register_and_login(client)
    db = SessionLocal()
    try:
        db.execute(update(User).where(User.email == u["email"]).values(role="ADMIN"))
        db.commit()
    finally:
        db.close()
    r = client.post("/auth/login", json={"email": u["email"], "password": u["password"]})
    u["headers"] = {"Authorization": "Bearer " + r.json()["access_token"]}
    return u


@pytest.fixture()
def admin(client):
    return _make_admin(client)


@pytest.fixture()
def company(client, admin):
    r = client.post("/companies", json={"name": PREFIX + "Acme", "role": "SDE"}, headers=admin["headers"])
    assert r.status_code == 201, r.text
    return r.json()
