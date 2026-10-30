# Low-Level Design (LLD) — Placement Tracker Enhancements

> **Scope:** Detailed design of modules, endpoint behavior, validation, and data access for Company + Application CRUD and status tracking.
>
> This is a design-only deliverable; no code changes are performed as part of this document.

---

## 1. Module layout (proposed, consistent with repo)

Existing modules:
- `app/auth/*` (router, dependencies, jwt handler)
- `app/users/router.py`
- `app/models/*`
- `app/schemas/*` (company/application currently empty)

Proposed additions (minimal):
- `app/companies/router.py`
- `app/applications/router.py`
- Implement Pydantic models in:
  - `app/schemas/company.py`
  - `app/schemas/application.py`

Optional (thin services, only if needed for cleanliness):
- `app/companies/service.py`
- `app/applications/service.py`

---

## 2. Data contracts (Pydantic schemas)

### 2.1 Company schemas

**CompanyCreate**
- `name: str` (required, non-empty)
- `role: str` (required, non-empty)
- `location: str | None`
- `package_lpa: float | None` (>= 0)
- `application_link: str | None` (optional; may validate URL format)

**CompanyOut**
- `id: UUID`
- all fields from CompanyCreate

### 2.2 Application status type

**ApplicationStatus (Enum)**
- `APPLIED`
- `INTERVIEW`
- `OFFER`
- `REJECTED`

Implementation detail:
- Use `enum.Enum` so invalid statuses trigger 422 validation.

### 2.3 Application schemas

**ApplicationCreate**
- `company_id: UUID` (required)
- `status: ApplicationStatus | None` (default handled server-side or schema default)
- `notes: str | None`

**ApplicationUpdate**
- `company_id: UUID | None`
- `status: ApplicationStatus | None`
- `notes: str | None`

**ApplicationOut**
- `id: UUID`
- `user_id: UUID`
- `company_id: UUID`
- `status: ApplicationStatus`
- `notes: str | None`

> Note: If the API should return company name/role in application responses, define an extended schema like `ApplicationOutWithCompany` and join in queries. Keep MVP minimal unless UI needs it.

---

## 3. Router details

### 3.1 Companies router (new)

**File:** `app/companies/router.py`

Endpoints:

1) `POST /companies`
- Auth: required (`get_current_user`)
- Request: `CompanyCreate`
- Behavior:
  - Validate required fields (Pydantic)
  - Insert into `companies`
  - Return `CompanyOut`
- Responses:
  - `201 Created`
  - `422` validation

2) `GET /companies`
- Auth: required
- Behavior:
  - Query all companies ordered by name (optional)
  - Return list of `CompanyOut`

### 3.2 Applications router (new)

**File:** `app/applications/router.py`

Ownership rule:
- For any operation on `/applications/{id}`: fetch by id; if not found → 404; if found but `user_id != current_user.id` → 403.

Endpoints:

1) `POST /applications`
- Auth: required
- Request: `ApplicationCreate`
- Behavior:
  - Check `Company` exists for `company_id`.
    - If missing → `404` or `400` (choose one; recommend 404)
  - Create `Application(user_id=current_user.id, ...)`
  - Default `status=APPLIED` if not provided
  - Return `ApplicationOut`

2) `GET /applications`
- Auth: required
- Behavior:
  - `SELECT * FROM applications WHERE user_id = current_user.id`
  - Return list of `ApplicationOut`

3) `GET /applications/{id}`
- Auth: required
- Behavior:
  - Load application by id
  - Enforce ownership
  - Return `ApplicationOut`

4) `PATCH /applications/{id}`
- Auth: required
- Request: `ApplicationUpdate`
- Behavior:
  - Load and ownership check
  - If `company_id` provided: validate company exists
  - Apply updates (status/notes/company_id)
  - Return updated `ApplicationOut`

5) `DELETE /applications/{id}`
- Auth: required
- Behavior:
  - Load and ownership check
  - Delete
  - Return `204 No Content`

---

## 4. Database access patterns

### 4.1 Session management

Use existing `SessionLocal` dependency pattern:
- `db = SessionLocal()` per request
- `try/finally: db.close()`

### 4.2 Queries

- Company existence check:
  - `db.query(Company).filter(Company.id == company_id).first()`
- List applications:
  - `db.query(Application).filter(Application.user_id == current_user.id).all()`

### 4.3 Transaction handling

- For create/update/delete:
  - `db.add(obj)`
  - `db.commit()`
  - `db.refresh(obj)`

Rollback strategy:
- On exceptions, `db.rollback()` then raise HTTPException(500) (or allow FastAPI default error handler).

---

## 5. Error handling (detailed)

### 5.1 Auth errors
- Missing token → 401
- Invalid/expired token → 401

### 5.2 Authorization errors
- Application exists but owned by other user → 403

### 5.3 Not-found errors
- Application id does not exist → 404
- Company id does not exist when creating/updating application → 404 (recommended)

### 5.4 Validation errors
- Invalid status string → 422 (Enum validation)
- Invalid UUID format → 422

---

## 6. Edge cases

- Deleting an application twice:
  - First delete returns 204
  - Second delete returns 404
- Updating with empty payload:
  - PATCH with no fields should return 200 with unchanged object (or 422 if schema enforces at least one field; MVP: allow empty).
- Notes length:
  - Optionally cap via schema (e.g., 2000 chars) to avoid unbounded payloads.

---

## 7. Testing considerations

### 7.1 Unit tests (if introduced)

- Schema validation tests:
  - Invalid statuses rejected
  - Required fields present

- Authorization tests:
  - user A cannot access user B application

### 7.2 Integration tests (recommended minimal)

Using `TestClient` and a test database:

- Register/login flow
- Create company
- Create application
- List applications (must be user-scoped)
- Update application
- Delete application

If no automated tests are added, document repeatable manual curl commands in README or a `docs/test-plan.md` (optional).

---

## 8. Security notes (LLD)

- Do not trust client-supplied `user_id`.
- Ensure JWT secret is not hardcoded for deployed environments.
- Add CORS allowlist for the frontend origin(s).

