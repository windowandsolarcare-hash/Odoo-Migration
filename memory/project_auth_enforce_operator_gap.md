---
name: project_auth_enforce_operator_gap
description: "AUTH_ENFORCE=1 401's the Operator (headless no-cookie /owner ops) — Operator needs a real auth path BEFORE enforcement can be turned on. Rolled back 2026-09-04."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-05T01:13:27.264Z
---

**Flipping `AUTH_ENFORCE=1` breaks the Operator, and must NOT be done until the Operator has real auth.** (Rolled back 2026-09-04, same day it was turned on.)

**What happened:** the Cheryl-silo go-live set `AUTH_ENFORCE=1` (Render env). It correctly walled Cheryl to `/cheryl/*` (verified: cheryl session got 401 on `/owner/*`, 200 on `/cheryl/*`). **But it also 401'd the OPERATOR out of every `/owner/*` op** (scheduling, cards, offers, payments — DJ's live ops hands). Lead rolled it back to `AUTH_ENFORCE=0` (merge-safe via Render MCP `update_environment_variables`, ~2-3 min) — fully reversible, no lasting harm.

**Root cause:** the **Operator** is a headless Claude session that performs DJ's live operations by calling the app's own `/owner/*` HTTP endpoints (per its charter [[feedback_assistant_use_app_workflow_not_raw_api]]) with **NO login cookie**. It only worked because enforcement was off (monitor mode). In the authz soak report (`/owner/api/authz/report`) its calls appear as `no-cookie` from `curl`/`python-requests` — **indistinguishable from fleet smoke-tests**, and were wrongly cleared at GATE 2 as "cookieless test traffic, fine to block." They are NOT fine to block — they're live ops.

**The lesson for any future AUTH_ENFORCE attempt:** the soak's `no-cookie` automation bucket hides real, must-keep callers (the Operator). Before enforcing, the Operator needs a real auth path FIRST:
- **Cleanest (Lead's pick):** Operator logs in programmatically — POST owner name+PIN to `/api/login` → capture the `wsc_session` cookie → send it on all its `/owner/*` calls. DJ drops an owner credential in a key file for it. No code change, rule-4 clean.
- **Alt:** a service-token/header (e.g. `OPERATOR_SECRET`) added to authz PUBLIC handling — but that's a code change + a new secret.

Then re-run the (now one-step, non-disruptive) silo flip WITH the Operator authed. **Cheryl is already fully set up** ([[project_cheryl_hud_v1]]): partner 23243 (cheryl role + PIN), `/cheryl/hud` + `/cheryl/library` live, seed loaded → re-enabling is just the `AUTH_ENFORCE=1` flip once the Operator is covered. Deferred to a weekday (no weekend rush) per DJ.

Ties to [[feedback_verify_limits_before_declaring]]: a soak/report that can't distinguish a real headless caller from test noise is not sufficient proof on its own — enumerate who the no-cookie callers actually ARE before enforcing.
