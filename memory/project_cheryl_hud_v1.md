---
name: project_cheryl_hud_v1
description: "Cheryl's HUD v1 (/cheryl/hud) — additive per-viewer layer over the SAME feed store; how it reuses DJ's v2_hud.html without forking; go-live gates."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-04T22:27:03.512Z
---

Cheryl's HUD v1 shipped + end-to-end verified 2026-09-04 (spec: `3_Documentation/WSC-CHERYL-HUD-SPEC.md`; contract: `FEED_CONTRACT_V2_LIVELIST.md`). A SECOND viewer (Cheryl, role `cheryl`) reads the SAME `wsc.feed.items` store as DJ, entirely ADDITIVELY — DJ's HUD is byte-identical (the §1 hard rule).

**The additive design (all in `routers/owner/feed.py`, DJ's paths untouched):**
- `list_items_for_viewer(pid, audience_tag, ...)` + `ack_for_viewer(iid, op, pid, ...)`. A non-owner viewer sees an item ONLY if its optional `audience` list contains their tag; **omission = owner-only = today's behaviour** (so every existing card is invisible to Cheryl). Per-viewer status lives in `entry['viewers'][str(pid)]`; the top-level `status` stays DJ's, read/written exactly as today. Resolution: `viewers[pid]` if present else `'new'` — NEVER fall back to top-level status.
- `feed_live.py` has a SEPARATE `cheryl_cards(pid)` registry (`CHERYL_PRODUCERS`/`CHERYL_IDS`) — NOT in `LIVE_PRODUCERS` — so DJ's `live_cards()` is provably unchanged. v1 producers: `_cheryl_questions` + `_cheryl_stale_surfaces` (card 1 "tasks" was CUT — no `x_owner`/task-surface yet). They read Cheryl's-cloud's blob `wsc.decisions.2026`: card 2 counts `questions[].state=='open'`, card 3 counts `surfaces[].state=='stale'` under decisions whose `state` is open/propagating. Both teleport to the Workbench artifact. Derived/read-only → auto-clear when count hits 0.

**Session carries the partner id:** `authz.make_session(name, role, pid=None)` adds optional `p` to the token (backward-compatible; old 180-day cookies still verify). `auth.py` login passes `user.get("id")`. Verified live: a cheryl login yields `{'r':'cheryl','p':<id>}`.

**Renderer REUSE, not fork (§7):** `static/owner/v2_hud.html` was parameterized with two globals near the top of its inline script: `var FEED_BASE=(window.WSC_FEED_BASE||'/owner')` and `var HUD_EXTRAS=(window.WSC_HUD_EXTRAS!==false)`. All ~11 feed calls use `FEED_BASE+'/api/feed/...'`; the 2 DJ-only calls (`/owner/api/lead/daily_status`, `/owner/api/library/hud_seen`) are gated behind `HUD_EXTRAS`. DJ's page injects NEITHER global → defaults → byte-identical network calls. `routers/cheryl/hud.py` serves the SAME file with `<script>window.WSC_FEED_BASE='/cheryl';window.WSC_HUD_EXTRAS=false;</script>` injected before the first `<script`, plus `/cheryl/api/feed/list`+`/live_list`+`/ack` (registered in main.py after `cheryl_clients`, distinct paths so no shadowing).

**★ GO-LIVE GATES (v1 code done, but NOT usable-by-Cheryl until):**
1. **DATA:** Cheryl's-cloud must populate `wsc.decisions.2026` with `questions[]`/`surfaces[]` or her 2 cards stay empty (0 items = correct, not a bug).
2. **★ SILO ENFORCEMENT:** the guard (`authz._role_allowed`: cheryl→/cheryl only) is code-correct but `AUTH_ENFORCE` is OFF (monitor mode) — a cheryl session STILL reaches `/owner` today. "Her login only reaches her screens" is FALSE until `AUTH_ENFORCE=1`. Pairs with [[project_workiz_retirement]]-era auth soak.
3. **HER LOGIN + OLD-ACCESS CLOSE:** DJ creates her real cheryl-role `res.partner` (or reconcile to one login with her Library identity). Minting a login does NOT revoke existing owner sessions (stateless 180-day HMAC, no revocation) — closing needs SESSION_SECRET rotation or logging out her devices. Also `_SECRET = SESSION_SECRET or ODOO_API_KEY or 'wsc-dev'` → set SESSION_SECRET explicitly (decouples from the Odoo key; rotating that key logs everyone out).

Concurrency (DJ-raised): the app runs a SINGLE uvicorn worker + `numInstances=1`, so feed.py's `threading.Lock` + `submit_item`'s add-by-id merge already serialize all card writes (both Operators write via `/api/feed/submit`). True CAS on the blob is only needed if the web service is ever scaled >1 worker/instance. See [[feedback_verify_limits_before_declaring]].
