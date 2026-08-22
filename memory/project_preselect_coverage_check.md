---
name: After accounting migration phase 4-5, verify payment preselect coverage
description: Pending follow-up — once historical Workiz payment CSVs land in Odoo's account.payment, run a coverage check on the field assistant's last-payment preselect. Today most customers default to "Check" because Odoo has almost no payment history.
type: project
originSessionId: 96c7eadf-7840-4091-9290-6d3aed1806c8
---
When the Odoo accounting migration phases 4-5 complete (Workiz Payment CSV imports populating `account.payment`), run a coverage check on the field assistant payment preselect.

**Why:** As of 2026-04-29, the preselect logic in `_last_payment_method_by_partner` (Saunders Render App/routers/owner/dashboard.py:2624) is correct and verified end-to-end (Gary Marsalone partner 24153 → contact 23031 → Zelle, confirmed via direct Odoo query). But almost every customer falls through to the 'check' default because there are virtually no `account.payment` records in Odoo yet — only a handful from invoices DJ has processed through Odoo. The fix is the accounting migration, not the code. DJ confirmed "Path A" (wait for migration, no Workiz API fallback).

**How to apply:**

When DJ mentions completing accounting migration phase 4 or 5 (the Workiz CSV import phases — see `project_odoo_accounting_migration.md`), proactively offer to run this check:

```python
# Coverage report — % of upcoming-schedule customers that now have an account.payment
sos = odoo_rpc('sale.order','search_read',
    [[['date_order','>=', today_iso + ' 00:00:00'],
      ['date_order','<=', plus_14d_iso + ' 23:59:59'],
      ['state','in',['sale','done']]]],
    {'fields':['partner_id']})
partner_ids = list({s['partner_id'][0] for s in sos if s.get('partner_id')})
result = _last_payment_method_by_partner(partner_ids)
print(f"Coverage: {len(result)}/{len(partner_ids)} ({100*len(result)//max(1,len(partner_ids))}%)")
print("Methods:", Counter(result.values()))
```

If coverage is < 70%, investigate why (memo parsing? walk Property→Contact failing for some? PML IDs changed?).

If coverage is healthy (≥70%), no action needed — preselect is now doing its job in production.

**Related:**
- `project_odoo_accounting_migration.md` — phase status
- `project_account_payment_no_ref_field.md` — the schema gotcha that caused the original outage
- `session_apr28_29_summary.md` — original preselect implementation context
