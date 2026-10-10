---
name: project_voice_dial_caller_phone
description: "/owner/voice/dial now rings the LOGGED-IN user's own phone (not always DJ) via _caller_phone resolving the authz session → hr.employee or Cheryl's partner; + the hr.employee roster facts + the authz grant Cheryl needs."
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-10T08:28:05.070Z
---

**STAGED 2026-10-10 (branch specialists/dialer-caller-phone, voice.py 909f79c2; Lead QC-GREEN; code deploys independently for DJ/employees, Cheryl use waits on an authz grant → DJ deploy).** Driver: Cheryl runs Lead-Technician phone interviews from HER phone Mon/Tue Oct 12-13 (Dispatcher/HR).

**The resolved `ring` is normalized to E.164** (`+1XXXXXXXXXX`) inside `_caller_phone`'s validator so a display-format employee phone ("(760) 334-8311") still rings via Twilio; non-dialable → '' → DJ fallback (Lead QC nit).

**Change (surgical):** `routers/owner/voice.py` `voice_dial` rang `'To': DJ_PHONE_NUMBER` always. Now `ring = _caller_phone(request, p) or DJ_PHONE_NUMBER`; `'To': ring`. `From`/caller-ID the callee sees is UNCHANGED (still `biz` = the chosen Main line (760) 334-5355) — only who rings FIRST changes. No new routes.

**`_caller_phone(request, body)`** — identity from the **authz session cookie** (`authz.session_from_request`; `{n:name, r:role, p:partner_id}`), never the body's claims; optional `access_code`/`employee_id` override:
1. employee (access_code / employee_id / session name `n`) → `hr.employee` phone, priority **mobile_phone > phone > work_phone > private_phone**.
2. **Cheryl** (role `cheryl` / `p==23243`) → her `res.partner` phone (she is NOT an hr.employee).
3. no dialable number (≥10 digits) → `''` → rings DJ (unchanged fallback).

**Roster facts (verified via Odoo 2026-10-10):** ONLY 3 `hr.employee`: id=1 **Daniel J Saunders = DJ** (phone/work/mobile all his cell …6946; `DJ_EMPLOYEE_ID` default=1), id=2 Danny Saunders (only work_phone …8311), id=3 David Osuna (inactive, no PIN). **Cheryl is NOT an hr.employee** — she's `res.partner 23243` ("Cheryl Johnson", cell ends **…2822**, company_id=False). So "ring from their hr.employee record" (Dispatcher's assumed mechanism) does NOT cover Cheryl → resolver branch 2 uses her partner phone.

**⚠ AUTHZ GRANT Cheryl needs (DJ's call — [[feedback_dj_owns_cheryl_erp_access]]; authz.py = Lead's seam, builders don't edit it):** a `cheryl`-role session is BLOCKED from `/owner/voice/dial` today — `_role_allowed` (routers/authz.py) only grants cheryl the paths in `CHERYL_GRANTED_OWNER` (hiring/hr/meeting/memory). To let Cheryl use the dialer, add `'/owner/voice/dial'` + `'/owner/voice/numbers'` (the dialer loads the number list on open) to `CHERYL_GRANTED_OWNER`. Then her cheryl session (p=23243) rings …2822. The dialer static page is under `/static/...` (not authz-gated). DO NOT use the `'owner'` shortcut login for Cheryl — it resolves `n='DJ Sanders'` and would ring DJ.

**Identity plumbing:** PIN login = `hr.employee.x_render_access_code` (`/api/auth`, `/api/whoami?access_code=`). Owner cookie minted via `authz.make_session(name, role, pid)`; `n` = employee name. Dialer page = `static/owner/v2_dialer.html`, posts `{to, caller_id, name}` to `/owner/voice/dial` ([[feedback_call_opens_dialer_never_dials]]). Voice router mounted `prefix="/owner"` (main.py:1080), single `/voice/dial` def (not shadowed). See [[project_cheryl_dan_shared_tasks]].
