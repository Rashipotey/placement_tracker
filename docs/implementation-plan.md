# Placement Tracker — Implementation Plan

> **Repo:** https://github.com/Rashipotey/placement_tracker  
> **Jira project:** `codemie-placement-tracker`  
> **Target file:** `docs/implementation-plan.md`  
> **Working branch:** `docs/add-implementation-plan`  
> **Base branch:** `main` (verified default branch)  
> **Scope:** Planning/documentation only — no application code or Jira changes.

## 1. Project Overview

Placement Tracker is a minimal full‑stack application for tracking job applications. The current repository contains a FastAPI backend with authentication and SQLAlchemy models, but it does not yet expose domain CRUD APIs (companies/applications/rounds), does not contain a frontend, and has no automated tests.

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

Backend sub-structure (verified):
- `app/main.py`
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

### 4.2 Stories and Subtasks
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

### 4.3 Jira links
(Replace `<KEY>` with the issue key)
- https://poteyrashi.atlassian.net/browse/CPT-1
- https://poteyrashi.atlassian.net/browse/CPT-2
- https://poteyrashi.atlassian.net/browse/CPT-3
- https://poteyrashi.atlassian.net/browse/CPT-4

## 5. Identified Gaps and Blockers (Verified)

### 5.1 Product/feature gaps
- No domain CRUD endpoints for companies/applications/rounds (CPT-1).
- No frontend application at all (CPT-2).
- No test harness or test suite (CPT-4).

### 5.2 Technical inconsistencies / risks
- **Hardcoded JWT secret:** `SECRET_KEY = "change_this"` in `app/auth/jwt_handler.py` (addressed by CPT-21).
- **Dependency mismatch risk:** code imports `pydantic_settings.BaseSettings` but `requirements.txt` lists `python-settings` (addressed by CPT-22).
- **Runtime schema creation:** `Base.metadata.create_all()` used instead of migrations (not covered by Jira; note as risk).

### 5.3 Requirements ambiguities (need confirmation in implementation)
- Company scoping: global vs user-specific (mentioned as a decision point in CPT-5 context).
- Application status enum values for UI/filtering (not explicitly specified in issue list fields retrieved).
- Whether rounds require a frontend UI (backend story exists; frontend stories do not mention rounds).

## 6. Proposed Implementation Phases

1. **Phase A — Backend domain APIs (CPT-1)**
   - Implement schemas and routers for Companies → Applications → Rounds.
2. **Phase B — Auth/config hardening (CPT-3)**
   - Remove hardcoded secrets, align dependencies, add env/runbook.
3. **Phase C — Frontend MVP (CPT-2)**
   - Scaffold UI, implement auth flow, applications list + form.
4. **Phase D — Testing & validation (CPT-4)**
   - Add pytest harness and core API tests.

Rationale: backend APIs unblock frontend; config hardening should land before broader use; tests stabilize behavior.

## 7. Task-by-Task Implementation Plan (Traceable to Jira)

For each item below: **Current status** is the Jira status returned by the search (all were `To Do` at retrieval time).

### CPT-12 — Implement Pydantic schemas for Company (create/update/read)
- **Status:** To Do
- **Existing functionality / gap:** `app/schemas/company.py` exists but is empty.
- **Proposed implementation:** Define `CompanyCreate`, `CompanyUpdate`, `CompanyRead` schemas aligned to `Company` SQLAlchemy model.
- **Dependencies:** None
- **Expected outcome:** API layer can validate Company payloads.
- **Validation:** Unit-level import check; API endpoints can serialize Company objects.

### CPT-13 — Implement Companies router (CRUD endpoints)
- **Status:** To Do
- **Existing functionality / gap:** No companies router exists.
- **Proposed implementation:** Add FastAPI router with CRUD endpoints; decide company ownership rules (global vs user-scoped) consistent with CPT-5 decisions.
- **Dependencies:** CPT-12
- **Expected outcome:** Companies can be created/updated/listed/deleted via API.
- **Validation:** Manual API smoke tests; verify 404 on missing id; verify 422 on invalid payload.

### CPT-14 — Implement Pydantic schemas for Application (create/update/read)
- **Status:** To Do
- **Existing functionality / gap:** `app/schemas/application.py` exists but is empty.
- **Proposed implementation:** Define schemas aligned to `Application` model, including relationship keys (company_id) and status fields (enum if defined).
- **Dependencies:** None
- **Expected outcome:** Validated request/response shapes for applications.
- **Validation:** Import + serialization check.

### CPT-15 — Implement Applications router (CRUD, per-user authorization)
- **Status:** To Do
- **Existing functionality / gap:** No applications router exists; no per-user scoping beyond `/users/me`.
- **Proposed implementation:** CRUD endpoints that always scope queries by `current_user.id`; enforce ownership checks for read/update/delete.
- **Dependencies:** CPT-14; (recommended) CPT-13 if applications require company existence.
- **Expected outcome:** Users can only see and mutate their own applications.
- **Validation:** Create two users and confirm cross-user access returns 403/404 as designed.

### CPT-16 — Implement Rounds schemas + router under applications
- **Status:** To Do
- **Existing functionality / gap:** No rounds API exists.
- **Proposed implementation:** Nested routes under applications (e.g., `/applications/{id}/rounds`), validating parent application ownership.
- **Dependencies:** CPT-15
- **Expected outcome:** Rounds CRUD tied to applications with authorization.
- **Validation:** Ensure rounds cannot be accessed if parent application is not owned.

