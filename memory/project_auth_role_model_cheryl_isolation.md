---
name: project_auth_role_model_cheryl_isolation
description: "The app's session/role auth model (authz.py) and the /cheryl role-isolation fix — roles, _role_allowed, AUTH_ENFORCE is ON, how login sets role+pid, and why owner must not open /cheryl."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-10T03:50:31.125Z
---

**Auth model (saunders-render-app `routers/authz.py`):** session = signed cookie `make_session(name, role, pid)` → token body `{n,r,exp,p}`. `role` ('r') ∈ **'owner' | 'tech' | 'cheryl'**; `p` = the partner id (owner/Dan=3, Cheryl=23243). Login is at `/` (serves `static/login.html`) + POST `/api/login` (auth.py): looks up res.partner by name + `x_render_pin` + `x_render_role`; sets role from `x_render_role`, pid=user id; route_map redirects cheryl→`/cheryl/`, owner→owner app. `session_actor(request)` → 'cheryl' if role=='cheryl' or p==23243, else 'dan', else None.

**The gate:** `authz.check(request)` → (allowed, would_block). PROTECTED_PREFIXES = `/owner`, `/tech`, `/cheryl`. PUBLIC = `/static`, `/api/login`, `/book`, `/c/`, `/healthz`, `/sw.js` etc. — NOTHING under `/cheryl` is public (all post-login). `_role_allowed(role,path)`: tech→`/tech` only; cheryl→`/cheryl` + the `CHERYL_GRANTED_OWNER` prefixes (`/owner/hiring`, `/owner/hr`, `/owner/api/meeting`, `/owner/api/memory` — DJ-granted owner surfaces, path-boundary matched). **★ AUTH_ENFORCE is ON in prod** (verified 2026-09-10: a no-session browser GET /owner/ → 307 to /), so the gate actively blocks, not just monitors. Middleware `_authz_gate` (main.py): on block, HTML non-/api → RedirectResponse, else 401 JSON.

**The /cheryl isolation fix (2026-09-10, role/session desync bug):** `_role_allowed` had `if role=='owner': return True` = **owner opened EVERYTHING incl. `/cheryl`**. So when DJ's owner session landed on a `/cheryl` URL (an external bookmark/home-screen shortcut to the cheryl app, tapped under his owner cookie), it was served Cheryl's UI while `session.p` stayed 3 → `cheryl/documents.py _viewer_pid` read p=3 → `documents_for_recipient(3)` empty → Cheryl's "Shared with me" showed empty even though the note was shared to 23243. The VIEW flipped, the SESSION didn't. FIX: (A) `_role_allowed` owner → `return not path.startswith('/cheryl')` (owner app ≠ Cheryl's personal workspace); (B) `_authz_gate` hard-enforces `/cheryl` even in monitor mode + role-aware redirect: non-cheryl browser on `/cheryl` → 307 to `/owner/` (owner) or `/` (login); `/cheryl/api/*` → 401. A real cheryl session (role=cheryl) stays fully allowed. **Rule: role, launcher, and session.p must stay in lockstep — never serve one person's screens under another's login.** No owner code links to/calls `/cheryl` (v2_apps.js self-guards via `location.pathname.indexOf('/cheryl')===0`). See [[feedback_never_send_dj_to_odoo]], [[project_cheryl_dan_shared_tasks]], [[feedback_dj_owns_cheryl_erp_access]].
