---
name: project_ai_rewrite_grounding
description: "\"Ask Claude to rewrite\" (/api/ai/rewrite, followups.py) invented facts — rewrote \"what's your address?\" into \"I already have your address at [placeholder]\". Fixed: forbid inventing/placeholders + optionally ground on real customer facts+thread."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0e6fb90e-8d05-4272-91a3-ed7ee21488d7
  modified: 2026-08-15T16:03:11.748Z
---

**Symptom (DJ, 2026-08-14):** on a new referral (no address on file — the initial draft correctly ASKED "what's your address?"), DJ hit "Ask Claude to rewrite" and it produced "I already have your address at **[specific address on Furyke Way in Hemet]**" — a fabricated claim + a bracketed PLACEHOLDER that would send literally. Same hallucination class as [[project_inbox_drafter_grounding]] (Nancy "Bob Hope Drive") and [[project_draft_booking_link_placeholder]].

**Root cause:** `/api/ai/rewrite` (followups.py L432, SHARED by inbox rewrite + follow-ups + booking reply cards) received ONLY `{text, instruction}` — no customer record, no thread — and its prompt said "preserve facts" but had NO rule against INVENTING facts. So it added a plausible-sounding address to be "helpful." It has no memory; it was never given the address to reference.

**Fix (commits followups 4dbb457 / v2_inbox 202ad25):**
1. **Anti-invention rule** in the rewrite system prompt (all callers): "do NOT invent/add/assume any fact (address, price, panel count, date, name) not in the current message or the FACTS provided; NEVER output a bracketed placeholder; if the message ASKS the customer for info, KEEP asking — never claim you already have it."
2. **Optional grounding:** rewrite now accepts `c` (conv norm). If passed, it lazy-imports `sms._conv_get/_customer_context/_thread_text` → feeds the REAL customer facts (address/gate/history) + recent thread as "FACTS (reference ONLY these)". So when the info genuinely exists (address on file OR the customer said it in the thread), the rewrite uses the REAL value; otherwise it can't invent. **v2_inbox rewriteReply passes `c: CUR.norm`.** Backward-compatible: callers without `c` (booking cards, follow-ups) just get the anti-invention rule.

Booking-link preservation (existing) still runs after. General rule: any AI text pass (draft, rewrite, suggest) must be grounded + forbidden from inventing/placeholdering — instruction alone isn't enough, but it's the floor.
