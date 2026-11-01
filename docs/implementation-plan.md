# Placement Tracker — Implementation Plan

> **Repo:** https://github.com/Rashipotey/placement_tracker  
> **Jira project:** `codemie-placement-tracker`  
> **Target file:** `docs/implementation-plan.md`  
> **Base branch:** `main` (verified default branch)  
> **Scope:** Planning/documentation only — no application source code or Jira issue changes.

## 1. Project Overview

Placement Tracker is a minimal full‑stack application for tracking job applications. The repository currently contains a FastAPI backend with authentication and SQLAlchemy models, but it does not yet expose domain CRUD APIs (companies/applications/rounds), does not contain a frontend, and has no automated tests.

This plan sequences implementation work based on the verified Jira backlog in project `codemie-placement-tracker` (issues `CPT-*`) and the verified current codebase on `main`.

## 2. Repository and Technology Stack (Verified)

### Backend
- **Framework:** FastAPI (`fastapi`, `uvicorn`)
- **ORM:** SQLAlchemy
- **DB driver:** `psycopg2-binary` (PostgreSQL)
- **Auth:** JWT (`python-jose`), password hashing via `passlib[bcrypt]`
- **Multipart:** `python-multipart`

### Repository structure (`main`)
Top-level:
- `app/` — FastAPI backend
- `requirements.txt`
- `README.md` (empty)
- `.gitignore`
- `docs/` (contains this plan)

Backend sub-structure (verified):
- `app/main.py` (creates schema via `Base.metadata.create_all` and includes auth/users routers)
- `app/auth/` (router, jwt handler, security)
- `app/users/` (router)
- `app/models/` (`User`, `Company`, `Application`, `Round`)
- `app/schemas/` (`auth.py`, `user.py`, plus **empty** `company.py`, `application.py`)
- `app/database/` (connection/session)

### Frontend
- **Not present** in repository.

### Tests / CI
- **Not present** in repository.

## 3. Current Implementation Status (Verified)

### Implemented (backend)
- FastAPI app wiring in `app/main.py`
- Auth endpoints:
  - `POST /auth/register`
  - `POST /auth/login`
- Protected user endpoint:
  - `GET /users/me`
- SQLAlchemy models exist:
  - `User`, `Company`, `Application`, `Round`

### Partially implemented
- `app/schemas/company.py` and `app/schemas/application.py` exist but are empty.
- Database tables created at runtime via `Base.metadata.create_all(bind=engine)` in `app/main.py`.

### Not implemented
- No CRUD APIs for companies/applications/rounds.
- No frontend.
- No tests.
- No migrations.

## 4. Jira Backlog Analysis (Verified)

Jira search used: `project = "codemie-placement-tracker" ORDER BY created ASC`.

### 4.1 Epics
- **CPT-1** — Backend API: Companies, Applications, Rounds (MVP)
- **CPT-2** — Frontend UI (MVP)
- **CPT-3** — Auth & Configuration Hardening
- **CPT-4** — Testing & Quality Gates (MVP)
- **CPT-25** — Backend DX: Local run, migrations, and environment setup
- **CPT-30** — Security & repo hygiene (MVP)

### 4.2 Stories / Subtasks
**Backend (CPT-1)**
- **CPT-5** — Create/Read/Update/Delete Companies via API
  - **CPT-12** — Implement Pydantic schemas for Company (create/update/read)
  - **CPT-13** — Implement Companies router (CRUD endpoints)
- **CPT-6** — Create/Read/Update/Delete Applications (scoped to current user)
  - **CPT-14** — Implement Pydantic schemas for Application (create/update/read)
  - **CPT-15** — Implement Applications router (CRUD, per-user authorization)
- **CPT-7** — Manage interview rounds for an application
  - **CPT-16** — Implement Rounds schemas + router under applications

**Frontend (CPT-2)**
- **CPT-8** — Frontend: Register/Login and store JWT token
  - **CPT-17** — Frontend scaffold + routing (auth guarded)
  - **CPT-18** — Frontend auth pages + token storage + logout
- **CPT-9** — Frontend: Applications list + create/edit application
  - **CPT-19** — Frontend applications list (fetch + render)
  - **CPT-20** — Frontend application form (create/edit)

