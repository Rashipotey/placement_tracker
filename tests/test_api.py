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


# ---- cross-user access: missing -> 404, owned by someone else -> 403 (CPT-11) ----

def _make_application(client, user, company):
    r = client.post("/applications", json={"company_id": company["id"], "notes": "mine"}, headers=user["headers"])
    assert r.status_code == 201
    return r.json()


def test_other_user_gets_403_on_application(client, user, other_user, company):
    a = _make_application(client, user, company)
    hb = other_user["headers"]
    url = f"/applications/{a['id']}"
    assert client.get(url, headers=hb).status_code == 403
    assert client.put(url, json={"status": "REJECTED", "notes": "hacked"}, headers=hb).status_code == 403
    assert client.delete(url, headers=hb).status_code == 403
    # owner still has access and the data is unchanged
    r = client.get(url, headers=user["headers"])
    assert r.status_code == 200 and r.json() == a
    # B's own list does not include A's application
    assert client.get("/applications", headers=hb).json() == []


def test_other_user_gets_403_on_rounds(client, user, other_user, company):
    a = _make_application(client, user, company)
    ha, hb = user["headers"], other_user["headers"]
    base = f"/applications/{a['id']}/rounds"
    rnd = client.post(base, json={"round_name": "R1", "feedback": "f"}, headers=ha).json()

    assert client.get(base, headers=hb).status_code == 403
    assert client.post(base, json={"round_name": "evil"}, headers=hb).status_code == 403
    assert client.get(f"{base}/{rnd['id']}", headers=hb).status_code == 403
    assert client.put(f"{base}/{rnd['id']}", json={"status": "FAILED"}, headers=hb).status_code == 403
    assert client.delete(f"{base}/{rnd['id']}", headers=hb).status_code == 403

    # owner's data is unchanged
    assert client.get(base, headers=ha).json() == [rnd]


def test_missing_application_and_round_return_404(client, user, company):
    h = user["headers"]
    missing = uuid.uuid4()
    assert client.get(f"/applications/{missing}", headers=h).status_code == 404
    assert client.put(f"/applications/{missing}", json={"notes": "x"}, headers=h).status_code == 404
    assert client.delete(f"/applications/{missing}", headers=h).status_code == 404
    assert client.get(f"/applications/{missing}/rounds", headers=h).status_code == 404
    assert client.post(f"/applications/{missing}/rounds", json={"round_name": "R"}, headers=h).status_code == 404

    a = _make_application(client, user, company)
    base = f"/applications/{a['id']}/rounds"
    assert client.get(f"{base}/{missing}", headers=h).status_code == 404
    assert client.put(f"{base}/{missing}", json={"status": "PASSED"}, headers=h).status_code == 404
    assert client.delete(f"{base}/{missing}", headers=h).status_code == 404


def test_round_under_wrong_application_returns_404(client, user, company):
    h = user["headers"]
    a1 = _make_application(client, user, company)
    a2 = _make_application(client, user, company)
    rnd = client.post(f"/applications/{a1['id']}/rounds", json={"round_name": "R1"}, headers=h).json()
    assert client.get(f"/applications/{a2['id']}/rounds/{rnd['id']}", headers=h).status_code == 404


def test_unauthenticated_rounds_and_applications_return_401(client):
    assert client.get(f"/applications/{uuid.uuid4()}").status_code == 401
    assert client.get(f"/applications/{uuid.uuid4()}/rounds").status_code == 401
