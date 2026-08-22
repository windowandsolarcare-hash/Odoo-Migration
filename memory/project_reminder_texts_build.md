---
name: project_reminder_texts_build
description: "Appointment reminder texts moved OFF Workiz status-automation onto Render/Twilio — messaging.py (canonical send) + reminders.py (3-day confirm + night-before, HUD approval) built & verified live 2026-07-30"
metadata: 
  node_type: memory
  type: project
  originSessionId: 8f0313dc-02cc-482c-833a-0ab0d7a6b313
  modified: 2026-07-30T23:03:15.181Z
---

**2026-07-30.** First real cut of post-Workiz customer texting. DJ's ask: dump Workiz (Monday-ish),
stop triggering texts by flipping a Workiz SubStatus ("clunky"), and get reminders running on the
Render side. Scope he chose for the cutover = **the two reminders only** (3-day reconfirm +
night-before). Approve-first, **through the HUD** — not a separate screen.

**Built (all live + verified on the local Twilio number +17603435762):**
- **`routers/owner/messaging.py` (NEW) = THE canonical outbound SMS layer.** Everything that
  texts a customer must call `messaging.send(to, body, partner_id, so_id, kind, idem)`. It does:
  idempotency ledger (`wsc.msg.sent`, same `idem` never sends twice), STOP list (`wsc.msg.optout`),
  Odoo Do-Not-Contact check (walks property→parent), transport via `sms._send_sms`, threads the
  message into the **existing inbox conversation** so replies land under it, and posts to
  res.partner + sale.order chatter. Also `record_optout` (adds to list AND writes
  `x_studio_activelead='Do Not Contact'` on the PARENT — Twilio never tells Odoo), `record_optin`,
  `classify_keyword`, `in_quiet_hours` (8am–9pm PT).
- **`routers/owner/reminders.py` (NEW)** — sweeps `sale.order` by **`date_order`** (the real
  trigger, not a status). `confirm` = today+3, `eve` = tomorrow. Builds a batch into
  `wsc.reminders.batch.<id>`, submits **ONE** approval card per batch to the HUD feed
  (`reminders:<kind>:<date>`, generic stable title, count in `badge`, names in `why_now`) per
  [[project_attention_feed_contract]]. `on_approve` → `/owner/api/reminders/send_batch` (idempotent).
- **`static/owner/v2_reminders.html` (NEW)** — the review screen the card opens: per-customer
  editable body, Skip/Include, Send-this-one, Send-all. Fetch timeouts + double-tap guards.
- **`sms.py` (surgical edits, nothing removed):** `_send_sms` now sends via
  `TWILIO_MESSAGING_SERVICE_SID` when set (falls back to `From`) and **returns Twilio's dict**
  instead of a bool (both existing callers only test truthiness, so unaffected); inbound now calls
  `reminders.handle_inbound()` BEFORE triage so YES/STOP/START never land in Needs Reply — the
  message is still threaded + logged either way.
- **`main.py`:** registered both routers + `_scheduled_reminders` every 30 min (builds only,
  never sends). Render env `TWILIO_MESSAGING_SERVICE_SID=MG9d920513cc6e7f7963a4334a818fbf05`
  set via MCP **merge** (replace:false).