**Config/Hardening (CPT-3)**
- **CPT-10** — Externalize JWT and DB configuration (remove hardcoded secret)
  - **CPT-21** — Move JWT secret/algorithm/expiry to env-driven settings
  - **CPT-22** — Fix dependency/config mismatch (pydantic-settings vs python-settings)
  - **CPT-23** — Add .env.example + README runbook (local setup)

**Testing (CPT-4)**
- **CPT-11** — Add minimal test suite for core API flows
  - **CPT-24** — Create pytest harness and test DB strategy

**DX / Platform**
- **CPT-26** — Add CORS configuration for frontend→backend API calls
- **CPT-27** — Introduce DB migrations (Alembic) and remove runtime create_all in production path
- **CPT-28** — Add docker-compose for local Postgres and API runbook
- **CPT-29** — Publish minimal API docs and ensure OpenAPI reflects Companies/Applications/Rounds endpoints

**Security / Repo hygiene**
- **CPT-31** — Remove committed __pycache__ and add ignore rules
- **CPT-32** — Add basic CI workflow to run backend tests

### 4.3 Jira links
- https://poteyrashi.atlassian.net/browse/CPT-1
- https://poteyrashi.atlassian.net/browse/CPT-2
- https://poteyrashi.atlassian.net/browse/CPT-3
- https://poteyrashi.atlassian.net/browse/CPT-4

## 5. Identified Gaps and Blockers (Verified)

### 5.1 Feature gaps
- Domain CRUD endpoints missing for companies/applications/rounds (CPT-1).
- Frontend missing entirely (CPT-2).
- Tests and CI missing (CPT-4, CPT-32).

### 5.2 Technical inconsistencies / risks
- **Hardcoded JWT secret:** `SECRET_KEY = "change_this"` in `app/auth/jwt_handler.py` (CPT-21).
- **Dependency mismatch:** `app/database/connection.py` imports `pydantic_settings.BaseSettings` but `requirements.txt` lists `python-settings` (CPT-22).
- **No migrations:** runtime schema creation via `create_all()` risks drift (CPT-27).
- **Repo hygiene:** `__pycache__` tracked in git (CPT-31).

### 5.3 Requirements ambiguities (call out explicitly)
- Company scoping: global vs user-specific (not fully specified in retrieved Jira fields; treat as a decision point during CPT-5/CPT-13).
- Application status enum values for UI/filtering not specified.
- Rounds UI is not explicitly included in frontend stories.

## 6. Proposed Implementation Phases

1. **Phase 1 — Backend domain APIs (CPT-1)**
2. **Phase 2 — Auth/config hardening (CPT-3)**
3. **Phase 3 — Frontend MVP (CPT-2)**
4. **Phase 4 — Web integration essentials & DX (CORS, docs, compose, repo hygiene)**
5. **Phase 5 — Testing & CI (CPT-4)**
6. **Phase 6 — Migrations / production safety (CPT-25)**

Rationale: backend APIs unblock frontend; hardening should happen before broad usage; tests/CI stabilize changes; migrations reduce drift risk.

## 7. Task-by-Task Implementation Plan (Traceable to Jira)

> Jira statuses in this plan are from the Jira search response (all were **To Do** at retrieval time).

### Phase 1 — Backend domain APIs (Epic: CPT-1)

#### CPT-12 — Implement Pydantic schemas for Company (create/update/read)
- **Status:** To Do
- **Existing functionality / gap:** `app/schemas/company.py` is empty.
- **Proposed implementation:** Add `CompanyCreate`, `CompanyUpdate`, `CompanyRead` schemas aligned to `Company` model.
- **Dependencies:** —
- **Expected outcome:** Validated request/response payloads for companies.
- **Validation:** Import schemas; create a company via API (once router exists) and confirm response model works.

#### CPT-13 — Implement Companies router (CRUD endpoints)
- **Status:** To Do
- **Existing functionality / gap:** No companies router wired into `app/main.py`.
- **Proposed implementation:** Add CRUD endpoints. Decide company scope (global vs user-specific) and implement accordingly.
- **Dependencies:** CPT-12
- **Expected outcome:** `/companies` CRUD endpoints exist.
- **Validation:** Manual API smoke tests; check OpenAPI lists the endpoints.

