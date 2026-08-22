---
name: project_smart_confirm_detect
description: "Natural-language appointment confirmations now auto-mark confirmed. reminders.py handle_inbound: exact YES_WORDS fast-path, else a conservative AI check (_ai_is_confirmation, Haiku) — only runs when we're AWAITING a confirm from that number. sched/launch confirm now registers awaiting so TEXT replies (not just the page) get caught. DJ approved 2026-08-07 (Donna replied 'the 12th is good for me' and wasn't caught)."
metadata:
  node_type: memory
  type: project
  originSessionId: 1e80ea0d-78f5-4aa2-bc1d-25aace876ab5
  modified: 2026-08-08T15:29:41.308Z
---

**Trigger:** DJ manually confirmed Donna (SO 17383, Aug 12) — she'd replied **"Wed 8/12/26 at 10:00 am is good for me"** but stayed `confirmed:false` because the old detector only matched exact `YES_WORDS`. DJ: make it smart + he wants a confirmed indicator on the schedule.

## Confirmed flag + schedule indicator (already existed)
- Unified flag `CONFIRM_KEY = 'wsc.reminders.confirmed.<so_id>'` (ISO). `is_confirmed(so_id)`; `/api/sched/state` returns `confirmed`; Command Center `/api/sched/states` returns `confirmed[]`. The confirmed indicator renders from it — v2_command cards + **"✓ Confirmed by customer"** banner (v2_field). **(2026-08-07, DJ:)** the v2_command card indicator is now a **full-width green "✓ CONFIRMED" bar across the top of the card** (`.conf-bar`, jobCard `confBar`) — replaced the small easy-to-miss `<span class="b ok">` pill, since the pill got buried. Same `_CONF`/`/api/sched/states` data — so the "who's confirmed next week" view was already built; Donna just wasn't marked. Set it manually via `ir.config_parameter set_param wsc.reminders.confirmed.17383`.

## TWO-TIER card status (DJ 2026-08-07)
The schedule card now shows TWO levels: **maint heads-up "I'll be there"** (`reminders.appt_confirm` → `_maint_state_set(so,'ok')`, `wsc.maint.advance.<so>`) = a LIGHT **✓ Acknowledged** pill; the **4-day confirm** (`CONFIRM_KEY`) = the BOLD green **✓ CONFIRMED** bar. "Acknowledged" is internal-only until now (it gates who gets the 4-day confirm). Card side BUILT (v2_command.html: `_ACK` from `sched/states.acknowledged`, `.b.ack` pill when acked && !confirmed && !accepted; graceful). DATA one-liner speced to specialist: add `acknowledged:[so where maint state=='ok']` to `scheduler.py api_sched_states` (via `reminders._maint_states_batch`).

## Acknowledged now visible + settable on the JOB DETAIL (BUILT 2026-08-08)
DJ hit the gap on Bill Blane (SO 17243, **Nov 12** job): he'd replied "OK" (old-Workiz acknowledgement) and the backfill DID mark him (`wsc.maint.advance.17243 state=ok`), but DJ couldn't SEE it — the ✓ Acknowledged pill only lived on the **schedule card**, and a far-future (Nov) card isn't rendered until the job enters the visible scheduling window. Fix = surface acknowledged on the job detail (visible any time):
- **reminders.py:** `GET /api/maint/state?so_id=` → `{state, acknowledged:(state=='ok'), via, ts}`; `POST /api/maint/mark_ack {so_id,on}` → on=True reuses canonical `appt_confirm(so, source='manual')`, on=False rolls back to 'sent'. (Owner endpoints, no token, JSON body — match /api/maint/advance/send.)
- **v2_field.html (job detail):** mirrors the existing "✓ Mark confirmed"/`_confBan` pattern → a LIGHT `#ack-pill` "✓ Acknowledged" + a dashed `#mark-ack-btn` "✓ Mark acknowledged" (with a "clear" link on the pill). `loadAckState(soid)` (called in openJob next to `loadSchedState`) fetches /api/maint/state; `markAck(on)` posts mark_ack. Verified live: /api/maint/state?so_id=17243 → acknowledged:true.
- **v2_customers.html (Customer Brain job list, 2026-08-08 commit 3f5d3eb):** each NOT-done (upcoming) job row gets a `<span class="ackslot" data-so=>` placeholder; `loadAckPills()` (called after `d.innerHTML=html` in renderDossier) fetches /api/maint/state per slot and fills a light `.jpill.ack` "✓ Acknowledged" pill. One tiny call per upcoming job (customers usually 0-1). Done jobs never show it. Kept OFF dashboard.py (customer_jobs lives there — high-risk file) by using the existing endpoint from the frontend.

