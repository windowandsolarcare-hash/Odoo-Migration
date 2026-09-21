---
name: project_scheduling_spacing_and_windows
description: "Scheduling #1–3 (2026-09-21). #1 = interval-based slot spacing by prior job's real length + 20min drive + 15min buffer (build_day_plan hard-filter for customers; slot_offers soft-⚠ for manual). #2 = customer sees a ~2hr WINDOW (display only, date_order stays exact start). #3 = Command Center shows the exact start–end block (already done via _len_end)."
metadata: 
  node_type: memory
  type: project
  originSessionId: 11d2c5cb-9040-46fe-b04b-20ac84f0828f
  modified: 2026-09-21T15:18:43.634Z
---

**Scheduling #1–3 (2026-09-21, Lead-QC'd, DJ-approved forks).** DJ's 4 scheduling reqs; #4 (day-off exclusion) is [[project_day_off_two_representations]]. #1–3:

## Duration source (reliable — no fork)
A job's length = `int(x_job_length_min) or _job_block_min(job_type)`. `_job_block_min` (scheduler.py) defaults: personal-time 0, combo 120, gutter 60, touch/quote 30, windows·solar·default **90**. `SLOT_MIN=90` (booking.py) == the default (a typical job).

## #1 — interval spacing (commit be346eae scheduler + cee0860d slot_offers)
Root cause of unreachable-slot offers (Andy/Jeff: Jeff 8:00×90m → 9:30 offered though drive made it unreachable): the old `booking._free_slots` used a COARSE fixed 90-min grid + "does any job START in this bucket" — ignored a prior job's real length spilling over AND drive time.
- **Constants (scheduler.py, DJ-approved):** `DESERT_DRIVE_MIN=20` (flat desert-wide v1; distance-based later), `SLOT_BUFFER_MIN=15`.
- **`build_day_plan` (customer-facing AUTO path → HARD filter):** `occupied` now carries `(start, length)`; a grid start is reachable only if for every job it's NOT in `[ostart, ostart+olen+20+15)` (arrive-after-prior) AND the job isn't in `[s, s+SLOT_MIN+20+15)` (finish-before-next; SLOT_MIN=90 proxy for the new job's unknown length — == typical job, so no underestimate). Feeds so-suggest/city-suggest/reactivation/new_job via rank_days → all inherit the hard filter. (Verified: Jeff 8:00×90 blocks 8:00 AND 9:30, block=8:00–10:05, 11:00 open.)
- **`_job_fits_at` (known-length validation):** adds the 20+15 gap ("too tight (needs 35m drive+buffer)" vs raw "overlaps").
- **`slot_offers` MANUAL offer/reserve → SOFT-⚠ (fork 3):** `_slot_spacing_warnings(slots, so_id)` resolves the SO's real length + runs `_job_fits_at`; `/api/offers/record` + `/reserve` return `tight`/`tight_warning` but NEVER drop — DJ overrides. (Layered ON TOP of #4's hard day-off drop, which still drops.)

## #2/#3 — one slot, two views (NO new fields; commit 225f3edf booking)
The SO stores date_order = the EXACT start (= the window's start) + x_job_length_min = length. NEVER store a window range.
- **#2 CUSTOMER = ~2hr WINDOW (display derivation):** the branded offer page `_OFFER_HTML.fmt()` renders each slot as `[start, start+120]` → "Thursday, October 8 · 9:30–11:30 AM" (same-meridiem drops the redundant start AM/PM; nbsp before AM/PM so it never wraps). Booking a slot still posts the exact START. The general booking page already used Morning/Afternoon windows + api_times a 2hr range.
- **#3 INTERNAL Command Center = EXACT block (already done):** `dashboard._len_end(date_order, x_job_length_min, job_type)` → (length_min, end_label, is_estimate), returned as `end`/`length_min` on the schedule/command endpoints. UI already renders start–end: `v2_field.html:953` (`t+' – '+job.end`) and `v2_command.html:642` (Command Center `j.time+' – '+j.end`). No change needed.

## Offer-reply TEMPLATE (in-flight, separate)
offers/send relayed a caller-supplied body (drift + one mis-signed "DJ"; DJ is "Dan" to customers). Building a FIXED template (mirror reminders/maint voice: "Hi {first}, it's Dan with Window & Solar Care … – Dan", tap-to-book, carries reserved time+link) — NOT an AI drafter. Pending DJ's one-tap WORD sign-off (customer-facing wording is his call). {time} = the #2 window. Related: [[feedback_dj_operating_instincts]] (2 quote types, warm/one-push, tap-to-book), [[feedback_reuse_canonical_endpoint]].
