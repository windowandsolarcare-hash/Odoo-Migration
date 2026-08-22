---
name: project_grounded_inbox_drafts
description: "The inbox auto-suggest hallucinated prices because _inbox_ai_facts (real rates/payment/open-days) was stranded inside the DEAD HUD-card block (sms.py:994 return). Fix: shared _grounded_context() feeds every live drafter + the ✨ rewrite the same real facts."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-08-21T20:16:08.152Z
---

**Why the inbox auto-suggested reply used to make up prices (fixed 2026-08-21).** In `routers/owner/sms.py` there's an **intentional `return` at ~line 994** (DJ 2026-08-07): the block below it builds per-customer **HUD `inbox_ai` approval cards** (`submit_item(kind='approval', source='inbox_ai')` for reply/reschedule/cancel), which DJ deliberately killed — "a customer texting lives in the Inbox ONLY → ONE rollup card." ★ The removed thing is those **HUD cards, NOT the facts-grounding** — but `_inbox_ai_facts()` (real per-item window rates via `quote_prices()`, payment methods, real open days via `open_days_for_partner()`) was ONLY called inside that dead block, so **no live inbox draft ever got real figures** even though the `_inbox_brain()` system prompt tells the model "use the live rates provided." That gap = the pricing hallucination. The ✨ rewrite dodged it only because DJ types the price himself.

**Fix = one shared grounded context, no card resurrection.** `_grounded_context(partner_id, thread, message, data_needed=None)` (sms.py, ~after `_inbox_ai_facts`) = `_customer_context(pid)` (the customer's real jobs) **+** `_inbox_ai_facts(triage's data_needed, pid)` (the real rates/payment/open-days triage says the reply needs). **PURE READ** — no writes/cards/side effects. Wired onto ALL live drafters, each also getting `escalate=_thread_is_hard(thread, msg)` (Haiku→Sonnet on hard threads):
- inbound auto-suggest, `GET /api/inbox/suggest`, `/api/inbox/redraft`, `/api/inbox/intent`, voice `_draft_outbound` (all in sms.py)
- `ai_rewrite` (`POST /api/ai/rewrite`, followups.py) — swapped its `_customer_context` for `_grounded_context` so ✨ and the inbox are grounded IDENTICALLY.
The dead block + the `return` at 994 stay untouched. Commits: sms.py c949988, followups.py 9be3e30 (Lead QC'd the diff first — this is money-adjacent, always propose+verify-by-content).

**Verified by content:** `/suggest` on a real "quote to clean 8 panels" thread now **defers to a quote** (invents NO solar price), and ✨ "make it warmer" stays clean/concise (grounding only ADDS real facts). To re-verify after any change: hit `/owner/api/inbox/suggest?c=<normphone>` on a pricing thread and read the draft; convs live in `ir.config_parameter` `wsc.sms.conv.<normphone>`. See [[project_second_contact_and_recipient_picker]] (same field-app messaging area).
