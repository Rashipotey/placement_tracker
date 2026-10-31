# Placement Tracker — Implementation Plan

> **Repo:** https://github.com/Rashipotey/placement_tracker  
> **Jira project:** `codemie-placement-tracker`  
> **Plan scope:** Planning/documentation only (no code changes performed in this work item).

## 1. Overview & Planning Scope

This document defines a minimal, full‑stack implementation sequence for the Placement Tracker project based on **verified** Jira and repository state.

### Sources of truth
- **Requirements:** Jira project `codemie-placement-tracker`
- **Implementation baseline:** Current GitHub repository state on default branch `main`

### Verified limitation (requirements)
At the time of planning, Jira search returned **0 issues** in `codemie-placement-tracker` via the Jira API integration. Therefore:
- There are **no Epic/Story/Task issue keys** available to map planned work.
- This plan remains **structural and technical**, and must be updated to reference real Jira issue keys once the backlog exists.

## 2. Current Implementation Status (Verified)

### 2.1 Repository structure
Top-level (verified via GitHub Contents API):
- `app/` (FastAPI backend)
- `requirements.txt`
- `README.md` (empty)
- No `docs/` directory currently

### 2.2 Backend/API (FastAPI)
Implemented endpoints (verified by reading `app/main.py` and router modules):
- `GET /` — health/root message
- `POST /auth/register` — user registration
- `POST /auth/login` — login, returns access token
- `GET /users/me` — current user profile (JWT protected)

Not implemented:
- No API endpoints for placement tracking domain: **companies**, **applications**, **rounds**

### 2.3 Database
- SQLAlchemy models exist for:
  - `User`
  - `Company`
  - `Application`
  - `Round`
- Tables are created at runtime in `app/main.py` via `Base.metadata.create_all(bind=engine)`
- Config is loaded via `.env` (`DATABASE_URL`, others)

### 2.4 Schemas / validation
- Auth/user schemas exist.
- `app/schemas/company.py` and `app/schemas/application.py` exist but are **empty**.

### 2.5 Frontend
- No frontend present in repository.

### 2.6 Tests / CI
- No tests and no CI workflow present.

## 3. Repository Gaps & Technical Inconsistencies (Verified)

### 3.1 Security/config
- `app/auth/jwt_handler.py` uses hardcoded:
  - `SECRET_KEY = "change_this"`
  - `ALGORITHM = "HS256"`

### 3.2 Dependency concerns
- `requirements.txt` includes `python-settings` while the code uses `pydantic_settings.BaseSettings`.
  - This suggests either an incorrect dependency name or incomplete migration.

### 3.3 Domain model is unused
- Models exist for Company/Application/Round, but there are no routers/services/schemas to expose them.

### 3.4 No migrations
- Runtime schema creation is convenient for prototypes but risky for real environments.

### 3.5 Repo hygiene
- `__pycache__` directories are committed (present in Git tree). This is generally undesirable.

## 4. Planning Assumptions (Explicit)

Because Jira contains no issues, the plan assumes a minimal Placement Tracker MVP consistent with existing domain models:
- Users authenticate.
- Users track job **applications** associated with **companies**.
- (Optional) Each application can have **rounds**.

If these assumptions differ from intended product scope, update this plan after Jira backlog is populated.

## 5. Implementation Phases (Logical Order)

### Phase 0 — Requirements Baseline (Jira)
**Goal:** Ensure requirements exist and are traceable.

- **P0.1** Create Epics/Stories/Tasks in Jira for backend, frontend, testing, and configuration.
- **P0.2** Add acceptance criteria and definition of done.
- **P0.3** Link dependencies (e.g., backend API before frontend UI).

> **Traceability note:** Cannot map to actual Jira issue keys because Jira currently returns 0 issues.

### Phase 1 — Backend Domain API (Companies/Applications/Rounds)
**Goal:** Turn existing SQLAlchemy domain models into a usable API.

1. **Schemas (Pydantic)**
   - Implement request/response schemas for Company, Application, Round.
   - Add enums for statuses where applicable.

2. **Routers + CRUD**
   - `companies` router: CRUD endpoints
   - `applications` router: CRUD endpoints, scoped to authenticated user
   - `rounds` router: CRUD endpoints under an application

3. **Authorization**
   - Ensure application/round access is restricted to owning user.

4. **Error handling**
   - Standardize 404/403/422 behaviors.

**Dependencies:** Auth must remain functional (already implemented).

### Phase 2 — Configuration Hardening
**Goal:** Remove hardcoded secrets and align config/dependencies.

