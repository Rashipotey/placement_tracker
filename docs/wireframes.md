# Wireframes (text-based) — Placement Tracker Enhancements

> **Scope:** Text-only wireframes for a minimal UI that exercises the approved backend enhancements. The repository currently contains backend code only; these wireframes are for a planned UI.

---

## 1. Login page

```
+---------------------------------------------------+
| Placement Tracker                                 |
+---------------------------------------------------+
| Email:    [____________________________]          |
| Password: [____________________________]          |
|                                                   |
| [ Login ]                                         |
|                                                   |
| Don't have an account? [Register]                 |
+---------------------------------------------------+
| Error area (inline):                              |
| - "Invalid email or password"                     |
| - "Server unreachable"                           |
+---------------------------------------------------+
```

**Interactions**
- Click **Login**:
  - Sends `POST /auth/login`
  - On success: store token and navigate to Applications list.
  - On failure (401): show inline error.

---

## 2. Register page

```
+---------------------------------------------------+
| Create account                                    |
+---------------------------------------------------+
| Name:     [____________________________]          |
| Email:    [____________________________]          |
| Password: [____________________________]          |
|                                                   |
| [ Register ]                                      |
|                                                   |
| Already have an account? [Login]                  |
+---------------------------------------------------+
| Validation messages:                              |
| - "Email already exists"                          |
| - "Password must be at least N characters" (opt) |
+---------------------------------------------------+
```

**Interactions**
- Click **Register**:
  - Sends `POST /auth/register`
  - On success: navigate to Login.

---

## 3. Applications list page

```
+--------------------------------------------------------------------------------+
| Placement Tracker                                  [Logout]                    |
+--------------------------------------------------------------------------------+
| [Add Application]  [Manage Companies]                                        |
+--------------------------------------------------------------------------------+
| Filters (optional): Status [All v]   Search [__________]                      |
+--------------------------------------------------------------------------------+
| Applications (My Applications)                                               |
|--------------------------------------------------------------------------------|
| Company        | Role          | Status     | Notes      | Actions             |
|--------------------------------------------------------------------------------|
| Acme Corp      | SDE Intern    | APPLIED    | ...        | [Edit] [Delete]     |
| Globex         | Analyst       | INTERVIEW  | ...        | [Edit] [Delete]     |
|--------------------------------------------------------------------------------|
| Pagination (optional):  < Prev   Page 1 of 1   Next >                          |
+--------------------------------------------------------------------------------+

Delete confirmation modal:
+-----------------------------+
| Delete application?         |
| This cannot be undone.      |
| [Cancel]        [Delete]    |
+-----------------------------+

Error toast/banner:
- "Unauthorized, please login again" (401)
- "Failed to load applications" (network/500)
```

**Interactions**
- On page load:
  - Calls `GET /applications` with bearer token.
- **Edit**:
  - Navigate to application edit page.
- **Delete**:
  - Confirm → call `DELETE /applications/{id}` → refresh list.

---

## 4. Create / Edit application page

```
+---------------------------------------------------+
| < Back | Application                              |
+---------------------------------------------------+
| Company: [Select company v]   [Add new company]    |
| Status:  [APPLIED v]                                |
| Notes:                                         |
| [_____________________________________________]   |
| [_____________________________________________]   |
|                                                   |
| [Save]     [Cancel]                               |
+---------------------------------------------------+
| Inline validation:                                |
| - "Company is required"                          |
| - "Status must be one of: APPLIED, INTERVIEW..." |
+---------------------------------------------------+
```

**Interactions**
- On load (create/edit):
  - Call `GET /companies` to populate dropdown.
- Save (create):
  - `POST /applications`
- Save (edit):
  - `PATCH /applications/{id}`

---

## 5. Manage companies page (minimal)

```
+---------------------------------------------------+
| < Back | Companies                                |
+---------------------------------------------------+
| Create company                                    |
| Name: [____________________]                      |
| Role: [____________________]                      |
| Location: [________________] (optional)           |
| Package LPA: [_____] (optional)                   |
| Link: [____________________] (optional)           |
|                                                   |
| [Create]                                          |
+---------------------------------------------------+
| Companies list                                    |
|---------------------------------------------------|
| Acme Corp - SDE Intern                            |
| Globex - Analyst                                  |
+---------------------------------------------------+

Errors:
- "Name and Role are required"
- "Failed to create company"
```

**Interactions**
- Create calls `POST /companies`
- List calls `GET /companies`

---

## 6. Authorization/Session expired state

When any API call returns 401:

```
+----------------------------------------------+
| Session expired                              |
| Please login again.                          |
| [Go to Login]                                |
+----------------------------------------------+
```

Behavior:
- Clear stored token and redirect to Login.