#### CPT-14 — Implement Pydantic schemas for Application (create/update/read)
- **Status:** To Do
- **Existing functionality / gap:** `app/schemas/application.py` is empty.
- **Proposed implementation:** Add `ApplicationCreate/Update/Read` with `company_id` and status fields.
- **Dependencies:** —
- **Expected outcome:** Validated application payloads.
- **Validation:** Import schemas; serialize model instances.

#### CPT-15 — Implement Applications router (CRUD, per-user authorization)
- **Status:** To Do
- **Existing functionality / gap:** No applications router; no per-user domain scoping.
- **Proposed implementation:** CRUD endpoints scoped by `current_user.id`; enforce ownership checks; require existing company.
- **Dependencies:** CPT-14; recommended CPT-13
- **Expected outcome:** Each user sees only their applications.
- **Validation:** Create two users; ensure cross-user reads/updates fail.

#### CPT-16 — Implement Rounds schemas + router under applications
- **Status:** To Do
- **Existing functionality / gap:** No rounds router.
- **Proposed implementation:** Nested routes under an application; enforce parent ownership.
- **Dependencies:** CPT-15
- **Expected outcome:** `/applications/{id}/rounds` CRUD endpoints exist with authorization.
- **Validation:** Confirm user B cannot access rounds under user A’s application.

### Phase 2 — Auth & Configuration Hardening (Epic: CPT-3)

#### CPT-21 — Move JWT secret/algorithm/expiry to env-driven settings
- **Status:** To Do
- **Existing functionality / gap:** Hardcoded values in `jwt_handler.py`.
- **Proposed implementation:** Read JWT settings from environment (single source of truth).
- **Dependencies:** —
- **Expected outcome:** No secrets committed; configurable per environment.
- **Validation:** App boot + login works with env vars.

#### CPT-22 — Fix dependency/config mismatch (pydantic-settings vs python-settings)
- **Status:** To Do
- **Existing functionality / gap:** `pydantic_settings` import missing from requirements.
- **Proposed implementation:** Align dependencies and imports.
- **Dependencies:** —
- **Expected outcome:** `pip install -r requirements.txt` produces runnable app.
- **Validation:** Fresh venv install + `uvicorn app.main:app` starts.

#### CPT-23 — Add .env.example + README runbook (local setup)
- **Status:** To Do
- **Existing functionality / gap:** README empty; no `.env.example`.
- **Proposed implementation:** Document required env vars and local run steps.
- **Dependencies:** CPT-21, CPT-22 (recommended)
- **Expected outcome:** New dev can run backend.
- **Validation:** Follow README in clean environment.

### Phase 3 — Frontend MVP (Epic: CPT-2)

#### CPT-17 — Frontend scaffold + routing (auth guarded)
- **Status:** To Do
- **Existing functionality / gap:** No frontend code.
- **Proposed implementation:** Add minimal SPA scaffold and guarded routes.
- **Dependencies:** Backend auth stable; recommended after CPT-21.
- **Expected outcome:** Frontend runs locally.
- **Validation:** Protected route redirects when unauthenticated.

#### CPT-18 — Frontend auth pages + token storage + logout
- **Status:** To Do
- **Existing functionality / gap:** No auth UI.
- **Proposed implementation:** Register/login forms; store token; attach bearer token.
- **Dependencies:** CPT-17
- **Expected outcome:** User can login and call protected endpoint.
- **Validation:** `/users/me` succeeds from frontend after login.

#### CPT-19 — Frontend applications list (fetch + render)
- **Status:** To Do
- **Existing functionality / gap:** No applications UI.
- **Proposed implementation:** List user applications with basic filters.
- **Dependencies:** CPT-18, CPT-15
- **Expected outcome:** Applications render in UI.
- **Validation:** Create app via API; see it in UI.

#### CPT-20 — Frontend application form (create/edit)
- **Status:** To Do
- **Existing functionality / gap:** No create/edit UI.
- **Proposed implementation:** Create/edit form; requires companies list.
- **Dependencies:** CPT-19, CPT-13
- **Expected outcome:** User can create/edit applications end-to-end.
- **Validation:** Changes persist and appear in list.

### Phase 4 — Web integration essentials & DX

#### CPT-26 — Add CORS configuration for frontend→backend API calls
- **Status:** To Do
- **Existing functionality / gap:** No CORS middleware.
- **Proposed implementation:** Configure allowed origins.
- **Dependencies:** Before browser integration testing.
- **Expected outcome:** Browser calls succeed.
- **Validation:** Confirm no CORS errors in browser console.

