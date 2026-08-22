---
name: project_request_confirm_flow
description: "AGREED 3-state flow (DJ 2026-08-07) for a customer who picks their own day on the ?c=1 confirm page: REQUESTED='we'll confirm the exact time' (never 'all set') → DJ Accepts + sets exact time + presses 'Launch Confirmation' (explicit, not auto) → CONFIRMED='You're all set'. Customer picks morning/afternoon window only; DJ sets the exact time by route. Speced to specialist; not yet coded."
metadata:
  node_type: memory
  type: project
  originSessionId: 1e80ea0d-78f5-4aa2-bc1d-25aace876ab5
  modified: 2026-08-08T14:19:54.073Z
---

**STATUS 2026-08-07: CODED by specialist (deployed).** State-1 ctx bug fixed (`sched_ctx` splits `accepted` vs new `requested` flag; page render has a requested branch = "Thanks, we've got your request for <day, window>. We'll confirm the exact time shortly." + stacked sig; "You're all set" is state-3 only). State-2 "Launch Confirmation" = the confirm send box's send button is now labeled **📤 Launch Confirmation** (v2_field _openSendBox + wsc_sendbox.js); NOT auto-send. Flow variance: the `sched_req` HUD card is a **📅 Set the time** action that opens the day-planner ON the requested day (= "Accept his day + set time" in one motion) rather than a separate "✓ Accept his day" tap — one fewer tap, same 3 states. #1 (window) + #3 (📍 pin/available) already shipped. See [[project_sched_page_window_and_fit]].

**DJ walked the Ed Dismukes (SO 17555) flow live and locked the wording.** The confirm text says "…tap here to confirm, or let me know if you need to reschedule: <link>". The link is NOT confirm-only — it opens the branded ?c=1 page with 3 options (confirm · pick from open days · pick own day), so tapping it IS a valid reschedule path. DJ's confusion earlier = he opened Ed's link AFTER Ed had already picked, so he saw the "all set" state, not the deciding menu. **One link = all options; original text is fine.**

## The agreed 3-STATE model (customer picks their own day)
1. **REQUESTED** (customer chose a day + morning/afternoon window; pending DJ): page/ack = **"Thanks — we've got your request for <day, morning/afternoon>. We'll confirm the exact time shortly. – Dan."** Drops a `sched_req:<so_id>` HUD card. ★ **BUG:** `booking.py` sched ctx returns `accepted:true` for BOTH `requested` AND `accepted` (~L720), so re-opening a REQUESTED link wrongly shows **"You're all set"** before DJ set a time/okayed it. Fix: requested → the "we'll confirm" state, never "all set".
2. **DJ ACCEPTS + SETS TIME + LAUNCHES:** tap **✓ Accept his day** on the card → reschedule to requested day → DJ sets the EXACT time (route; customer only picked a window) → presses an explicit **"Launch Confirmation"** button → THAT sends the confirm text with the exact time. **NOT auto-send** (DJ wants the explicit button; reuse WSCSendBox confirm send). The 2nd confirm is NOT redundant — customer gave a window, DJ confirms the exact time.
3. **CONFIRMED** (customer taps option 1): page = **"You're all set — <day, exact time>. See you then!"** ONLY this state says "all set".

## The 3 page taps → which endpoint / state / chatter (verified in booking.py 2026-08-08)
The branded sched page (`_SCHED_HTML`) has THREE buttons, and "Accepted" is NOT "the customer built their own appointment":
- **b1 "That works ✓"** → `confirmProposed()` → POST `/api/sched/confirm` with **token only, NO date/time**. Books the slot ALREADY on the SO (`c['time']` = the time DJ set). Sets `wsc.sched.<so> state=accepted` AND `wsc.reminders.confirmed.<so>` (a page tap IS a confirm, like YES). **This is the common case** — customer just accepts DJ's proposed day+time; he did NOT pick the clock time.
- **b2 "give me the next available date"** → `showDays()` (up to 3 route-tight suggestions, 📍 pin on fit day) → tapping one → POST `/api/sched/confirm` **WITH date+time**. Same accepted+confirmed state, but a DIFFERENT day than proposed.
- **b3 "I have a particular day"** → `showPick()` (date + Morning/Afternoon/No preference) → POST `/api/sched/request` → state `requested` (NOT accepted, NOT confirmed) + drops the `sched_req:<so>` HUD card for DJ.
**Distinct chatter logging (added 2026-08-08, commit 30dce29):** `sched_confirm` branches on `body.get('date')` → b1 logs **"✅ Customer confirmed the time we offered: {slot}"**, b2 logs **"✅ Customer picked a different day we offered: {slot}"** (was one ambiguous "✅ Customer self-scheduled" for both). b3 already logged "📅 Customer REQUESTED …". Origin: DJ realized Henry Salvidor (SO 17230) only tapped b1 to accept DJ's 9:30 slot, but the old log made it read like Henry self-scheduled.

## Card precedence: CONFIRMED bar WINS over Accepted pill (DJ approved 2026-08-08, mailed to specialist)
Because b1/b2 set BOTH accepted state and the confirmed flag, a self-scheduled job is genuinely CONFIRMED. DJ wants the bold green **✓ CONFIRMED** bar to win over the light **✓ Accepted** pill on the v2_command card. Precedence: **CONFIRMED bar > Accepted pill > Acknowledged pill**. Render change is specialist's (v2_command jobCard) — data already present in `/api/sched/states` (`confirmed[]` + `accepted`/`acknowledged`).

## Decision: confirmed-screen self-service = NO
Once confirmed, the link shows "You're all set" with no reschedule option = a dead end. DJ chose to LEAVE it (rare case; customer just texts to change → the smart inbox surfaces it as a reschedule HUD card). Building self-service reschedule-after-confirm = too much machinery for the edge case.

## Related fixes speced same day (all specialist's booking.py + scheduling card)
#1 confirm page "pick your own" → **Morning/Afternoon/No preference**, not an exact `<input type=time value=09:00>` (Ed's "9:00" was just the default). #2 one-tap **✓ Accept his day** card (was "Open job" only). #3 confirm day list (`showDays`) → **📍 "I'll already be in your area"** pin on route-tight day + "available" on others (route-tight sort in `_open_dates_for_city` already returns a `fit` flag; main /book page shows it, sched page doesn't). See [[project_sched_lifecycle_one_page]] [[project_auto_confirm_branded_page]].

## Review-request screen: exact-time picker was hidden by a display bug (fixed 2026-08-08)
DJ on the **Review request** page (v2_booking.html — DJ approves a customer's self-requested day, sets the exact time by route): "it should allow me to pick time exactly." The exact-time UI ALREADY existed — a `#time-edit` block with `<input id="t-start" type="time">`/`t-end`, and `approve()` already POSTs `{start:t-start.value,...}`. BUG: `pickSlot()` revealed it with `$('time-edit').style.display=''` — but the stylesheet has `#time-edit{display:none}`, and setting `.style.display=''` only CLEARS the inline style, so it fell straight back to CSS `none`. So the Start/End inputs were NEVER visible; DJ was stuck with the one suggested 1.5h slot. Fix = `style.display='block'` (commit 353863b) + a "Set the exact start time" label above the inputs. Lesson: to un-hide an element whose CSS default is `display:none`, set an explicit `'block'`/`'flex'`, never `''`. Inputs were mobile-safe already (no appearance:none; same pattern as the working `#d-date` picker). See [[feedback_ios_date_input_appearance]].
