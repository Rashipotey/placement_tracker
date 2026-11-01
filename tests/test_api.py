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
    r = client.post("/auth/login", json={"email": user["email"], "password": "wrong-password"})
    assert r.status_code == 401


def test_protected_routes_require_token(client):
    assert client.get("/users/me").status_code == 401
    assert client.get("/companies").status_code == 401
    assert client.get("/applications").status_code == 401


def test_company_validation_and_crud(client, admin, company):
    h = admin["headers"]
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


def test_company_delete_blocked_while_referenced(client, user, admin, company):
    h = user["headers"]
    a = client.post("/applications", json={"company_id": company["id"]}, headers=h).json()
    assert client.delete(f"/companies/{company['id']}", headers=admin["headers"]).status_code == 409
    client.delete(f"/applications/{a['id']}", headers=h)
    assert client.delete(f"/companies/{company['id']}", headers=admin["headers"]).status_code == 204


def test_applications_list_only_own(client, user, company):
    # A second user sees none of the first user's applications.
    other_email = f"{PREFIX}{uuid.uuid4().hex[:8]}@example.com"
    client.post("/auth/register", json={"name": PREFIX + "o", "email": other_email, "password": "password123"})
    tok = client.post("/auth/login", json={"email": other_email, "password": "password123"}).json()["access_token"]
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


# ---- application.round_id (user-approved: current round of an application) ----

def _round(client, user, application_id, name="R1"):
    r = client.post(f"/applications/{application_id}/rounds", json={"round_name": name}, headers=user["headers"])
    assert r.status_code == 201
    return r.json()


def test_round_id_exposed_and_null_by_default(client, user, company):
    a = _make_application(client, user, company)
    assert a["round_id"] is None
    assert client.get(f"/applications/{a['id']}", headers=user["headers"]).json()["round_id"] is None


def test_set_and_clear_current_round(client, user, company):
    h = user["headers"]
    a = _make_application(client, user, company)
    rnd = _round(client, user, a["id"])
    r = client.put(f"/applications/{a['id']}", json={"round_id": rnd["id"]}, headers=h)
    assert r.status_code == 200 and r.json()["round_id"] == rnd["id"]
    assert client.get("/applications", headers=h).json()[0]["round_id"] == rnd["id"]
    # other fields can be updated without touching round_id
    r = client.put(f"/applications/{a['id']}", json={"status": "INTERVIEWING"}, headers=h)
    assert r.json()["round_id"] == rnd["id"]
    r = client.put(f"/applications/{a['id']}", json={"round_id": None}, headers=h)
    assert r.status_code == 200 and r.json()["round_id"] is None


def test_round_from_another_application_or_missing_is_rejected(client, user, company):
    h = user["headers"]
    a1 = _make_application(client, user, company)
    a2 = _make_application(client, user, company)
    foreign = _round(client, user, a2["id"])
    assert client.put(f"/applications/{a1['id']}", json={"round_id": foreign["id"]}, headers=h).status_code == 422
    assert client.put(f"/applications/{a1['id']}", json={"round_id": str(uuid.uuid4())}, headers=h).status_code == 422
    assert client.get(f"/applications/{a1['id']}", headers=h).json()["round_id"] is None


def test_create_ignores_round_id(client, user, company):
    r = client.post("/applications", json={"company_id": company["id"], "round_id": str(uuid.uuid4())},
                    headers=user["headers"])
    assert r.status_code == 201 and r.json()["round_id"] is None


def test_other_user_cannot_set_round_id(client, user, other_user, company):
    a = _make_application(client, user, company)
    rnd = _round(client, user, a["id"])
    r = client.put(f"/applications/{a['id']}", json={"round_id": rnd["id"]}, headers=other_user["headers"])
    assert r.status_code == 403
    assert client.get(f"/applications/{a['id']}", headers=user["headers"]).json()["round_id"] is None


