---
name: project_candidate_comparison_entrypoints
description: "The ZipRecruiter Candidate Comparison page lives at GET /owner/hiring/compare (Portal's hiring_compare.py) and is cheryl-reachable; entry points = DJ v2_apps tile + Cheryl index.html WSC Hire chooser."
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-10T14:40:57.534Z
---

**Candidate Comparison page (Portal-owned):** `GET /owner/hiring/compare` → `routers/owner/hiring_compare.py:73` (a REAL route — the router reads the HTML and serves it, NOT a /static path). Notes API `/owner/api/hiring/compare/notes` (GET:80 / POST:98); extras (GET:129 / POST:149). The in-page **Call button POSTs `/owner/voice/dial`** → stays dark for Cheryl until DJ grants `/owner/voice/dial` (see [[project_voice_dial_caller_phone]]).

**Cheryl-role reaches it with NO new authz grant** (Portal-verified through the middleware, not just page code): `/owner/hiring/compare` starts with `/owner/hiring`, which is in `CHERYL_GRANTED_OWNER`, and `_role_allowed`'s cheryl branch is a path-boundary match (`path==p or startswith(p+'/')`). Notes/extras under `/owner/api/hiring` are granted too. Gate is enforcing (un-authed `/owner/api/*` → 401), so it's genuinely DJ+Cheryl only.

**Entry points (DEPLOYED 2026-10-10 to main — DJ "deploy both now" after Portal's Page 2 /owner/hiring/compare went live; v2_apps.js 1a62e209 + cheryl/index.html 2224fb1d, stale-base re-applied onto fresh main, Lead+Portal verified Page 2 live by content before ship; Dispatcher/HR-routed):**
- **DJ launcher** = `static/owner/v2_apps.js` APPS array (the WSCLauncher 🚀 FAB list): added tile `{ ico:'🧮', t:'Candidate Compare', h:'/owner/hiring/compare' }`.
- **Cheryl hub** = `static/cheryl/index.html`: the WSC Hire card `openWSCHiring()` now opens a plain-`<div>` **chooser** (no native dialog) with exact-label buttons **"Old ATS"** → `/owner/hiring#cheryl` and **"New — ZipRecruiter"** → `/owner/hiring/compare#cheryl`; both set `localStorage.wsc_ac='wsc2026'` first (the owner access code the hiring/compare pages need — the `ac:true` pattern, also in `static/cheryl/launcher.js`). `openWSCHiring()` kept intact.

**Ownership:** `static/cheryl/*` shell — Cheryl's-Cloud owns some Cheryl fragments (e.g. plan-views.html New-project button); notified them on the index.html touch to avoid a collision. See [[project_cheryl_dan_shared_tasks]], [[feedback_dj_owns_cheryl_erp_access]].
