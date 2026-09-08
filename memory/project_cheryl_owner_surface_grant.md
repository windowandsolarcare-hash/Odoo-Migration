---
name: project_cheryl_owner_surface_grant
description: "REPEATABLE mechanism (DJ 2026-09-08) to grant cheryl-role a named W&SC OWNER surface: add its path prefix(es) to CHERYL_GRANTED_OWNER in routers/authz.py — ONE list, boundary-matched, no new router/page edits. First grants: /owner/hiring + /owner/hr (+ their /owner/api/hiring, /owner/api/hr). NOT delegation. Never add /owner/v2_apps (the owner launcher). Security: path-scoped, company_id scoping untouched, cheryl still 401s on every other /owner/*."
metadata:
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-08T20:49:56.338Z
---

**Built 2026-09-08. DJ ruled (governance, firm): he will open MORE of his W&SC owner/ERP surfaces to Cheryl over time — the workspace is NOT permanently walled off — so cheryl-role access must be a REPEATABLE named-surface grant, NOT a bespoke hole each time.** First grant: WSC Hiring (/owner/hiring) + HR (/owner/hr), which Cheryl actively helps run.

**The mechanism — `routers/authz.py`:**
- `_role_allowed(role, path)` returned, for `cheryl`, `path.startswith('/cheryl')` ONLY → cheryl 401'd on all /owner/*.
- Added a tuple **`CHERYL_GRANTED_OWNER`** (currently `'/owner/hiring','/owner/api/hiring','/owner/hr','/owner/api/hr'`) + the cheryl branch now also returns True for a **PATH-BOUNDARY** match:
  `any(path == p or path.startswith(p + '/') for p in CHERYL_GRANTED_OWNER)`.
- ★ **To grant Cheryl a NEW W&SC owner surface later: add its prefix(es) to CHERYL_GRANTED_OWNER. That's it** — no new router, no delegation, no page edits (unlike the /cheryl/ideas delegation pattern in [[project_cheryl_ideas_delegation]], which this REPLACES as the preferred method for owner-surface grants).

**Why boundary-match, not bare `startswith` (Lead's hardening, important as the list grows):** a bare prefix over-grants by collision — `/owner/hr` would also match a future `/owner/hr-report` / `/owner/hranything`, silently handing Cheryl an ungranted surface. `path == p or startswith(p + '/')` grants `/owner/hr` and `/owner/hr/...` (so /hr/jd, /hr/offer work) but NOT `/owner/hrX`. Query strings are fine (`check()` uses `request.url.path`, already query-stripped). Unit-tested: /owner/hr-report, /owner/hring, /owner/hiringx → DENIED.

**Why it needed nothing else (recon):** the pages already anticipate Cheryl (openWSCHR sets localStorage hr_user='Cheryl'+wsc_ac; openWSCHiring sets wsc_ac); the ONLY wall was authz. hiring.py serves /owner/hiring + /owner/api/hiring/*; hr.py serves /owner/hr (hr.html is a stub → the real page /static/owner/v2_hr.html, already public) + /hr/jd + /hr/offer + /owner/api/hr/*. Every DATA call the pages make lands in these 4 namespaces — no whoami/shared-owner dependency. Their only out-of-namespace refs are shared owner CHROME (clock-in bar, ql_panel, /owner/v2_apps launcher, a /owner/v2_home "home" link) which 401 GRACEFULLY (chrome absent, Hiring/HR function intact).

**SECURITY (DJ's guardrails held):** path-scoped — cheryl STILL 401s on every other /owner/* (dashboard, customers, voice, payments…); each handler's own **company_id** fails-open scoping is untouched (W&SC data only; no other-company data lives under these paths); **★ NEVER add `/owner/v2_apps`** (the owner launcher = the full owner app list — Cheryl must not see it). Verified on live: anonymous (no cookie) hits /owner/hiring + /owner/hr → 401 (grant is COOKIE-scoped, not public). Positive path (cheryl reaches + FUNCTIONS) + boundary probes = Lead's cheryl-cookie QC (a Specialists session can't mint a cheryl cookie — see [[feedback_verify_limits_before_declaring]]).

**Follow-up (not blocking access):** make the Hiring/HR pages' "home" link + owner chrome context-aware for cheryl (home → /cheryl/, hide the owner launcher) so her nav is clean — same pattern as [[project_cheryl_ideas_delegation]]'s ideas.html base-detection.
