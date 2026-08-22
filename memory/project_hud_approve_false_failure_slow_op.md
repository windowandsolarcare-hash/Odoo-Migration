---
name: project_hud_approve_false_failure_slow_op
description: "HUD approve cards falsely showed \"Launch failed — nothing sent\" on heavy/slow approvals (e.g. paywatch record) that actually SUCCEEDED — client 30s timeout aborted while the server finished. Fixed with re-check + 45s."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0e6fb90e-8d05-4272-91a3-ed7ee21488d7
  modified: 2026-08-07T03:29:35.159Z
---

**Bug (2026-08-06):** DJ tapped Approve on the John Bullock paywatch card ($330 Zelle, SO 17389) and got red **"Launch failed — nothing sent. Try again."** — but it had FULLY succeeded server-side (INV/2026/02527 posted+paid, job marked Done, next maintenance SO 17552 created ~3mo out). False failure.

**Root cause:** the paywatch Approve → `/owner/api/paywatch/record` → `_execute_payment` is a HEAVY chain of ~15-20 sequential Odoo RPCs (invoice create/force-deliverable/post + payment register + paid-in-full closeout: mark Done + snapshot roll-up + `create_next_maintenance_so` w/ line-item copy). DB commits spanned 03:18:00→03:18:17 but with Render↔Odoo per-call latency the wall-clock exceeded the HUD's **30s fetch timeout** (`jpost(...,30000)` in v2_hud.html `doApprove`). `jfetch` returns `null` on abort, and `doApprove` treated `!d` (null/unknown) the SAME as `d.ok===false` (definite fail) → showed "nothing sent" even though it went through. (No request log appears for an aborted request.)

**Fix (v2_hud.html doApprove):**
- Separated the null/unknown case from `ok===false`. On `ok===false` → real error message. On **null** → the outcome is UNKNOWN, not failed.
- Added `_cardCleared(id)`: re-GET `/owner/api/feed/list` — approve endpoints are idempotent and **delete their own card on success** (paywatch: `settle()` + `delete_item('paywatch:<so>')`), so if the card is gone server-side it went through → show ✅ + removeCard. Else → soft "Still working — it may have gone through. Pull to refresh to check before retrying."
- Bumped approve timeout 30s → 45s for headroom.
This is GENERIC — helps every approval card (incl. lead's HUD confirm/reminder cards). Safe because these approvals are idempotent (retry never double-charges; `_execute_payment` dedups on posted+paid, `create_next_maintenance_so` on the `wsc.maint.next_created.<so>` flag).

**Also:** fixed the paywatch card WORDING (specialist_paywatch.py `_submit_card`) — dropped the stale "then mark the job Done in Workiz as usual" line and the confusing `payer "memo"` (e.g. `Dawson Bullock "N/A"`); now: "Approve to record it. If it clears the balance, the job is auto marked paid in full + Done and the next visit is created — no other steps, no Workiz." See [[project_mark_done_refuses_workiz_uuid]].
