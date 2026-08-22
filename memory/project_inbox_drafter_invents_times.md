---
name: project_inbox_drafter_invents_times
description: "BUG (DJ 2026-08-03): inbox reply drafter INVENTS appointment times because its context (sms.py _customer_context) feeds date-only, UTC — no time, no PT. Any 'what time are you coming?' → hallucinated time. Fix routed to specialist."
metadata: 
  node_type: memory
  type: project
  originSessionId: 1e80ea0d-78f5-4aa2-bc1d-25aace876ab5
  modified: 2026-08-04T00:36:25.800Z
---

**DJ caught the inbox AI suggesting the wrong appointment time.** Donna Uchimura's reply card said the job was at "9:00" (and "Wednesday August 5th") — BOTH fabricated. Real job = SO 264937, `date_order` UTC `2026-08-04 18:00:00` = **Tue Aug 4, 11:00 AM PT**, stored correctly.

## Root cause (sms.py — specialist's lane)
`_customer_context(partner_id)` (~L215) builds the drafter's context with **date-only, UTC**: `date = (so['date_order'] or '')[:10]`. The model is never given the appointment **time** (nor a PT conversion). So on a timing question it has nothing to answer with and **fabricates a time** (and can drift the day). This affects EVERY "what time are you coming?" thread → risk of telling a customer the wrong arrival time.

## Fix (pointed the specialist at it 2026-08-03 via AGENT_MAIL)
The correct pieces already exist in sms.py: **`_find_upcoming_job(partner_id)` (~L607) + `_fmt_pt_dt(dt_pt)`** (used by the reschedule/cancel paths) return the accurate PT datetime. Fix = inject the real next appointment ("Next scheduled: Tue Aug 4, 11:00 AM PT (SO 264937)") into `_customer_context` / draft facts, AND tighten the prompt: "state a specific date/time ONLY if it appears in the provided data — never guess." Lead did NOT edit sms.py (specialist active there). Ties into [[project_inbox_assistant]]. General rule reminder: [[project_date_order_is_start_time]] — date_order is UTC; always convert to PT (UTC-7 PDT / UTC-8 PST) for display.
