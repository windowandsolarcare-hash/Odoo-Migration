---
name: project_scheduling_spacing_and_windows
description: "Scheduling #1–3 (2026-09-21). #1 = interval-based slot spacing by prior job's real length + 20min drive + 15min buffer (build_day_plan hard-filter for customers; slot_offers soft-⚠ for manual). #2 = customer sees a ~2hr WINDOW (display only, date_order stays exact start). #3 = Command Center shows the exact start–end block (already done via _len_end)."
metadata: 
  node_type: memory
  type: project
  originSessionId: 11d2c5cb-9040-46fe-b04b-20ac84f0828f
  modified: 2026-09-21T15:44:32.142Z
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

## Offer-reply TEMPLATE (DONE + LIVE, commit 9b574a9d, DJ-word-approved)
The bug was drift + one mis-signed "DJ": the offer send-box prefilled a CLIENT-side `defaultBody` in wsc_offerbox.js ("Hi {first}! Here are a couple of times…", no "Dan"), DJ edited it (+ AI-reword) and sent it. So the fix is at the PREFILL, not the send:
- **`slot_offers._offer_reply_body(offer)`** = the canonical fixed template (mirrors reminders/maint voice): "Hi {first}, it's Dan with Window & Solar Care. I've got {day} at {time} open for your {service} — tap here to lock it in: {link}  – Dan" (several-slots: "a couple of openings for your {service} … grab whichever works best"). `_slot_day_window(iso)` → "Tuesday the 29th" + the #2 2hr window. `_friendly_service(job_type)` = keyword-map of x_studio_x_studio_x_studio_job_type → friendly phrase (solar→solar panel cleaning, window/commercial→window cleaning, gutter→gutter cleaning, pressure→pressure washing, screen→screen service, quote/estimate→estimate, touch→touch-up, cobweb→cobweb cleaning) with a REQUIRED fallback → "service" (missing/unknown NEVER leaks a raw code).
- **PREFILL:** `/api/offers/reserve` + `/api/offers/get` now return `body`=_offer_reply_body; `route_map.js` forwards `body:d.body` into `WSCOfferBox.open`; the box's `opts.body` (server) is primary; `defaultBody` is now an on-brand "Dan" LAST-RESORT only.
- **★ GUARDED, not strict:** DJ REVIEWS-THEN-SENDS + uses AI-reword, so `/api/offers/send` PREFERS the edited body: `body = (data.get('body') or '').strip() or _offer_reply_body(offer)` — his edit wins; a no-body send still gets the template. (An earlier commit 6d4e5382 made the generator PRIMARY = overrode his edits = a regression; corrected in 9b574a9d.) Rule-9 catch: found the deliberate edit path BEFORE shipping strict-template. messaging.send guards (idempotency/quiet-hours/DNC) unchanged.

## Timeline READ-cache (commit 68a5d1b3) — same pattern as inbox #5
`reactivation.api_outreach_timeline` did 4 UNCACHED Odoo RPCs/open (mail.message×120 + task + lead + partner) = phone-felt slowness. Added `_TL_CACHE` (per parent-pid, `_TL_TTL=100s`) — miss assembles+stores the payload, HIT returns it (0 RPCs). **TTL is PRIMARY freshness** (some outreach markers written by Odoo-side automations OUTSIDE the app), plus `_tl_invalidate(pid)` on the 2 in-app writes (api_outreach_log + api_touch) for immediacy. READ-only wrap (assemble/markers/content untouched → cached==uncached by construction). See [[project_inbox_summary_readmodel_a5]] (same TTL/invalidate read-cache idiom).

Related: [[feedback_dj_operating_instincts]] (warm/one-push, tap-to-book, review-then-send), [[feedback_reuse_canonical_endpoint]], [[feedback_question_when_big_picture_wrong]] (the prefill-vs-send-endpoint catch).