#### CPT-29 — Publish minimal API docs and ensure OpenAPI reflects Companies/Applications/Rounds endpoints
- **Status:** To Do
- **Existing functionality / gap:** OpenAPI reflects only current routers.
- **Proposed implementation:** Ensure routers use response models and are included.
- **Dependencies:** CPT-13, CPT-15, CPT-16
- **Expected outcome:** `/docs` lists domain endpoints and auth.
- **Validation:** Verify `/docs` has companies/applications/rounds.

#### CPT-28 — Add docker-compose for local Postgres and API runbook
- **Status:** To Do
- **Existing functionality / gap:** No compose.
- **Proposed implementation:** Provide Postgres + API setup.
- **Dependencies:** CPT-23 recommended.
- **Expected outcome:** One-command local environment.
- **Validation:** `docker compose up` starts services.

#### CPT-31 — Remove committed __pycache__ and add ignore rules
- **Status:** To Do
- **Existing functionality / gap:** `__pycache__` tracked.
- **Proposed implementation:** Remove caches; add ignore patterns.
- **Dependencies:** —
- **Expected outcome:** Cleaner repo.
- **Validation:** New caches not tracked.

### Phase 5 — Testing & CI (Epic: CPT-4)

#### CPT-24 — Create pytest harness and test DB strategy
- **Status:** To Do
- **Existing functionality / gap:** No tests.
- **Proposed implementation:** Pytest + TestClient + isolated DB strategy.
- **Dependencies:** —
- **Expected outcome:** Tests run locally.
- **Validation:** `pytest` runs.

#### CPT-11 — Add minimal test suite for core API flows
- **Status:** To Do
- **Existing functionality / gap:** No automated coverage.
- **Proposed implementation:** Auth tests + per-user authorization tests.
- **Dependencies:** CPT-24, CPT-15
- **Expected outcome:** Core flows guarded.
- **Validation:** All tests pass.

#### CPT-32 — Add basic CI workflow to run backend tests
- **Status:** To Do
- **Existing functionality / gap:** No CI.
- **Proposed implementation:** GitHub Actions workflow running pytest.
- **Dependencies:** CPT-24
- **Expected outcome:** PR checks run automatically.
- **Validation:** CI green on PR.

### Phase 6 — Migrations / production safety (Epic: CPT-25)

#### CPT-27 — Introduce DB migrations (Alembic) and remove runtime create_all in production path
- **Status:** To Do
- **Existing functionality / gap:** Runtime `create_all()` in `app/main.py`.
- **Proposed implementation:** Alembic migration workflow; remove/guard create_all.
- **Dependencies:** After core models/APIs stabilize.
- **Expected outcome:** Predictable schema evolution.
- **Validation:** Migration upgrade works; app boots without create_all in prod.

## 8. Dependencies and Execution Order

1) CPT-12 → CPT-13
2) CPT-14 → CPT-15
3) CPT-16
4) CPT-21 + CPT-22 → CPT-23
5) CPT-26
6) CPT-17 → CPT-18 → CPT-19 → CPT-20
7) CPT-24 → CPT-11 → CPT-32
8) CPT-29
9) CPT-31 (any time)
10) CPT-28
11) CPT-27

## 9. Testing and Validation Strategy

### Backend
- Manual smoke tests (curl/Postman): register/login, `/users/me`, company/app/round flows.
- Automated tests: auth, CRUD, per-user authorization, negative cases.

### Frontend
- Manual validation: auth guard, token persistence, CRUD flows.

## 10. Risks and Mitigations

- Hardcoded secrets → CPT-21.
- Dependency mismatch → CPT-22.
- Runtime schema creation → CPT-27.
- Missing CORS → CPT-26.
- No tests/CI → CPT-24/CPT-11/CPT-32.

## 11. Completion Criteria

MVP is complete when:
- CPT-1 backend APIs are delivered (companies/applications/rounds) with correct authorization.
- CPT-2 frontend provides auth + applications list/form.
- CPT-3 config is env-driven and installs cleanly.
- CPT-4 tests exist and CI runs.
- DX items (CPT-23, optionally CPT-28) allow reviewers to run locally.

---

**Jira issues covered:** CPT-1..4, CPT-5..24, CPT-25..32 (as retrieved from Jira search).