## CONFIRMED shown alongside ACKNOWLEDGED everywhere + Customer-Brain CARDS (DJ 2026-08-08, "same logic should apply here, add confirmed logic in same places")
Rule: a status pill appears ONLY if the customer has an OPEN (not-Done) job that's confirmed or acknowledged; once Done, nothing shows. Precedence **CONFIRMED (bold solid-green) > ACKNOWLEDGED (light green)**.
- **`/api/maint/state` now also returns `confirmed`** (reminders.py, `is_confirmed` + 'False'/'false' guard — CONFIRM_KEY values can literally be the string 'False'). commit b6d6c68.
- **v2_customers JOB ROWS:** `loadAckPills` now fills `.jpill.conf` "✓ Confirmed" if confirmed else `.jpill.ack` "✓ Acknowledged".
- **v2_customers CUSTOMER CARDS (search results):** `custCard` renders a `.chip.conf`/`.chip.okc` pill from `c.next_confirmed`/`c.next_ack`. commit 69aa8da.
- **`/api/search` (dashboard.py) enriched:** in the existing next_by loop I capture `next_so_by[cid]=so.id`; after the loop, TWO batched `ir.config_parameter search_read` (keys `wsc.reminders.confirmed.<so>` + `wsc.maint.advance.<so>` for all next-job so_ids) → sets `p['next_confirmed']`/`p['next_ack']`. Never per-partner. SKIP set already excludes done/canceled so "next" is always an open job. commit 0742f17 (guarded: +30 lines, freshly based on live 13672).
- **Job detail (v2_field.html)** already had the confirmed banner (`_confBan`) + my ack pill — no change needed.
Verified live: /api/maint/state?so_id=17243 → confirmed:false,acknowledged:true; /api/search?q=Bill Blane → next_ack:true,next_confirmed:false.

## WZ (Workiz) pills removed everywhere (DJ 2026-08-08)
Workiz retired → the "WZ" link pills are dead. Removed from 5 files (7 spots in field.html incl. a `t.workiz_link` "WZ <uuid>" variant, +v2_customers/v2_field/v2_reactivation/v2_stats). Left the `data-workiz` menu attrs + `🔄 Sync from Workiz` buttons (not WZ pills; ask before touching). Commits d0c07f4/6f0737b/103fb56/7a6f653/2b99b0c. node --check passed all; field.html −8 lines (4 collapsed wzPill blocks).
- **Live-handler gap FIXED (DJ approved 2026-08-08):** `_maint_handle_inbound` used to catch a reply as acknowledgement ONLY when the number was still in `_maint_awaiting()`. Bill's "OK" came **23 days** after the heads-up → awaiting expired → not auto-caught (the backfill caught it, not the live handler). Now when there's no awaiting record it falls through to **`_maint_late_ack`**: a CLEAN short bare ack (in YES_WORDS / _YES_STARTS / 'sounds good'/'that works'/'thank'/👍👌🙏, ≤4 words, no '?', no reschedule/cancel word) + the customer has an upcoming job with maint state 'sent' (`_find_pending_maint_so` = child_of partner, date_order≥today, first state=='sent') → `appt_confirm(source='text')` + friendly reply (idem maint_advance_ack:<so>). Anything not a clean ack falls through to the inbox untouched. Low harm since ack no longer gates the 4-day confirm; DJ has a 'clear' link on the job-detail pill. Commit 0a421f8.

## Smart detection (BUILT 2026-08-07, reminders.py)
- **`handle_inbound`** only evaluates a reply as a confirm when the number is in `_awaiting()` (PENDING_KEY, set by `_mark_awaiting` when we send a confirm). Upgraded the YES check: `is_yes = text in YES_WORDS`; **if not, `is_yes = _ai_is_confirmation(body)`**.
- **`_ai_is_confirmation(body)`** — Haiku (`get_anthropic_client`, `CLAUDE_HAIKU` from `.shared`), 4-token YES/NO. CONSERVATIVE: True only on a clear accept ("that works", "the 12th is good for me", "see you then"); reschedule/cancel/question/unrelated → NO; **any error → False (never false-confirm)**. Runs ONLY when awaiting (not on random inbound). Adds ~1-2s to that inbound only.
- **`/api/sched/launch` confirm mode** now calls `_mark_awaiting(phone, so_id, ...)` after a successful send — previously a manual/reschedule confirm sent via sched/launch did NOT register awaiting, so a TEXT reply (vs the ?c=1 page) was never evaluated. THAT was Donna's actual gap. (The reminders BATCH confirm already marked awaiting at L358.)
- Maintenance Stage-1 replies (`_maint_handle_inbound`, MAINT_CONFIRM_KEY) still use exact YES only — could get the same AI upgrade later.

## PENDING (#2, mailed to specialist)
Manual **"Mark confirmed"** tap for the rare reply the AI leaves unsure — belongs next to the specialist's ✓ Confirmed banner (v2_field) / inbox thread; sets the same CONFIRM_KEY. Coordinated via AGENT_MAIL. See [[project_auto_confirm_branded_page]] [[project_sched_lifecycle_one_page]].
