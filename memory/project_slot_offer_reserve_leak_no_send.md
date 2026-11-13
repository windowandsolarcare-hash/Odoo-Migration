---
name: project_slot_offer_reserve_leak_no_send
description: "Stray wsc.slot_offers holds — the ONLY owner action that writes one, and how a hold survives with no text sent"
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-11-13T08:24:33.796Z
---

Traced 2026-11-12 (DJ flagged 2 stray holds today: Greg Chevalier SO 17457 confirmed-for-today, Larry & Teresa Ballinger SO 17490 postponed — both reserved future dates with NO customer text; DJ: "getting placed without my knowledge"). Both cleared by Operator; bug confirmed look-only, fix held for DJ.

**★ FIXED 2026-11-13 — "fix A" shipped (Lead byte-QC GREEN, DJ greenlit). commits wsc_offerbox a429308d / slot_offers 32da54a0 / ENDPOINT_MAP f4376ff3.** Lead ruled A-now + server guard, B (reserve-at-send) data-gated. What shipped:
- `wsc_offerbox.js`: the hold is now freed on EVERY box abandonment, not just the "Don't send" button — refactored the clear into one `abandon()` reused by the backdrop tap + "Don't send"; plus a `pagehide` (persisted===false) `sendBeacon('/owner/api/offers/clear')` for true unload/navigate. **`visibilitychange` is deliberately NOT wired** (Lead req #3): a screen-sleep/app-background KEEPS the hold so DJ can glance away and return to the still-open box and tap Send. Committing to Send nulls `_active` first so a mid-send unload can't free it. Hard-kill-mid-box tail → 48h expiry backstop.
- `slot_offers.py`: server **confirmed-today guard** `_so_scheduled_today(so_id)` (state sale/done AND date_order today PT) → `/api/offers/reserve` + `/api/offers/record` early-return `{ok:false, guard:'scheduled_today'}` before any record (fail-open on error). **B-data-trigger:** `_annotate_expired_leak` in `_expire_inplace` flags offers that hit 48h expiry never-sent (`o['expired_unsent']`), surfaced by read-only owner-walled **`GET /owner/api/offers/leak_stats`** (returns {expired_total, expired_unsent, leaked_offer_ids}). If leak_stats stays ~0, B stays deferred; if material, promote reserve-at-send (fix B). record_offer + /api/offers/send were NOT touched.
- Known non-blocking residual (Lead-noted, not fixed): opening a 2nd offer box over an unsent 1st orphans the 1st hold (`_active` overwritten) — near-unreachable (fullscreen overlay), caught by 48h + leak counter.

**The ONE owner path that writes a `wsc.slot_offers` hold:** the "📌 Offer 2-3 times instead of booking one" toggle inside a job's RESCHEDULE sheet (route_map.js `WSCDayPlan`, enabled wherever the host passes `cfg.offer={partner_id,so_id,name}` — `_job_detail_panel.js:83`, `v2_command.html:1405`). Flow: toggle on → tap slots (`OFFER.picks`) → tap blue **"📤 Send these N times"** (`_doReserve`, route_map.js:247) → `POST /owner/api/offers/reserve` → `slot_offers.record_offer` **writes the hold (48h pending) immediately**, mints the `/c/<token>` link, THEN opens `WSCOfferBox`. The actual text is a SECOND tap ("📤 Send offer" → `/owner/api/offers/send`) inside that box.

**Why holds land with no text (the leak):** reserve and send are decoupled, and the hold is rolled back ONLY by the box's "Don't send" button (`wsc_offerbox.js:75` → `/api/offers/clear`). Any OTHER dismissal leaves the hold live 48h with no text and no signal:
- backdrop tap closes the box without clearing (`wsc_offerbox.js:56` `if(e.target===ov) ov.remove()` — no clear_offer),
- screen sleep / refresh / app-background / navigate-away after the reserve committed.
(The 2026-09-02 "Don't send frees them" fix only covers that one button; `get_offer` re-mint + v2_waiting "free them on Waiting" exist because the survival path was known but not closed.) Button label "Send these N times" is a misnomer — it reserves-then-previews.

**No guard on an already-confirmed job:** the offer toggle shows on EVERY reschedule sheet regardless of state — incl. Greg's job confirmed for today. Offering future dates to move a today-job silently ate capacity (pushed Mira's booking page to Dec 4).

**CLEAN actions that do NOT write a hold (verified) — DJ can use freely:**
- **Postpone** (`/api/postpone_job`, `/api/inbox/postpone`, `park_tickle`) → only `postpone_odoo_so` flips status to Postponed. No hold.
- **"Send booking link"** (inbox menu → `inboxIntent('booking')` → `/api/inbox/intent` intent=booking, sms.py:3901) → mints a plain `make_token(pid)` self-book link as a DRAFT into the reply box. No offer_id, no slots, NO hold.
- **"Confirm the appointment"** → `sched/launch` mode=confirm, self-schedule link. No hold.
NOTE the customer-text-driven reserve chain (sms.py:2120-2162, inbound "reschedule" reply → auto-offer) also calls `record_offer`, but that's not a button DJ presses.

**Recommended fix (DJ's go — customer-scheduling-capacity, ships via DJ review):** move the reserve to the moment of SEND (reserve inside WSCOfferBox's send handler, not in `_doReserve`) — one change kills the whole leak class (backdrop/sleep/refresh all become harmless) AND makes the button name honest. Secondary: guard the toggle off on a job already confirmed/scheduled for today. See [[project_slot_offers_reserve_design]], SLOT_OFFERS_CONTRACT.md, [[feedback_no_ai_offered_dates_use_link]].