def test_deleting_current_round_nulls_round_id(client, user, company):
    h = user["headers"]
    a = _make_application(client, user, company)
    current = _round(client, user, a["id"], "current")
    other = _round(client, user, a["id"], "other")
    client.put(f"/applications/{a['id']}", json={"round_id": current["id"]}, headers=h)
    # deleting a non-current round leaves round_id alone
    assert client.delete(f"/applications/{a['id']}/rounds/{other['id']}", headers=h).status_code == 204
    assert client.get(f"/applications/{a['id']}", headers=h).json()["round_id"] == current["id"]
    assert client.delete(f"/applications/{a['id']}/rounds/{current['id']}", headers=h).status_code == 204
    assert client.get(f"/applications/{a['id']}", headers=h).json()["round_id"] is None


def test_deleting_application_with_rounds_removes_them(client, user, company):
    h = user["headers"]
    a = _make_application(client, user, company)
    rnd = _round(client, user, a["id"])
    client.put(f"/applications/{a['id']}", json={"round_id": rnd["id"]}, headers=h)
    assert client.delete(f"/applications/{a['id']}", headers=h).status_code == 204
    assert client.get(f"/applications/{a['id']}/rounds", headers=h).status_code == 404


# ---- roles / RBAC (CPT-33..38, CPT-46, CPT-47) ----

from sqlalchemy import select as _select  # noqa: E402
from sqlalchemy import update as _update  # noqa: E402

from app.database.connection import SessionLocal  # noqa: E402
from app.models.user import User  # noqa: E402
from app.scripts import bootstrap_admin  # noqa: E402


def _db_role(email):
    db = SessionLocal()
    try:
        return db.execute(_select(User.role).where(User.email == email)).scalar_one()
    finally:
        db.close()


def _set_db_role(email, role):
    db = SessionLocal()
    try:
        db.execute(_update(User).where(User.email == email).values(role=role))
        db.commit()
    finally:
        db.close()


def _claims(token):
    from jose import jwt
    from app.core.config import settings
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


def test_register_always_creates_user_even_if_role_sent(client):
    email = f"{PREFIX}{uuid.uuid4().hex[:8]}@example.com"
    r = client.post("/auth/register", json={"name": PREFIX + "x", "email": email, "password": "password123",
                                            "role": "ADMIN", "is_admin": True})
    assert r.status_code == 200
    assert _db_role(email) == "USER"


def test_me_includes_role_and_token_has_role_claim(client, user, admin):
    me = client.get("/users/me", headers=user["headers"]).json()
    assert me["role"] == "USER" and {"id", "name", "email"} <= set(me)
    assert client.get("/users/me", headers=admin["headers"]).json()["role"] == "ADMIN"
    assert _claims(admin["headers"]["Authorization"].split()[1])["role"] == "ADMIN"
    assert _claims(user["headers"]["Authorization"].split()[1])["role"] == "USER"


def test_login_accepts_json_body_and_rejects_bad_credentials(client, user):
    r = client.post("/auth/login", json={"email": user["email"], "password": user["password"]})
    assert r.status_code == 200 and r.json()["access_token"]
    assert client.post("/auth/login", json={"email": user["email"], "password": "nope"}).status_code == 401
    assert client.post("/auth/login", json={"email": PREFIX + "none@example.com", "password": "x"}).status_code == 401
    # credentials are no longer accepted in the query string
    assert client.post("/auth/login", params={"email": user["email"], "password": user["password"]}).status_code == 422


def test_user_can_list_but_not_write_companies(client, user, company):
    h = user["headers"]
    assert client.get("/companies", headers=h).status_code == 200
    assert client.get(f"/companies/{company['id']}", headers=h).status_code == 200
    assert client.post("/companies", json={"name": PREFIX + "n", "role": "r"}, headers=h).status_code == 403
    assert client.put(f"/companies/{company['id']}", json={"location": "X"}, headers=h).status_code == 403
    assert client.delete(f"/companies/{company['id']}", headers=h).status_code == 403
    assert client.get(f"/companies/{company['id']}", headers=h).json()["location"] is None  # unchanged


