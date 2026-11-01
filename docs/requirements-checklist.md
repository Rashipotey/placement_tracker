# Requirements → Implementation Checklist

Baseline from `main` (commit 884318f), Jira `CPT`, and Confluence space `capstonear`
(Architecture Diagram, HLD, LLD, UI Wireframes). Maintained by the Implementation Agent
(`.claude/agents/implementation-agent.md`). Status: Done / Partial / Missing / Out of scope.

## CPT-1 Backend CRUD
| Req | Artifact | Status | Notes |
|---|---|---|---|
| CPT-12 Company schemas | Jira; LLD §3.2 | Done | verified via smoke run (throwaway SQLite, not the pytest suite) |
| CPT-13 Companies router (global, authed; 409 on delete if referenced) | Jira; LLD §3.2 | Done | wired in `main.py`; 401/404/422/409 smoke-verified; PUT only (PATCH is optional in LLD) |
| CPT-14 Application schemas (status allow-list) | Jira; LLD §3.3 | Done | smoke-verified |
| CPT-15 Applications router, scoped to `current_user.id`, company must exist | Jira; LLD §3.3 | Done | per user decision (Option A): missing -> 404, owned by another user -> 403 in `get_owned_application`; pytest verified GET/PUT/DELETE as non-owner -> 403, owner data unchanged, list only own |
| CPT-16 Round schemas + nested router with parent ownership check | Jira; LLD §3.4 | Done | same helper: non-owner list/create/get/update/delete -> 403; missing application or round -> 404; round under a different application -> 404 (pytest verified) |
| Models User/Company/Application/Round | LLD §2 | Done | match LLD |
| Auth register/login, `GET /users/me` | LLD §3.1 | Done | |

