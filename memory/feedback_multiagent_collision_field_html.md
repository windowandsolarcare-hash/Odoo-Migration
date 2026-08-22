---
name: feedback_multiagent_collision_field_html
description: Real multi-agent collision — the line-count guard does NOT catch small silent drops; re-fetch live IMMEDIATELY before every push
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 3580ea04-ae9d-4fab-b3d1-3026be80528c
  modified: 2026-08-07T23:21:10.597Z
---

**On 2026-07-01 two agents edited static/owner/field.html concurrently and one silently overwrote the other.** Agent A pushed the card wrapper (`ap-card ap-card--nav`) around the "Navigate to Next Address" button at 15:02 (commit eb1b5d9). My length-picker push landed 2 min later at 15:04 (060d0f9), based on a fetch from BEFORE 15:02 — it reverted the card. DJ noticed the button no longer matched the "Navigate to Address" card and asked to investigate. Restored 2026-07-01 (commit 7586fec).

**Why:** the regression guard only compares LINE COUNT / bytes. My push was net-LARGER (it added the length picker), so a 3-line card wrapper going missing didn't trip it. Silent drops that are smaller than your additions are invisible to the size check.

**How to apply:** (1) Re-fetch the LIVE file with `gh api .../contents/<path>` IMMEDIATELY before editing+pushing — not at the top of a long multi-step task (the window between fetch and push is where a collision lands; my fetch was minutes stale). (2) When another agent may be active, treat every push as a potential race: fetch → edit → push in the tightest possible window, per file. (3) The size guard is necessary but NOT sufficient — it misses small silent reverts. After a big multi-file session, a `git`/commit-history sweep (per-commit +add/-del stats via `gh api repos/.../commits/<sha>`) reveals collisions: look for a commit with deletions that its message doesn't explain, especially two near-simultaneous commits to the same file. Reinforces the existing CLAUDE.md "FETCH THE LIVE FILE FIRST" gate.

**RECURRED 2026-08-07 on `routers/owner/reminders.py`** — a specialist reminders.py push (mark_confirmed / approve_request) used a local copy from BEFORE the lead's 2026-08-06 branded-auto-confirm commit → silently reverted `_confirm_page_body` + `build_batch('confirm')`/maint Stage 1 back to "reply YES" + dropped `_maint_confirmed_batch`'s CONFIRM_KEY reconciliation. DJ caught it live ("I thought we were into buttons only"). Lead re-applied all four. **`reminders.py` is THE most-collided file (both sessions edit it constantly) — after field.html/v2_field.html.** STANDING HANDSHAKE (both agreed): re-fetch reminders.py live immediately before ANY edit + diff before push, AND post "grabbing reminders.py" in AGENT_MAIL before touching it so the other session holds. Same applies to any hot shared file (field.html, v2_field.html, dashboard.py, sms.py, scheduler.py).
