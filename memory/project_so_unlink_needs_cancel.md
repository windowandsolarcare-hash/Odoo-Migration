---
name: Odoo blocks unlink on confirmed sale.order — must cancel first
description: 2026-04-27 — Render Claude's odoo_write tool now auto-cancels sale.order before unlink. Odoo's _unlink_except_draft_or_cancel hook raises UserError on direct unlink of state in (sale, sent, done).
type: project
originSessionId: 96c7eadf-7840-4091-9290-6d3aed1806c8
---
Odoo's `sale.order._unlink_except_draft_or_cancel` hook raises `UserError("You can not delete a sent quotation or a confirmed sales order. You must first cancel it.")` whenever you try to unlink an SO whose state is anything other than `draft` or `cancel`.

**To delete confirmed SOs you must:**
1. `odoo_rpc('sale.order', 'action_cancel', [[so_id]])`
2. `odoo_rpc('sale.order', 'unlink', [[so_id]])`

**Render Claude's `odoo_write` tool** auto-handles this as of commit 318a0801 (2026-04-27): when called with `model='sale.order'` + `method='unlink'`, it cancels each ID first then unlinks. So the LLM doesn't need to remember the two-step.

**Why:** This bites every time. Phase 4 doesn't have to deal with it because Phase 4 only fires on Workiz status changes — but when DJ asks Render Claude to delete a job, it tries unlink directly. Caught here when DJ asked to delete 3 SOs and got the UserError back.

**How to apply:**
- For one-off deletes via Python script: do `action_cancel` then `unlink`. The pattern I used for Judith Gordon's orphans (SOs 16767 and 16424) is the canonical example.
- For Render Claude: trust `odoo_write({model:'sale.order', method:'unlink', ids:[...]})` — the tool now handles the cancel automatically.
- Don't rely on the LLM to remember the two-step. The tool wraps it.
- Same pattern likely needed for `purchase.order` and other lifecycle models, but only add when actually hit.
