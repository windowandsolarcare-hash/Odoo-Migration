---
name: project_sched_lifecycle_one_page
description: Scheduling lifecycle = ONE branded page for schedule AND confirm (?c=1 flavor). Page-accept + YES set the confirmed flag; reschedule clears it; 2-week reschedule branch; confirmed banners/badges.
metadata: 
  node_type: memory
  type: project
  originSessionId: 0e6fb90e-8d05-4272-91a3-ed7ee21488d7
  modified: 2026-08-07T21:00:50.345Z
---

The customer scheduling→confirm→remind lifecycle was unified 2026-08-06 (DJ). Diagram: https://claude.ai/code/artifact/c0667cb1-8aa1-4203-aad6-8774ab787c42

**ONE branded page, two moments.** `_SCHED_HTML` in `routers/booking.py` (served `/book/sched/{token}`) is the SAME page for both first-propose (schedule) and lock-in (confirm). It reads `?c=1` (`var CM=/[?&]c=1(&|$)/.test(location.search)`) → confirmation wording: lead "We have you on the schedule for:", button1 "Yes, I'll be there ✓", button2 "I need to reschedule…". WITHOUT `?c=1` it's the schedule flavor ("Your next service is proposed for:", "That works ✓"). **All 3 options are present in BOTH flavors** — confirm is never a dead-end; they can still reschedule/pick from the confirm page.

**Confirmed flag** = ir.config_parameter `wsc.reminders.confirmed.<so_id>` (CONFIRM_KEY in reminders.py, `is_confirmed(so_id)`). Set when: (a) customer replies YES **or a natural-language confirm** — lead added `_ai_is_confirmation` (conservative Haiku) in `handle_inbound`, only when `_mark_awaiting` is set for that number; (b) books through the branded page (`booking.py /api/sched/confirm`); or (c) DJ taps **"✓ Mark confirmed"** manually. The 4-day auto-confirm skips anyone with this flag. NOTE (lead 2026-08-07): `/api/sched/launch` confirm mode now calls `_mark_awaiting` after send, so a TEXT reply (not just the ?c=1 page tap) gets evaluated — that was the real Donna gap ("the 12th is good for me" stayed unconfirmed before).
- **Manual override:** `POST /owner/api/sched/mark_confirmed {so_id}` (reminders.py) sets the flag + chatter note. UI = dashed "✓ Mark confirmed" tap under the ✓Confirmed banner in v2_field (shown only when NOT already confirmed; hidden on confirmed/accepted/requested via `_confBan` + a default-hide in `loadSchedState`). For the rare reply the AI leaves unsure.

**Reschedule un-confirms.** `scheduler.py /api/schedule/reschedule` clears BOTH `wsc.reminders.confirmed.<so_id>` and `wsc.sched.<so_id>` on success (a confirmation is for a specific appointment). Belt-and-suspenders: `reminders.py /api/sched/state` also clears both on a day-change mismatch. NOTE: the YES-reply handler stores the flag with NO date binding — reschedule-clear covers the main path; lead may add a date_key there later.

**Endpoints:**
- `reminders.py /api/sched/launch` — `mode` param. `mode='confirm'` → link `+?c=1`, confirm text, kind=`confirm_offer`, idem=`confirm:<so>:<day>`. Default `mode='schedule'` (AI-worded via ai_sched_message).
- `reminders.py /api/sched/state?so_id=` → returns `{state, when, confirmed}`.
- `scheduler.py /api/sched/states` (bulk, Command Center) → returns `{states:{}, confirmed:[so_ids]}`.

**UI:**
- `v2_field.html`: the OLD plain "📅 Send confirmation" (sendApptConfirm → /api/schedule/send_confirm, plain text) was retired. TWO buttons now: "📅 Send scheduling options" → `schedLaunch('schedule')` (branded pick-a-time page) AND "✅ Send confirmation" → `schedLaunch('confirm')` (branded ?c=1 confirm page, on-demand, no reschedule needed — added 2026-08-06 after DJ hit the gap with Donna; lead flagged it). Manual confirm button is EXPLICIT confirm (not date-smart); the `_dOut>14?'schedule':'confirm'` 2-week auto-choice only applies to the post-reschedule auto-open. Orphaned `_openApptConfirm`/`/api/schedule/send_confirm` remain unused (slated for wsc_sendbox.js consolidation). **Nothing SENDS on its own** — every send goes through DJ's preview box where he taps Send. After a reschedule, `submitJobRs` AUTO-OPENS the preview box (DJ is fine with the popup). **Mode = ALWAYS 'confirm'** (2026-08-07): DJ just SET a specific day+time in the planner, so the follow-up confirms THAT exact time at any distance — NOT a "pick your own day" scheduling link. (Reverted the earlier `_dOut>14?'schedule':'confirm'` 2-week cutoff — it sent Ed a pick-a-day link at 18 days out when DJ had already set 8am. DJ: "should be confirmation — I already picked 8am.") The "pick your own day" scheduling page is the SEPARATE deliberate blue button "📅 Send scheduling options". Applies to BOTH v2_field submitJobRs and specialist_reschedule submitJobRs (→ WSCSendBox mode:'confirm'). Green "✓ Confirmed by customer" banner via `_confBan()` reading `/api/sched/state.confirmed`.
- **Send-preview box** = `_openSendBox` (shared composer). Redesigned to a branded PREVIEW (not a plain "Android dialog" — DJ disliked that): "PREVIEW · to <first>" eyebrow, message in a brand-tinted editable bubble, "link is included — leave it in" hint, Don't-send / Send. Opt-in **"✨ Let AI tailor it to the conversation"** button (`opts.aiRewrite`) → re-drafts the words blending the recent thread, KEEPING the link. `schedLaunch` passes `aiRewrite` calling **`POST /owner/api/sched/ai_message {so_id,mode,current}`** (reminders.py) which reuses **`ai_sched_message(...,intent='schedule'|'confirm')`** (sms.py — `intent` added, default 'schedule', link-guardrail both ways).
- The 4-day confirm + night-before are lead's nightly HUD approval cards (already branded-page + approval-gated). DJ wants the same ✨ AI-tailor touch on those cards — ASK posted to AGENT_MAIL (lead owns the card render).
- `v2_command.html`: "✓ Confirmed" badge on job cards from `sched/states.confirmed` (`_CONF` map), shown when not already 'accepted'.

Lead still owns the daily 4-day auto-confirm ENGINE (build_batch/build_maint_stage — two parallel confirm systems); it still sends plain "reply YES" text. ASK posted to AGENT_MAIL to switch it to the branded `?c=1` link. See [[project_two_quote_pages_two_launchers]], [[feedback_call_opens_dialer_never_dials]].
