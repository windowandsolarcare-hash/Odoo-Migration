---
name: project_two_night_before_reminder_tracks
description: "reminders.py has TWO parallel night-before builders with near-identical titles; the maintenance one (gated on maint advance ok/sent, honoring backfilled ok) can surface INSTEAD of the plain one and silently drop regular confirmed jobs."
metadata: 
  node_type: memory
  type: project
  originSessionId: 62c57f62-79c0-4d47-9f2b-7e07e9e7d677
  modified: 2026-09-03T13:54:33.063Z
---

`routers/owner/reminders.py` has **two separate "Night-before reminder" builders** that can both produce HUD cards with near-identical titles:
1. **Plain eve** — `build_batch('eve')` → card id `reminders:eve:<date>` (title "Night-before reminders to send"), page `v2_reminders.html`. Includes **every** job dated tomorrow with `state in ('sale','done')`, valid phone, not DNC/STOP/already-sent. Message = `_eve_body()` ("just a quick reminder about our appointment tomorrow").
2. **Maintenance eve** — `_maint_stage_rows('eve')` → card id `maint_eve:review` (title "Night-before reminders"), page `v2_maint_comms.html?stage=eve`. Includes ONLY jobs whose maintenance advance state is `ok`/`sent` (line ~1152-1154). Message = `MAINT_EVE_CONFIRMED`/`MAINT_EVE_UNCONF` ("…for your service. If there's a gate code…").

**The bug (found 2026-09-02, Gayle-but-not-Fred):** the MAINTENANCE card surfaced and the plain one didn't, so a regular **confirmed** job (Fred Johns 004749/17350, state sale, 8am tomorrow) was dropped while Gayle Ormond (004770/17369) showed. Gayle only qualified because her advance state was `{"state":"ok","backfill":true}` from the 2026-08-08 backfill — and the maint eve gate does NOT strip backfilled states, even though `_maint_pending_rows` (line ~673) explicitly ignores `backfill` as "not evidence we contacted anyone." So the backfilled customer surfaced and the truly-confirmed one didn't.

**Tell (which card you're on):** the MAINT card's message contains "for your service. If there's a gate code"; the plain card's says "just a quick reminder about our appointment tomorrow. See you then!"

**Fix handed to Specialists 2026-09-03:** `3_Documentation/NIGHT_BEFORE_FIX_BRIEF.md` — unify to ONE night-before card covering every scheduled job tomorrow (plain-eve population, message branches maint/regular + confirmed/not); make the maint stage ignore backfilled `ok` like `_maint_pending_rows`; investigate why `reminders:eve:<date>` wasn't in `wsc.feed.items` though its batch was live. **Also a feature:** send the reminder (editable body) from JOB DETAIL — reuse `send_batch(only_so_ids=[so_id])` / `send_maint_stage(stage, so_id)` / `send_maint_advance(so_id, body=)`, mirror the "Send acknowledgement" box.

**Related:** the reminder message IS editable per-person on the review page (`v2_reminders.html` renders an editable `<textarea class="body">`). Feed items live in `ir.config_parameter` key `wsc.feed.items`; reminder batches in `wsc.reminders.batch.<kind>-<date>`; maint advance state in `wsc.maint.advance.<so_id>`. See [[feedback_reuse_canonical_endpoint]].