## CPT-3 Config & auth hardening
| Req | Artifact | Status | Notes |
|---|---|---|---|
| CPT-21 JWT secret/algorithm/expiry from env | Jira CPT-10 | Done | `jwt_handler.py` uses `settings`; no secret literal in `app/` (grep); token create/decode and protected routes smoke-verified; `JWT_SECRET_KEY` is required (no default), so existing `.env` files must add it |
| Single settings module (`DATABASE_URL`, `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `JWT_EXPIRE_MINUTES`) | Jira CPT-10 | Done | `app/core/config.py`; missing secret fails with a validation error (verified); `extra=ignore` so unrelated `.env` keys no longer crash startup |
| CPT-22 requirements match imports | Jira CPT-10 | Done | removed `python-settings`; pinned `bcrypt==4.0.1` because passlib 1.7.4 fails with bcrypt 5 on register (observed); `pip install --dry-run -r requirements.txt` resolves; fresh-venv install not run |
| CPT-23 `.env.example` + README runbook | Jira CPT-3 | Done | README steps not followed in a clean environment |

## CPT-2 Frontend
| Req | Artifact | Status | Notes |
|---|---|---|---|
| CPT-17 scaffold + auth-guarded routes | Jira; HLD §3.1 | Done | Vite + React + react-router-dom (user-approved) in `frontend/`; build OK; Selenium: unauthenticated `/applications` redirects to `/login`, and again after logout |
| CPT-18 / CPT-8 register/login/logout, localStorage token, Bearer header, 401 → login | Jira; LLD §5; Wireframes 2–3 | Done | Selenium: register/login/logout; register messages ("Email is required", "Password must be at least 8 characters", "Email already registered"); login messages ("Email is required", "Invalid email or password"); invalid token in localStorage -> cleared and redirected to /login |
| CPT-19 applications list (loading/empty/error, optional status filter) | Jira; Wireframes 4 | Done | Selenium: loading ("Loading applications...", via 3s emulated latency), empty, rows, status filter, error ("Failed to load applications" + Retry via emulated offline, Retry recovers) |
| CPT-20 create/edit form + delete confirm | Jira; Wireframes 5–6 | Done | Selenium: create, edit, delete Cancel/confirm, "Company is required", save failure banner "Unable to save application". "Status is required" is unreachable by design: the status select has no empty option (defaults to APPLIED) |
| CPT-26 CORS (prerequisite for browser calls) | LLD §6 | Done | env-configurable `CORS_ORIGINS`; allowed origin gets header, disallowed does not, preflight with Authorization OK (curl-verified) |
| Rounds UI | HLD §5.4 | Superseded | now covered by the user-approved requirement below (section "User-approved additions") |

## CPT-4 Tests
| Req | Artifact | Status | Notes |
|---|---|---|---|
| CPT-24 pytest harness + test DB | Jira; LLD §7 | Done | `tests/` + `requirements-dev.txt`; per user override, tests run against the dev DB `placement_tracker` (was empty, read-only inspection first); every record has a random `pytest_<id>_` prefix and only those are deleted at session end; verified all 4 tables had 0 rows after the run; no create_all/drop_all/truncate |
| CPT-11 tests: auth, `/users/me`, application CRUD, cross-user authorization, rounds | Jira; LLD §7 | Done | 15 pytest tests + 1 opt-in e2e module; cross-user asserts 403 (user decision) |

## User-approved additions (NOT yet in Jira or Confluence)
User statement: "the application must have round_id and user must be able to create/edit/delete rounds", in both frontend and backend; recorded in the repo only (Jira and Confluence deliberately not edited). HLD §5.4 and the wireframes still exclude a rounds UI and need a documentation update by the user. Minimal interpretation used (correct me if wrong):
| Req | Status | Notes |
|---|---|---|
| `applications.round_id` = the application's current round (nullable FK to `rounds.id`, `ON DELETE SET NULL`, `use_alter` for the circular FK) | Done | `create_all` DDL for a fresh DB checked with a mock PostgreSQL engine (CREATE TABLE then ALTER ADD CONSTRAINT); existing DB upgraded with an additive ALTER (see README "Upgrading an existing database"); row counts unchanged |
| `ApplicationRead` exposes `round_id`; `ApplicationUpdate` accepts `round_id` (null clears); a round of another application or a nonexistent round -> 422; not accepted on create (no rounds exist yet; ignored) | Done | pytest verified |
| Deleting the current round sets `round_id` to null; deleting an application also removes its rounds (previously a FK error, fixed because the UI now makes rounds common) | Done | pytest verified |
| Not-owned -> 403 / missing -> 404 (Option A) preserved for setting `round_id` | Done | pytest verified |
| Rounds UI: `/applications/:id/rounds` (list with loading/empty/error, create, edit round_name/status/feedback, delete with confirmation, "(current)" marker) and a "Current round" select on the application edit form | Done | Selenium verified (create, edit, set/clear current round, delete with Cancel and confirm) |

## Open questions
1. RESOLVED by user decision (Option A): missing -> 404, owned by another user -> 403 (CPT-11). Confluence LLD §3.3/3.4/§4 still says 404 for not-owned and needs a documentation update by the user (not edited here).
2. Stories outside the four epics (CPT-25, 27–32: Alembic, docker-compose, OpenAPI docs, `__pycache__` cleanup, CI) are out of scope unless approved.
3. Frontend build tooling is not specified in the artifacts.
4. PUT vs PATCH for updates: LLD lists both and marks PATCH optional.
5. Test database: user explicitly overrode the dev-database rule for this run; tests use the `placement_tracker` DB with prefixed records and targeted cleanup.
6. Provisional, awaiting review: `bcrypt==4.0.1` pin (verified need: with bcrypt 5.0.0 `POST /auth/register` raised `ValueError: password cannot be longer than 72 bytes` inside passlib 1.7.4's backend self-test) and `extra="ignore"` in settings (verified need: the original `Settings` raised `extra_forbidden` on the unrelated `GITHUB_OKEN` key in `.env`, so the app could not start).
7. `.env.example` in the working tree was modified outside this run (`DATABASE_URL` now `postgres:postgres@...`); not committed.
8. Logging: no logging requirement found in Jira (CPT-1..11, CPT-26 read in full; a project text search for logging/logger/audit/observability matched only CPT-8 via the phrase "log in"), the four Confluence pages (read in full; CQL matches on HLD/Wireframes are "login" stemming), or `docs/implementation-plan.md` (no match). None added.
9. E2E: `tests/e2e/test_e2e.py` (opt-in `E2E=1`, Selenium + Edge) - 11 scenarios pass (full suite incl. e2e: 26 passed after the 403 change); clean fresh-venv run (outside the repo) of the full suite: 16 passed.
10. CORS default (`CORS_ORIGINS` unset in `.env`): code default is `http://localhost:5173,http://localhost:3000`. Verified with only `.env` config: `http://localhost:5173` and `http://localhost:3000` are allowed (simple request and preflight with Authorization); `http://127.0.0.1:5173` is NOT allowed (preflight returns 400, no allow-origin header). Vite dev server by default is not reachable at 127.0.0.1 (connection failed), so this only matters if the frontend is opened that way or `--host` is used. Recommended minimal fix if needed: set `CORS_ORIGINS` in `.env` to include `http://127.0.0.1:5173`. No config/code changed.
