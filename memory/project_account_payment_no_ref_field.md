---
name: account.payment has no 'ref' field in Odoo 19 — use 'memo'
description: 2026-04-28 — Schedule endpoint broke ("No jobs today") because new code queried account.payment.ref which doesn't exist. Use memo for the customer-facing reference instead. Also: wrap any new helper that touches a less-trafficked model in try/except so a schema mismatch can never block the main page from rendering.
type: project
originSessionId: 96c7eadf-7840-4091-9290-6d3aed1806c8
---
In this Odoo 19 instance, `account.payment` does NOT have a `ref` field. Reading it raises `ValueError: Invalid field 'ref' on 'account.payment'`. The only customer-visible reference field is `memo` — that's where `account.payment.register` writes the `communication` value from `record_check_payment`.

**Why:** Caused a "No jobs today" outage on 2026-04-28 — the new last-payment-method preselect added an `account.payment.search_read` with `fields=['memo', 'ref']`. The exception bubbled out of `_last_payment_method_by_partner` and broke `tool_schedule` for the field assistant.

**How to apply:**
- For Zelle/Venmo memo detection, the only field to read is `memo`.
- Don't assume Odoo classics like `ref` exist — query `ir.model.fields` first if uncertain.
- More importantly: **any auxiliary lookup that decorates a primary response (preselects, badges, hints) should be wrapped in try/except.** The primary endpoint must keep working even if the side-trip fails. Pattern:

```python
def _safe_decorator(...):
    if not inputs: return {}
    try:
        # actual lookup
        return result
    except Exception:
        return {}  # graceful degradation — the main feature still works
```

Applied to `_last_payment_method_by_partner` after this incident.