def test_admin_company_crud(client, admin):
    h = admin["headers"]
    r = client.post("/companies", json={"name": PREFIX + "AdminCo", "role": "QA"}, headers=h)
    assert r.status_code == 201
    cid = r.json()["id"]
    assert client.put(f"/companies/{cid}", json={"location": "PUNE"}, headers=h).json()["location"] == "PUNE"
    assert client.delete(f"/companies/{cid}", headers=h).status_code == 204
    assert client.get(f"/companies/{cid}", headers=h).status_code == 404


def test_company_writes_require_authentication(client, company):
    assert client.post("/companies", json={"name": "x", "role": "y"}).status_code == 401
    assert client.delete(f"/companies/{company['id']}").status_code == 401


def test_admin_has_no_access_to_other_users_applications_or_rounds(client, user, admin, company):
    a = client.post("/applications", json={"company_id": company["id"]}, headers=user["headers"]).json()
    rnd = client.post(f"/applications/{a['id']}/rounds", json={"round_name": "R1"}, headers=user["headers"]).json()
    ha = admin["headers"]
    url = f"/applications/{a['id']}"
    assert client.get(url, headers=ha).status_code == 403
    assert client.put(url, json={"notes": "x"}, headers=ha).status_code == 403
    assert client.delete(url, headers=ha).status_code == 403
    assert client.get(url + "/rounds", headers=ha).status_code == 403
    assert client.post(url + "/rounds", json={"round_name": "x"}, headers=ha).status_code == 403
    assert client.put(f"{url}/rounds/{rnd['id']}", json={"status": "FAILED"}, headers=ha).status_code == 403
    assert client.delete(f"{url}/rounds/{rnd['id']}", headers=ha).status_code == 403
    assert client.get(f"/applications/{uuid.uuid4()}", headers=ha).status_code == 404
    assert client.get("/applications", headers=ha).json() == []  # only the admin's own
    assert client.get(url, headers=user["headers"]).json() == a  # unchanged


def test_role_is_read_from_db_not_from_stale_token(client, admin):
    # the token still carries role=ADMIN, but after demotion in the DB the server must refuse writes
    _set_db_role(admin["email"], "USER")
    r = client.post("/companies", json={"name": PREFIX + "stale", "role": "r"}, headers=admin["headers"])
    assert r.status_code == 403


def test_bootstrap_promotes_existing_user_only(client, user):
    assert _db_role(user["email"]) == "USER"
    db = SessionLocal()
    try:
        assert bootstrap_admin.promote(db, PREFIX + "missing@example.com") is False
        assert bootstrap_admin.promote(db, user["email"]) is True
    finally:
        db.close()
    assert _db_role(user["email"]) == "ADMIN"
    # a fresh login now carries the ADMIN claim and /users/me reports it
    r = client.post("/auth/login", json={"email": user["email"], "password": user["password"]})
    h = {"Authorization": "Bearer " + r.json()["access_token"]}
    assert client.get("/users/me", headers=h).json()["role"] == "ADMIN"


def test_bootstrap_command_line(client, user):
    import os
    import subprocess
    import sys
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    base = [sys.executable, "-m", "app.scripts.bootstrap_admin"]
    ok = subprocess.run(base + [user["email"]], cwd=root, env=dict(os.environ), capture_output=True, text=True)
    assert ok.returncode == 0, ok.stderr[-300:]
    assert _db_role(user["email"]) == "ADMIN"
    missing = subprocess.run(base + [PREFIX + "no@example.com"], cwd=root, env=dict(os.environ),
                             capture_output=True, text=True)
    assert missing.returncode == 1


def test_no_public_endpoint_can_promote(client, user):
    h = user["headers"]
    for method, path_ in [("post", "/admin/bootstrap"), ("post", "/auth/promote"), ("put", "/users/me")]:
        r = getattr(client, method)(path_, json={"role": "ADMIN"}, headers=h)
        assert r.status_code in (404, 405)
    assert _db_role(user["email"]) == "USER"
