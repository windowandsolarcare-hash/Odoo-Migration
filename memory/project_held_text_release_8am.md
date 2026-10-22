---
name: project_held_text_release_8am
description: "Overnight customer texts (held during 8pm-8am quiet hours) auto-release at the 8:00 AM allow-start via a DEDICATED server-side APScheduler job _scheduled_release_holds @ cron */5 (hits 8:00 sharp). Before 2026-10-22 the drain was piggybacked on the :26/:56 reminders tick so held texts went out ~8:26, never 8:00. A per-enqueue uuid nonce synthetic idem makes the drain/Send-now race at-most-once."
metadata:
  node_type: memory
  type: project
  modified: 2026-10-22T16:04:07.372Z
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
---

**The mechanism (messaging.py).** Customer SMS sent during quiet hours (after 8pm / before 8am PT, `QUIET_START_HOUR=8`/`QUIET_END_HOUR=20`, DST-aware `_PT = ZoneInfo('America/Los_Angeles')` in shared.py) are HELD, not sent: `send()` (messaging.py:~638) routes them to `_hold()` which appends to the Odoo param `wsc.msg.holdqueue`. They auto-release at the next 8:00 AM via `release_holds()` (messaging.py:228) — a no-op during quiet hours / empty queue, idempotent (each send re-checks the `already_sent` claim ledger). The HUD "🌙 N texts holding for morning" card promises "releases 8:00 AM PT".

**Root cause of the 2026-10-22 "didn't send at 8:00" report (DJ):** `release_holds()` had NO dedicated scheduler job — it was piggybacked inside `reminders_tick()` (reminders.py:2254), driven by `_scheduled_reminders` at cron `minute='26-59/30'` → fires only at :26 and :56. So the FIRST drain after the 8:00 quiet-end was **8:26, never 8:00**. (Verified from Render logs: the tick fired clean at 8:26:00; NOT a timezone bug, NOT a dead scheduler.) DJ saw texts still holding at ~8:25 and sent them manually.

**Fix (SHIPPED + verified live 2026-10-22):**
- **main.py** — new `_scheduled_release_holds()` job calling `owner_messaging.release_holds()`, registered in `build_scheduler()` at cron **`minute='*/5'`** (right after the `_scheduled_reminders` add_job line). `*/5` INCLUDES minute 0 → fires at 8:00:00 sharp; no-op before 8:00 (quiet). Kept the reminders_tick drain as a belt-and-suspenders backup. Commit dash `d0f70783`.
- **messaging.py `_hold()`** — stamp a per-enqueue synthetic idem `'hold:<norm>:<uuid4().hex[:8]>'` ONLY when the item has no real idem (confirmation-text idems preserved), AFTER `queued_at`, before `q.append`. Commit `240aabb1`. **Why:** `release_holds` and `hold_send_now` do an UNLOCKED read-modify-write on `wsc.msg.holdqueue`, and `send()`'s atomic `_claim_send` (PG) only guards when an idem is present — free-form texts had none, so a sub-second drain/Send-now overlap could double-text. Both paths now read `h.get('idem')` = the stamped nonce → `_claim_send` collides → at-most-once. A uuid NONCE (not a queued_at-derived key) is required: a `_now_iso()`-second-resolution key would collapse two distinct same-second same-number texts and SILENTLY DROP the 2nd (worse than a double). `_hold_key` returns the stamped idem so edit/cancel/send-now still address the item; pre-deploy held items (no stored idem) still send + stay addressable via `_hold_key`'s `to|queued_at` fallback.

**Verified:** log at 16:00:00 UTC 2026-10-22 shows `[scheduler:_scheduled_release_holds] lock acquired -> running` on one web instance + "lock held elsewhere -> standing by" on the others (the numInstances>=2 PG-advisory-lock singleton guard in `_sched_singleton`). 8:00-sharp confirmation is the organic next-morning log check.

**Test boundary (important):** you CANNOT headlessly stage a live drain test — `release_holds()` → `send()` → Twilio sends a REAL customer SMS. Do not inject a test hold against a real customer number to "prove" it; the at-most-once is closed by deterministic code + the idem claim; the authoritative live confirm is the organic 8:00 drain. See [[feedback_cant_headlessly_seed_is_security_feature]].

**Architecture note:** the scheduler runs IN-PROCESS on the web tier (`RUN_SCHEDULER` default-on, numInstances=2), NOT in a separate Render Background Worker — `worker.py` exists as the intended sole-scheduler owner but the zero-downtime STEP-2 flip was never done; no worker service is deployed. The `_sched_singleton` PG advisory lock (needs `MEMORY_DB_URL`, FAIL-CLOSED) keeps the 2 web instances from double-firing. §15: Audit plan-review → Lead firsthand confirm → Lead byte-QC → auto-deploy. See [[feedback_durable_watcher_not_session_cron]].
