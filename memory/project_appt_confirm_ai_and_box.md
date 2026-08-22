---
name: project_appt_confirm_ai_and_box
description: "Reschedule confirmation text — in-app editable box (no native prompt) + AI wording that plays off the customer's recent texts, guardrailed to keep the exact time, template fallback."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0e6fb90e-8d05-4272-91a3-ed7ee21488d7
  modified: 2026-08-05T07:30:14.106Z
---

**The "Send this confirmation to <cust>?" box after a reschedule** (v2_field `sendApptConfirm`). Theory: rescheduling a job does NOT itself notify the customer — this box offers to TEXT them the new time. Editable + skippable; `send_confirm` respects quiet hours (holds → sends 8am).

**Two fixes 2026-08-04 (DJ):**
1. **Native `prompt()` → in-app box.** The old `prompt()` was unusable on a phone (one cramped line, can't edit, autocorrect garbles it — and violates the no-JS-dialog rule). Replaced with `_openApptConfirm(soid,name,message)` in v2_field: a bottom-sheet with a real editable `<textarea>` (value set via `.value`, never innerHTML) + **📤 Send** and **Don't send**. `top:36px` so it clears the clock-in bar. DJ confirmed he sometimes doesn't want to send → Don't-send just closes, texts nothing (reschedule already saved).
2. **AI wording plays off previous texts.** Was a hardcoded template (`"Hi %s, you're scheduled for %s. See you then! – Dan"`). Now `scheduler.py` `_confirm_ctx` calls **`sms.py ai_confirm_message(partner_id, phone, first, when_lbl, fallback)`**: pulls the recent thread (`_conv_get(norm)` msgs, else `_history_msgs(_history_text(pid))`, last 6), Haiku writes a short confirmation in Dan's voice matching their tone/echoing a phrase (e.g. "in and out"). **Guardrail:** the exact time part (`when_lbl.split(' at ')[-1]`, e.g. "8:00 AM") MUST appear verbatim in the output or it returns the plain `fallback` template — so the time is never dropped/changed and nothing is invented. No-thread customers (demo Dick) → template. Verified: Rod (real thread) → "Great news, Rod—we got you scheduled for Wednesday, August 5 at 8:00 AM…" (kept exact time); Dick (no thread) → template.

**Also fixed:** after reschedule, v2_field `submitJobRs` now `await openJobById(soid, date)` so the job-detail HEADER refreshes to the new date/time (it was stale because the rescheduled job moves off the current day view).

`confirm_preview`/`send_confirm` live in scheduler.py (lead's); the AI hook is a 4-line additive call to my sms.py fn. Related: [[project_quiet_hours_hold_queue]], [[feedback_call_opens_dialer_never_dials]].

## Shared _openSendBox + AI scheduling message (2026-08-04)
Generalized the in-app box: v2_field `_openSendBox({title,note,message,okMsg,sendLabel,onSend})` is now the ONE composer; `_openApptConfirm` delegates to it AND `schedLaunch` ("Send scheduling options") uses it — replaced that flow's native `prompt()` too. onSend does the POST + returns JSON; box shows held/ok/error toast.
AI scheduling wording: sms.py `ai_sched_message(partner_id, phone, first, link, fallback)` (twin of ai_confirm_message) — Haiku drafts a warm book-your-next-cleaning SMS playing off recent texts; GUARDRAIL = the wscare.pro link must survive verbatim else returns template. reminders.py `/api/sched/launch` calls it (template fallback). Shared thread-pull extracted to sms.py `_recent_thread_text(partner_id, phone)`. Verified: Rod → "Hey Rod, whenever you're ready to schedule… book it right here: <link> – Dan".
