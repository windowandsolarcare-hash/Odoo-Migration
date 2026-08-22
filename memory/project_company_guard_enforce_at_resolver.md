---
name: project_company_guard_enforce_at_resolver
description: "The company_id in [1,False] filter must be enforced INSIDE the resolver, not per-caller — a bare partner_id path bypassed it and rendered a Saunders Printing customer a full W&SC customer portal (found + fixed 2026-08-19)."
metadata: 
  node_type: memory
  type: project
  originSessionId: 794f50c8-7ee3-4629-8a3e-298d430ec9f5
  modified: 2026-08-19T14:50:10.519Z
---

CLAUDE.md rule 8 says every `res.partner` customer search needs `['company_id','in',[1,False]]`.
The trap is **where** you put it.

**Real incident 2026-08-19 (customer portal).** `/owner/api/portal/link?q=<name>` carried the leaf
correctly. The sibling `?partner_id=<id>` path — and `build()` behind `/portal/api/me` — did not.
Result, verified on the LIVE site before fixing: `wscare.pro/p/26947-…` rendered a complete
**Window & Solar Care** portal for **National Baseball Hall of Fame**, a **Saunders Printing
(company 3)** customer — greeting, street address, everything. A Cheryl (2) contact behaved the same.
Fixed by putting a hard `_is_wsc()` check inside **`account()`**, the single resolver both routes
pass through (`portal.py` 1e580d36).

**Why:** two lessons that generalize past this one file.
1. **Enforce at the resolver, not at each caller.** A filter applied in one of N call paths is not a
   filter — it's a coin flip, and the unguarded path is the one nobody tests. Find the one function
   that turns an id/name into a record and guard there.
2. **`company_id` FAILS OPEN for W&SC.** W&SC customers are overwhelmingly `company_id = False`
   (unstamped from the migration), not `1`. So "unstamped W&SC customer" and "another business's
   customer" are *both* non-1 values — you cannot treat missing-company as safe. Check membership in
   `(1, False, None)` explicitly; never `!= 2 and != 3`, and never "if it has no company it's ours".

**How to apply:** any endpoint that accepts a raw `partner_id` (or a token minted from one) and
renders/sends W&SC-branded content needs this guard at its resolver. Lead raised the identical
prompt-only-vs-enforced gap for the voice `open_text_draft` tool the same day — treat a
prompt-level instruction to filter as documentation, never as enforcement.

Related: [[project_customer_portal]], [[feedback_no_guessing_on_fields]]
