---
name: project_inbox_drafter_grounding
description: "Inbox reply drafter invented a customer's street (\"Bob Hope Drive\"), 6 fake availability dates, and asked for a gate code already on file. Fixed by feeding _customer_context real address + gate status + real open days."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0e6fb90e-8d05-4272-91a3-ed7ee21488d7
  modified: 2026-08-11T15:42:21.116Z
---

**Incident (DJ, Nancy Tohl 2026-08-11):** the inbox "Suggested reply" claimed her "condo on Bob Hope Drive" (real address = 23 Calais Cir, Rancho Mirage), listed 6 specific availability dates (Aug 13/14/15, 19/20/21), and said "it's a gated community, I'll need the gate code" — when her gate code (#3066) is already on file. DJ: "this seems completely made up."

**Fact-check:** the $245 + "Windows Inside & Outside Plus Screens" were REAL (her last two jobs; `_customer_context` feeds last 3 SOs with amount + job type). The address, the dates, and the gate ask were HALLUCINATED.

**Root cause:** `_draft_reply` (sms.py) gets `context = _customer_context(partner_id)` + the thread. `_customer_context` supplied next-appointment + last-3-job history, but NOT the customer's street/city, NOT gate status, and NOT real availability. The live inbox-thread draft path (`conv['draft'] = _draft_reply(...)` ~L1162) never calls `_inbox_ai_facts` either, so it had ZERO availability data. The system prompt says "never invent an address/date," but a strong instruction alone doesn't stop the model from filling a plausible-looking void — it invents where DATA is missing (address, dates), and is correct where data is present (price/service).

**Fix (commit 41b5e31, sms.py `_customer_context`):** now appends
- `CUSTOMER ADDRESS: <street, city>. Use ONLY this — NEVER name any other street or invent an address.` (walks contact → Property child for the address/gate; property-as-brain).
- `GATE: a gate code is already ON FILE — do NOT ask the customer for the gate code.` (only when a gate code exists).
- `REAL OPEN DAYS (offer ONLY these …): …` via `open_days_for_partner(partner_id,3)`, or an explicit "none — do NOT propose any date, defer" when empty.

DJ chose (implicitly, "yes") to offer real open days rather than never-propose. Related earlier fix: [[project_inbox_drafter_invents_times]] (invented appt TIMES; added next-appointment to context). General rule: the drafter fabricates wherever context has a gap — ground every specific it might state (address, gate, dates, price) with real data + an inline "use only this" line; instruction without data is not enough.
