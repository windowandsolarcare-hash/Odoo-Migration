# Every payment lands in journal 6 (Chase Checking) — the METHOD lives only in the memo

**Type:** project
**Date:** 2026-09-01
**Found:** auditing Eric Connolly SO 17600 (264962) after a crash mid-payment

## The fact
`_execute_payment()` in `routers/owner/dashboard.py` (~line 4646) creates every payment with
**`'journal_id': 6` hardcoded** — journal 6 = **Chase Checking (BNK1)**. The payment METHOD is
carried two other ways only:

- `payment_method_line_id` (pml): `{'check': 8, 'cash': 6, 'zelle': 6, 'venmo': 6, 'credit': 7}`
  — note cash, zelle and venmo ALL share pml 6, so this does NOT distinguish them either.
- **the memo/communication string** ("Cash", "Zelle", a check number, …). This is the ONLY reliable
  method marker on the record.

So a CASH payment does **not** go to the Cash journal (18), Zelle does not go to Zelle (19), etc.

## Why it still reports correctly IN OUR APP
Readers special-case the memo BEFORE falling back to the journal. `routers/owner/cron.py` (~line 587):
```python
_JNL_BUCKET = {6: 'Check', 17: 'Check', 18: 'Cash', 19: 'Zelle', 20: 'Credit', 29: 'Other'}
... if 'cash' in memo: bucket='Cash'  elif 'zelle' in memo: ... else: _JNL_BUCKET.get(jnl_id,'Other')
```
**Journal 6 defaults to the 'Check' bucket.** So the memo is load-bearing: strip or reword it and a
cash payment silently reclassifies as a CHECK in every report.

## Why it matters (open, NOT yet raised with DJ as a decision)
- **In Odoo itself** — and to anyone reading the books directly, e.g. an accountant, or the pending
  W&SC accounting punch list — a cash collection looks like a Chase Checking entry. Cash on hand vs
  bank deposits cannot be told apart without parsing memo text.
- Any future reader that buckets by `journal_id` alone (the obvious, correct-looking thing to write)
  will misreport cash/zelle/venmo as Check. Treat journal_id as NOT meaningful for method.

## How to apply
- To ask "how was this paid?", read the **memo**, never the journal.
- Do NOT "clean up" or reformat payment memos — they are the method of record.
- Before writing any new payment report, read this file first; bucketing by journal is the trap.
- Journal IDs (confirmed 2026-06-07): 6 Chase Checking · 17 Check Payments · 18 Cash · 19 Zelle
  · 20 Credit Card · 29 Venmo. Journals 17/18/19/20/29 are essentially unused by the app's own
  payment path — only historical/manual entries land there.
