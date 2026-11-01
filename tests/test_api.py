import uuid

from tests.conftest import PREFIX


def test_register_login_and_me(client, user):
    r = client.get("/users/me", headers=user["headers"])
    assert r.status_code == 200
    assert r.json()["email"] == user["email"]


def test_register_duplicate_email_rejected(client, user):
    r = client.post("/auth/register", json={"name": "x", "email": user["email"], "password": "password123"})
    assert r.status_code == 400


def test_login_wrong_password(client, user):
    r = client.post("/auth/login", params={"email": user["email"], "password": "wrong-password"})
    assert r.status_code == 401


def test_protected_routes_require_token(client):
    assert client.get("/users/me").status_code == 401
    assert client.get("/companies").status_code == 401
    assert client.get("/applications").status_code == 401


def test_company_validation_and_crud(client, user, company):
    h = user["headers"]
    assert client.post("/companies", json={"name": PREFIX + "x"}, headers=h).status_code == 422
    assert client.get(f"/companies/{company['id']}", headers=h).json()["role"] == "SDE"
    r = client.put(f"/companies/{company['id']}", json={"location": "BLR"}, headers=h)
    assert r.status_code == 200 and r.json()["location"] == "BLR"
    assert any(c["id"] == company["id"] for c in client.get("/companies", headers=h).json())
    assert client.get(f"/companies/{uuid.uuid4()}", headers=h).status_code == 404


def test_application_crud(client, user, company):
    h = user["headers"]
    r = client.post("/applications", json={"company_id": company["id"], "notes": "n"}, headers=h)
    assert r.status_code == 201
    app_ = r.json()
    assert app_["status"] == "APPLIED"
    assert app_["user_id"] == client.get("/users/me", headers=h).json()["id"]

    assert [a["id"] for a in client.get("/applications", headers=h).json()] == [app_["id"]]
    assert client.get("/applications?status=OFFER", headers=h).json() == []

    r = client.put(f"/applications/{app_['id']}", json={"status": "OFFER"}, headers=h)
    assert r.status_code == 200 and r.json()["status"] == "OFFER"

    assert client.delete(f"/applications/{app_['id']}", headers=h).status_code == 204
    assert client.get("/applications", headers=h).json() == []


def test_application_validation(client, user, company):
    h = user["headers"]
    assert client.post("/applications", json={"company_id": str(uuid.uuid4())}, headers=h).status_code == 422
    r = client.post("/applications", json={"company_id": company["id"], "status": "NOPE"}, headers=h)
    assert r.status_code == 422


def test_company_delete_blocked_while_referenced(client, user, company):
    h = user["headers"]
    a = client.post("/applications", json={"company_id": company["id"]}, headers=h).json()
    assert client.delete(f"/companies/{company['id']}", headers=h).status_code == 409
    client.delete(f"/applications/{a['id']}", headers=h)
    assert client.delete(f"/companies/{company['id']}", headers=h).status_code == 204


def test_applications_list_only_own(client, user, company):
    # A second user sees none of the first user's applications.
    other_email = f"{PREFIX}{uuid.uuid4().hex[:8]}@example.com"
    client.post("/auth/register", json={"name": PREFIX + "o", "email": other_email, "password": "password123"})
    tok = client.post("/auth/login", params={"email": other_email, "password": "password123"}).json()["access_token"]
    client.post("/applications", json={"company_id": company["id"]}, headers=user["headers"])
    assert client.get("/applications", headers={"Authorization": "Bearer " + tok}).json() == []


def test_rounds_crud_for_owner(client, user, company):
    h = user["headers"]
    a = client.post("/applications", json={"company_id": company["id"]}, headers=h).json()
    base = f"/applications/{a['id']}/rounds"
    r = client.post(base, json={"round_name": "R1"}, headers=h)
    assert r.status_code == 201 and r.json()["status"] == "PENDING"
    rid = r.json()["id"]
    assert len(client.get(base, headers=h).json()) == 1
    r = client.put(f"{base}/{rid}", json={"status": "PASSED", "feedback": "ok"}, headers=h)
    assert r.status_code == 200 and r.json()["status"] == "PASSED"
    assert client.put(f"{base}/{rid}", json={"status": "X"}, headers=h).status_code == 422
    assert client.delete(f"{base}/{rid}", headers=h).status_code == 204
    assert client.get(base, headers=h).json() == []
