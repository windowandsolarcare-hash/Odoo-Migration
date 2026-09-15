---
name: project_tech_app_architecture
description: "The fresh Tech App (static/tech/app.html) — auth model, TECH_GRANTED_OWNER scoped grant, money wrapper, care seam, what's held"
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-15T01:18:54.367Z
---

The **Tech App** is a fresh, cohesive sequential field app for technicians (built 2026-09-14, DJ-authorized; brief `3_Documentation/TECH_APP_BUILD_BRIEF.md`). Built from scratch (NOT v2_field with rooms removed) so it doesn't feel bolted-on; it **reuses the proven owner ENDPOINTS**, not the owner screens. Walks the SOP day in order: Start-of-day → Job card → At-the-door → **Assessment** → Do-the-work → End-of-job → Comms → End-of-day.

**★ Auth model (rediscovered the hard way — get this right):**
- Canonical entry = **`/static/tech/app.html`** (PUBLIC via the `/static` prefix — "UI shells, no data"), NOT `/tech/app` (that protected route was removed; the middleware 401s it before the handler = dead-end).
- Real front door = the existing **`/login`** (name + PIN → signed **tech-role session cookie**; it stashes `tc_user`={type,name,employeeId} in localStorage). There is NO in-page PIN gate and NO "access_code alone authenticates" — the session cookie is the auth. The app boots by reading `tc_user` (session proxy); absent or any API 401 → redirect to `/login`. `whoami` needs both a session AND an access_code and returns `{user:{employeeId,...}}` — the app skips it, using `tc_user` for identity.

**★ tech role is confined to `/tech` only** (`authz._role_allowed`). Reusing owner endpoints therefore needs a scoped grant: **`TECH_GRANTED_OWNER`** in authz.py (path-boundary matched, mirrors CHERYL_GRANTED_OWNER) — granted exactly: `/owner/api/upcoming`, `/next_job_link`, `/job/append_note`, `/maintenance`, `/attachment`, own clock (`payroll/status`,`clockin_crew`,`clockout_crew`,`break`), job timer (`timer/start`,`timer/stop`,`timer/sessions`). ★ List payroll/timer as EXACT sub-paths, never the greedy parent (payroll-admin + timer records/edit stay owner-only). MONEY is deliberately OFF the grant.

**★ Money** = the ONE tech endpoint **`POST /tech/api/record_payment`** (`routers/tech/payments.py`) — maps method→(method,memo) and calls the canonical `routers.owner.payments._stale_so_payment → _execute_payment` (DRY, no dup logic); amount read server-side from the SO. Tech role never touches an `/owner` payment route.

**Care seam** = [[project_wsc_busy_async_feedback_component]]'s sibling `routers/care_store.py` (shared, Specialists owns): Assessment findings (`POST /tech/api/care/item`) + before/after (`POST /tech/api/care/beforeafter`) → the customer PORTAL displays them. partner_id derived server-side from the SO. Photos reuse `POST /owner/api/attachment` (description 'care'/'beforeafter'). Window SOP embedded in Do-the-work via `/tech/sop` + `/tech/sop_pro` (serve the same static/cheryl/sop_windows*.html source, raw).

**HELD / deferred (do NOT build without the ruling):** the **Comms/ETA stage** is HELD pending DJ — `/owner/api/eta` is a customer-facing TEXT SEND and the brief's guardrail is "no customer-facing sends without DJ" (if yes → a scoped `/tech` eta wrapper, not an /owner grant). **inside/outside mode toggle** deferred (v1 single-mode). Future: a tech should see only his ASSIGNED jobs (v1 shows the whole day).
