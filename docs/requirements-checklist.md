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
| CPT-15 Applications router, scoped to `current_user.id`, company must exist | Jira; LLD §3.3 | Partial | CRUD + scoping smoke-verified; cross-user status code (403 vs 404) unresolved: currently one shared 404 in `get_owned_application`, not asserted by any test |
| CPT-16 Round schemas + nested router with parent ownership check | Jira; LLD §3.4 | Partial | CRUD smoke-verified; cross-user code unresolved (uses `get_owned_application`) |
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
| CPT-17 scaffold + auth-guarded routes | Jira; HLD §3.1 | Done | Vite + React + react-router-dom (user-approved) in `frontend/`; `npm run build` succeeds; headless Chrome shows the login page when opening `/applications` without a token |
| CPT-18 / CPT-8 register/login/logout, localStorage token, Bearer header, 401 → login | Jira; LLD §5; Wireframes 2–3 | Partial | implemented and builds; not exercised end-to-end in a browser against the backend (no browser automation available); the backend endpoints it calls are covered by pytest |
| CPT-19 applications list (loading/empty/error, optional status filter) | Jira; Wireframes 4 | Partial | implemented and builds; not exercised in a browser |
| CPT-20 create/edit form + delete confirm | Jira; Wireframes 5–6 | Partial | implemented (company dropdown from `GET /companies`, no "+ Add Company") and builds; not exercised in a browser |
| CPT-26 CORS (prerequisite for browser calls) | LLD §6 | Done | env-configurable `CORS_ORIGINS`; allowed origin gets header, disallowed does not, preflight with Authorization OK (curl-verified) |
| Rounds UI | HLD §5.4 | Out of scope | no Jira story |

## CPT-4 Tests
| Req | Artifact | Status | Notes |
|---|---|---|---|
| CPT-24 pytest harness + test DB | Jira; LLD §7 | Done | `tests/` + `requirements-dev.txt`; per user override, tests run against the dev DB `placement_tracker` (was empty, read-only inspection first); every record has a random `pytest_<id>_` prefix and only those are deleted at session end; verified all 4 tables had 0 rows after the run; no create_all/drop_all/truncate |
| CPT-11 tests: auth, `/users/me`, application CRUD, rounds | Jira; LLD §7 | Partial | 10 tests pass; cross-user authorization (applications and rounds) NOT tested because 403 vs 404 is unresolved |

## Open questions
1. Cross-user access status code: CPT-11 says 403; LLD §3.3/3.4 says 404.
2. Stories outside the four epics (CPT-25, 27–32: Alembic, docker-compose, OpenAPI docs, `__pycache__` cleanup, CI) are out of scope unless approved.
3. Frontend build tooling is not specified in the artifacts.
4. PUT vs PATCH for updates: LLD lists both and marks PATCH optional.
5. Test database: user explicitly overrode the dev-database rule for this run; tests use the `placement_tracker` DB with prefixed records and targeted cleanup.
6. Provisional, awaiting review: `bcrypt==4.0.1` pin (verified need: with bcrypt 5.0.0 `POST /auth/register` raised `ValueError: password cannot be longer than 72 bytes` inside passlib 1.7.4's backend self-test) and `extra="ignore"` in settings (verified need: the original `Settings` raised `extra_forbidden` on the unrelated `GITHUB_OKEN` key in `.env`, so the app could not start).
7. `.env.example` in the working tree was modified outside this run (`DATABASE_URL` now `postgres:postgres@...`); not committed.
