---
name: project_pricing_snapshot_is_memo_not_dollar
description: "sale.order.x_studio_x_studio_pricing_snapshot is a TEXT pricing-MEMO field (the 'Pricing · this job' textarea), NOT a dollar amount. The quote's actual dollar price lives on the WINDOWS sale.order.line price_unit. _apply_quote_override (brain.py) and send_quote rewrite that LINE's price_unit — neither writes pricing_snapshot. Verified firsthand 2026-11-04 during the accept-to-job price-override byte-QC (Lead had assumed the override should be snapshotted into pricing_snapshot — WRONG)."
metadata:
  node_type: memory
  type: project
  originSessionId: c357000c-2b48-423f-90ce-2e1b8f1f9669
  modified: 2026-11-04T20:59:52.975Z
---

**The trap (Lead got this wrong 2026-11-04, Specialists caught it, Lead confirmed firsthand):** the field name `x_studio_x_studio_pricing_snapshot` *sounds* like it holds the job's snapshotted dollar price. It does NOT. It is a **text pricing-MEMO** field (surfaced as the "Pricing · this job" textarea, dashboard.py ~9493; written only from text memos / legacy Workiz sync). Writing a dollar number into it would corrupt the memo and would NOT change what the job bills.

**Where the dollar price actually lives:** on the **WINDOWS `sale.order.line`'s `price_unit`** (product = QUOTE_PRODUCT_IN_OUT / QUOTE_PRODUCT_OUTSIDE). `amount_total` reflects that line → that is what gets invoiced.

**What the quote/override code actually does (brain.py):**
- `_apply_quote_override(so_id, override)` rewrites ONLY the windows line's `price_unit` in place (siblings untouched; the [Render Quote Tool] breakdown note line is left alone). It NEVER writes pricing_snapshot. Guards: refuse posted invoice, refuse add-on priced lines, bound `0 < amt <= 100000`. Returns `{'ok':True,'amount':amt}` / `{'ok':False,'error':...}`.
- `send_quote` likewise does not write pricing_snapshot. In brain.py the field appears ONLY as a read/display mapping (`('Pricing','x_studio_x_studio_pricing_snapshot')` ~line 28) and in a read-fields list (~line 42) — zero writes.
- `accept_to_job_core` (quotes.py) carries the adjusted price the same way: `_replace_quote_line` writes the windows line, then (optional `amount_override`) `_apply_quote_override` rewrites that line's price_unit. No snapshot write anywhere in the accept path.

**Why:** CLAUDE.md's field table lists it only as "Pricing | sale.order | …pricing_snapshot | Snapshot" — ambiguous, easy to misread as a dollar snapshot. It is a MEMO. Don't repeat the mistake.

**How to apply:** to set/change a job's quoted dollar amount, write the WINDOWS line's `price_unit` (or reuse `_apply_quote_override`) — never `pricing_snapshot`. If you need the human pricing memo, that's the text field. Ties to Rule 1 (never guess field semantics — verify) and [[feedback_reuse_canonical_endpoint]].
