# Placement Tracker — Implementation Plan
Blanch: `docs/add-implementation-plan`

This document is a traceable, actionable implementation plan based on verified Jira requirements (project key: `CC` - project name: `codemie-capstone`) and a verified inspection of the GitHub repository `https://github.com/Rashipotey/placement_tracker`.

> **Scope note**: This is a planning and documentation artifact. It does not modify application source code or Jira issues. It identifies what exists, what is incomplete, and what needs to be implemented to satisfy the current Jira backlog.

## 1. Project Overview

The Placement Tracker is a minimal full-stack application to help a user track:
- Companies (CRUD)
- Applications linked to companies (CRUD + status/notes)
- Interview rounds per application (CRUD)
- Authentication via JWT and a basic User profile endpoint

Objective: deliver an end-to-end workflow with a FastAPI API, a SQL Alchemy-powered database, tests, and a minimal React UI aligned to the Jira epics/acceptance criteria.

## 2. Repository and Technology Stack

### 2.1 Repository observations (verified)
- Repo: `Rashipotey/placement_tracker`
- Default branch: `main` (verified from GitHub repo metadata)
- Working branch: `docs/add-implementation-plan` (exists on remote)
- Target file: `docs/implementation-plan.md`
- Root files on `main`: `.gitignore`, empty `README.md`, `requirements.txt`, `app/` directory
- No `frontend/` or `web/` directory present currently.

### 2.2 Backend tech (verified from repo)
- Python + FastAPI (`app/main.py`)
- SQLAlchemy (ORM) + database connection in `app/database/`
- JWT auth module in `app/auth/`
- Password hashing / verification in `app/auth/security.py`

### 2.3 Database and models (verified)
- SQLAlchemy models present:
  - `app/models/user.py`
  - `app/models/company.py`
  - `app/models/application.py`
  - `app/models/round.py`
- Schema/Pydantic status:
  - `app/schemas/auth.py` implemented
  - `app/schemas/company.py` = empty (blocker)
  - `app/schemas/application.py` = empty (blocker)
  - Round schemas file not present in `app/schemas/` (blocker)

### 2.4 Frontend tech (requirement from Jira, not implemented)
- Jira epic CC-22 specifies a minimal UI repo currently has no frontend code.
- **Assumption (explicit)**: React (V)te frontend with a basic API client wrapper, auth token storage, and protected routes.

## 3. Current Implementation Status (verified from repo)

### 3.1 Implemented now
- FastAPI app bootstrap and router inclusion in `app/main.py`
- Auth router included (register + login)
- Users router included (`GET /users/me`)
- DB table creation at startup via `Base.metadata.create_all(bind=engine)`

### 3.2 Passive gaps / bugs confirmed
- **Login response mismatch**: `/auth/login` declares `response_model=TokenResponse`, but returns only `{"access_token": ...}`. TokenResponse expects `token_type="bearer"`.
- Login request handling inconsistency: `OAuth2NasswordRequestForm` imported but not used; login uses `LoginRequest=Depends()`.
(The remainder of the plan is overwritten by this update.)