- Move JWT secret/algorithm/expiry to environment-driven settings.
- Align `requirements.txt` to match actual imports.
- Update README with required env vars and run steps.

### Phase 3 — Minimal Frontend (Full-stack requirement)
**Goal:** Provide a simple UI that consumes backend APIs.

- Choose a minimal frontend stack (to be decided once Jira scope confirms; repo currently has none).
- Pages:
  - Login/Register
  - Applications list (filter by status)
  - Create/edit application
  - (Optional) Manage rounds

**Dependencies:** Backend endpoints complete.

### Phase 4 — Testing & Quality
**Goal:** Add minimal automated tests to protect core flows.

- Backend tests:
  - Register/login
  - `/users/me`
  - CRUD applications scoped to user
- Add test DB strategy (e.g., ephemeral Postgres container or SQLite if compatible).

### Phase 5 — Packaging/Developer Experience
**Goal:** Make project runnable for reviewers.

- Add `.env.example`
- Add simple startup instructions in README
- Optional: Docker compose for Postgres + API

## 6. Task List (Traceability to Jira)

### Verified Jira coverage
- Jira project `codemie-placement-tracker`: **0 issues found**.

### Task mapping approach
Until Jira issues exist, tasks are listed with **placeholders**:
- `JIRA-TBD-001` etc.

Once Jira backlog exists, replace placeholders with real keys and titles.

#### Phase 1 Tasks (Backend)
- **JIRA-TBD-001 — Implement Company schemas**
  - Files: `app/schemas/company.py` (currently empty)
  - Depends on: none
- **JIRA-TBD-002 — Implement Application schemas**
  - Files: `app/schemas/application.py` (currently empty)
  - Depends on: none
- **JIRA-TBD-003 — Create companies router (CRUD)**
  - New module expected: `app/companies/router.py`
  - Depends on: JIRA-TBD-001
- **JIRA-TBD-004 — Create applications router (CRUD, per-user)**
  - New module expected: `app/applications/router.py`
  - Depends on: JIRA-TBD-002
- **JIRA-TBD-005 — Create rounds router (CRUD)**
  - New module expected: `app/rounds/router.py`
  - Depends on: JIRA-TBD-002

#### Phase 2 Tasks (Config)
- **JIRA-TBD-010 — Externalize JWT config**
  - Affects: `app/auth/jwt_handler.py`
  - Depends on: none
- **JIRA-TBD-011 — Fix/align dependencies in requirements.txt**
  - Depends on: audit outcome

#### Phase 3 Tasks (Frontend)
- **JIRA-TBD-020 — Create frontend scaffold**
  - Depends on: Phase 1 APIs
- **JIRA-TBD-021 — Implement auth UI + token storage**
  - Depends on: JIRA-TBD-020
- **JIRA-TBD-022 — Applications UI (list/create/edit)**
  - Depends on: JIRA-TBD-004

#### Phase 4 Tasks (Tests)
- **JIRA-TBD-030 — Add backend test harness**
  - Depends on: none
- **JIRA-TBD-031 — Add auth + application CRUD tests**
  - Depends on: JIRA-TBD-030, Phase 1 APIs

#### Phase 5 Tasks (DX)
- **JIRA-TBD-040 — Add README runbook & env documentation**
  - Depends on: config decisions

## 7. Dependencies Summary

- Frontend depends on backend APIs (Phase 1)
- Backend CRUD depends on schemas (Phase 1.1)
- Testing depends on stable API behavior
- Config hardening can be parallelized but should land before release

## 8. Risks, Blockers, Unresolved Questions

### Blockers (Verified)
- **Jira backlog is empty** (0 issues returned). Traceability cannot be completed until Jira has issues.

### Risks (Verified + inferred from repo state)
- Runtime table creation (`create_all`) risks schema drift.
- Hardcoded JWT secret is insecure.
- Committed `__pycache__` suggests repo hygiene issues.

### Unresolved questions
- Intended frontend framework (none exists in repo).
- Whether Rounds are required for MVP.
- Desired application status enum values.
- Whether Company is user-specific or global.

## 9. Recommended Sequence & Prerequisites

1. Populate Jira backlog with Epics/Stories/Tasks and acceptance criteria.
2. Implement backend schemas + CRUD routers + authorization.
3. Externalize JWT config; fix dependency mismatch.
4. Build minimal frontend UI consuming APIs.
5. Add tests and basic runbook.

---

**Document status:** Generated from verified repository state and verified Jira query results (0 issues). Update once Jira backlog exists.