**★ THE NIGHT-BEFORE WORDING IS DJ'S REAL ONE, recovered — don't reinvent it.** Pulled from the
imported Workiz transcripts (`ir.attachment` description `[workiz-history]`, see
[[project_workiz_chat_export_to_odoo]]) where it appears 40+ times:
> "Hi {first}, just a quick reminder about our appointment tomorrow. If you live in a gated
> community, be sure that I'm on the list or have the gate code."
Workiz's *automated* messages logged only as "Automated Message confirming the date and time..." —
so the 3-day confirm has **no** legacy wording and was drafted fresh (includes "Reply STOP to opt
out"; DJ can strike it on the review screen).

**★ GOTCHAS FOUND THE HARD WAY (verified against live Odoo):**
1. **`sale.order.partner_id` is the PROPERTY record, not the person** (e.g. 24884 "58 Grenache",
   `record_category='Property'`). The customer's name for "Hi {first}" comes from its `parent_id`.
   Phone lives on the property but is the parent's. `_partner_details()` handles the walk.
2. **`x_studio_x_studio_ok_to_text` is UNRELIABLE — do NOT hard-block on it.** 404 Yes / 315 No /
   201 blank across 920 properties, and Brenda Williams (id 24096) is `No` yet demonstrably
   received the tomorrow-reminder repeatedly. In Workiz it meant "don't send the automated
   confirmation", not "never text". Decision: it is a **flag on the review card**, not a gate.
   Hard blocks = Do Not Contact (68 contacts) + STOP list only.
3. `date_order` is UTC; sweep converts a **Pacific** calendar day to a UTC range
   (`_pt_day_bounds_utc`) or jobs fall off the edges.
4. `%-I` in strftime is POSIX-only — use `.strftime('%I:%M %p').lstrip('0')`.
5. Exclude `x_studio_x_studio_x_studio_job_type` containing "personal time" etc, and Workiz status
   Done/Canceled, or DJ texts himself about his own calendar blocks.

**VERIFIED LIVE 2026-07-30:** batch build against Aug-7 jobs produced correct names/phones/PT times
/gate codes; feed card correct shape (badge 2); real SMS to DJ's cell `SM576881c9...` =
**delivered**; repeat call with the same `idem` correctly refused (`already_sent`).

**Test hooks (token = CRON_SECRET):** `/owner/api/reminders/batch?kind=&rebuild=1&target=YYYY-MM-DD`
(run a day early / test a day that has jobs), `/owner/api/reminders/state?token=`,
`/owner/api/reminders/arm_test?token=&to=&so_id=` (seeds the awaiting-YES marker so replying YES
exercises the confirm path). ⚠ Use DJ's own **S00197 = so_id 17503** for arm_test, not a real
customer's SO.

**NOT DONE / KNOWN GAPS:**
- **Reactivation + re-engagement still send via WORKIZ** (`reactivation.py` writes
  `x_studio_manual_sms_override`, `reengage.py` self-calls followup/launch, both rely on Workiz
  automation). **These die with Workiz** and were explicitly OUT of the scope DJ picked. Biggest
  remaining cutover risk.
- Booking-confirmation text, quote texts, "funds received" texts also still Workiz-side.
- The booking specialist's flow assumes "DJ flips Workiz status → text auto-fires"
  (AGENT_MAIL 2026-07-29d/e) — that assumption breaks at cutover.
- Only the LOCAL number can send. Toll-free +18775024795 needs **Toll-Free Verification**
  (separate from A2P) — status unverified. Ports of the 7 Workiz numbers not started
  ([[project_twilio_port_details]]).
- No Twilio status-callback webhook yet, so a carrier-rejected message still reads as sent.
- Confirmation state lives in `ir.config_parameter wsc.reminders.confirmed.<so_id>` (+ chatter),
  not a real Odoo field — promote later if DJ wants it visible/reportable in Odoo.

**Why:** this is the first customer-facing outbound texting the business owns end-to-end, and the
send layer is deliberately ONE function so the next duty (reactivation) plugs in instead of growing
a second Twilio path.
**How to apply:** never call Twilio directly — call `messaging.send()`. New reminder-ish duties
build a batch + submit one HUD approval card; they do not push and do not render their own UI.
Related: [[project_sms_inbox_build]] [[project_voice_inbound_plan]] [[project_twilio_a2p_and_entity]]
[[feedback_reuse_canonical_endpoint]].

**★★ TWO BUGS FOUND ON DJ'S FIRST REAL TEST (2026-07-30 night) — both fixed, both worth remembering:**
1. **`sms.py` silently SWALLOWED every text DJ sent to the business number.** The dormant Phase-0
   "DJ texts the business line to approve a queued draft" branch matched on `DJ_PHONE_NUMBER` and
   **returned unconditionally** — even with an empty queue. So DJ's "Yes" hit the webhook (Render
   log showed `POST /owner/api/sms/incoming 200`) and vanished: no inbound in the conversation, the
   awaiting marker never cleared, no auto-reply. It only bites when DJ texts the business line
   himself — which is EXACTLY how he tests, so it would have masked every future test too. Fix
   (commit 074e3247): moved the `return` INSIDE `if pending_list:` so an empty queue falls through
   to normal handling. Legacy branch otherwise untouched (rule 10). ★ Diagnostic that cracked it:
   webhook logged 200 but the conversation had no inbound message ⇒ the handler early-returned, not
   a Twilio/webhook-config problem. Check the Render request log BEFORE suspecting Twilio.
2. **Auto-reply was stored BEFORE the message it answered** — thread read backwards. `handle_inbound`
   ran (and its `messaging.send` appended the outbound) before `sms_incoming` appended the inbound.
   Fix (commit 2f96760b): append + `_conv_set` the inbound FIRST, then call `handle_inbound`, then
   re-read the conv before setting triage state. **General rule: anything that can auto-reply must
   persist the incoming message before it runs.**

**Verified after the fixes:** armed → inbound YES → awaiting cleared → "Great — see you then!" sent
→ Info card `reminders:confirmed:<so_id>` (kind `attention`) → conv `status=open`, `unread=False`
(never Needs Reply). Replying YES twice sends only ONE thank-you (idem `reminder_ack:<so_id>`).
