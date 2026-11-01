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
| CPT-17 scaffold + auth-guarded routes | Jira; HLD §3.1 | Blocked | no frontend tooling exists; needs user approval for build tool/dependencies |
| CPT-18 / CPT-8 register/login/logout, localStorage token, Bearer header, 401 → login | Jira; LLD §5; Wireframes 2–3 | Blocked | |
| CPT-19 applications list (loading/empty/error, optional status filter) | Jira; Wireframes 4 | Blocked | |
| CPT-20 create/edit form + delete confirm | Jira; Wireframes 5–6 | Blocked | needs `GET /companies` |
| CPT-26 CORS (prerequisite for browser calls) | LLD §6 | Done | env-configurable `CORS_ORIGINS`; allowed origin gets header, disallowed does not, preflight with Authorization OK (curl-verified) |
| Rounds UI | HLD §5.4 | Out of scope | no Jira story |

## CPT-4 Tests
| Req | Artifact | Status | Notes |
|---|---|---|---|
| CPT-24 pytest harness + isolated test DB | Jira; LLD §7 | Blocked | no safe test DB: `.env` DATABASE_URL points at the dev database `placement_tracker`; needs a dedicated DB from the user; no tests; pytest not installed in `.venv` |
| CPT-11 tests: auth, `/users/me`, application CRUD, cross-user authorization | Jira; LLD §7 | Blocked | |

## Open questions
1. Cross-user access status code: CPT-11 says 403; LLD §3.3/3.4 says 404.
2. Stories outside the four epics (CPT-25, 27–32: Alembic, docker-compose, OpenAPI docs, `__pycache__` cleanup, CI) are out of scope unless approved.
3. Frontend build tooling is not specified in the artifacts.
4. PUT vs PATCH for updates: LLD lists both and marks PATCH optional.
5. Test database: only the development database is configured; a dedicated test DB is required before CPT-4 tests are run.