### CPT-21 — Move JWT secret/algorithm/expiry to env-driven settings
- **Status:** To Do
- **Existing functionality / gap:** Hardcoded secret/algorithm/expiry in `jwt_handler.py`.
- **Proposed implementation:** Centralize config in settings loaded from env; use secure defaults only for local dev.
- **Dependencies:** None
- **Expected outcome:** No hardcoded secrets in repo; runtime configured via env.
- **Validation:** App boots with env vars; token creation/verification works.

### CPT-22 — Fix dependency/config mismatch (pydantic-settings vs python-settings)
- **Status:** To Do
- **Existing functionality / gap:** `requirements.txt` does not reflect imports (`pydantic_settings`).
- **Proposed implementation:** Align dependency list with actual imports and FastAPI/Pydantic versions.
- **Dependencies:** None
- **Expected outcome:** Clean install works from `requirements.txt`.
- **Validation:** Fresh venv install + import/run.

### CPT-23 — Add .env.example + README runbook (local setup)
- **Status:** To Do
- **Existing functionality / gap:** `README.md` empty; no `.env.example`.
- **Proposed implementation:** Document required env vars (DATABASE_URL, JWT settings), local run steps.
- **Dependencies:** CPT-21, CPT-22 (recommended so docs match reality)
- **Expected outcome:** A reviewer can run backend locally.
- **Validation:** Follow README from scratch on a clean machine.

### CPT-17 — Frontend scaffold + routing (auth guarded)
- **Status:** To Do
- **Existing functionality / gap:** No frontend exists.
- **Proposed implementation:** Create minimal SPA scaffold with routes; implement auth guard for protected pages.
- **Dependencies:** Backend auth endpoints existing (already implemented) + stable config (recommended after CPT-21).
- **Expected outcome:** Frontend app runs and can navigate between login and protected routes.
- **Validation:** Manual: unauthenticated users are redirected to login.

### CPT-18 — Frontend auth pages + token storage + logout
- **Status:** To Do
- **Existing functionality / gap:** No auth UI.
- **Proposed implementation:** Login/register screens that call backend; store JWT (localStorage for MVP) and attach Authorization header.
- **Dependencies:** CPT-17
- **Expected outcome:** User can register/login/logout from UI.
- **Validation:** `GET /users/me` works from UI after login.

### CPT-19 — Frontend applications list (fetch + render)
- **Status:** To Do
- **Existing functionality / gap:** No applications UI.
- **Proposed implementation:** Fetch applications for current user and render list view.
- **Dependencies:** CPT-18, CPT-15
- **Expected outcome:** Applications appear in UI after creation.
- **Validation:** Create application in backend and verify it appears for the user.

### CPT-20 — Frontend application form (create/edit)
- **Status:** To Do
- **Existing functionality / gap:** No form UI.
- **Proposed implementation:** Form for create/edit; include company selection (requires companies API).
- **Dependencies:** CPT-19, CPT-13
- **Expected outcome:** User can create and edit applications via UI.
- **Validation:** Confirm persisted changes reflected in list and backend.

### CPT-24 — Create pytest harness and test DB strategy
- **Status:** To Do
- **Existing functionality / gap:** No tests.
- **Proposed implementation:** Add pytest dependencies/config; choose test DB approach.
- **Dependencies:** None
- **Expected outcome:** Tests can run locally/CI.
- **Validation:** `pytest` runs and connects to test DB.

### CPT-11 — Add minimal test suite for core API flows
- **Status:** To Do
- **Existing functionality / gap:** No automated coverage.
- **Proposed implementation:** Tests for register/login, `/users/me`, application CRUD + authorization.
- **Dependencies:** CPT-24, CPT-15
- **Expected outcome:** Core flows protected from regression.
- **Validation:** CI/local pytest green; include negative tests for cross-user access.

## 8. Dependencies and Execution Order

**Recommended execution order** (explicit dependencies):
1. CPT-12 → CPT-13 (companies schemas then router)
2. CPT-14 → CPT-15 (applications schemas then router)
3. CPT-16 (rounds depends on applications)
4. CPT-21 + CPT-22 → CPT-23 (config/deps before docs)
5. CPT-17 → CPT-18 → CPT-19 → CPT-20 (frontend scaffold → auth → list → form)
6. CPT-24 → CPT-11 (test harness before test suite)

**Cross-cutting dependency notes**
- Frontend application features (CPT-19/20) require backend apps/companies APIs (CPT-15/13).
- If applications require company existence, complete companies before applications (recommended).

## 9. Testing and Validation Strategy

### Backend
- Manual smoke test with curl/Postman:
  - register/login, then call `/users/me`
  - create company → create application → create round
- Automated tests (CPT-24, CPT-11):
  - auth flow
  - per-user authorization checks
  - CRUD happy paths and invalid payloads

### Frontend
- Manual validation:
  - protected route redirects
  - token persists and is used on API calls
  - list view updates after create/edit

## 10. Risks and Mitigations

- **Hardcoded secrets** (current): mitigate via CPT-21.
- **Dependency mismatch breaks installs:** mitigate via CPT-22.
- **No migrations:** risk of schema drift; mitigate later by adding migrations tooling (not currently in Jira scope).
- **Frontend framework choice not specified:** keep minimal; document decision in CPT-17 implementation.

## 11. Completion Criteria

MVP can be considered complete when:
- Backend exposes companies/applications/rounds CRUD with correct authorization (CPT-1 stories/subtasks complete).
- Frontend provides register/login and application tracking UI (CPT-2 stories/subtasks complete).
- JWT/config is environment-driven and dependencies install cleanly (CPT-3 complete).
- Tests exist for core backend flows and pass (CPT-4 complete).

---

**Generated from verified Jira issue list (CPT-1..CPT-24) and verified repository state on `main`.**
