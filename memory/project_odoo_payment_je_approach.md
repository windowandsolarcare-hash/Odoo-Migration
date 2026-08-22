---
name: Odoo 19 Historical Payment via Direct JE
description: account.payment.register wizard creates in_process payments with move_id=False in Odoo 19 SaaS — use direct journal entry + account.move.line.reconcile() instead
type: project
originSessionId: bcd62e72-19be-4a09-af3f-a38378b2ba9e
---
# Odoo 19 Historical Payment — Direct JE Approach

**Discovered:** 2026-05-08

## The Problem

`account.payment.register` wizard in Odoo 19 SaaS creates `account.payment` records in `in_process` state with `move_id=False` (no journal entry). This means:
- AR is NOT cleared (invoice `amount_residual` stays at full amount)
- `payment_state` shows `in_payment` (misleading — nothing is actually posted)
- `action_post()` on the payment also fails to create the journal entry

This affects ALL payment wizard calls — whether via `account.payment.register` wizard or direct `account.payment.create()` + `action_post()`. Not a missing-field issue.

## The Fix: Direct Journal Entry + Reconcile

For historical payments (not bank-fed), create the accounting directly:

```python
CHASE_JOURNAL_ID = 6    # Chase Checking journal
CHASE_ACCOUNT_ID = 100  # 101401 Chase Checking (9008) account
AR_ACCOUNT_ID    = 6    # 121000 Accounts Receivable account

def apply_payment(invoice_id, partner_id, amount, date_str, memo=''):
    pay_date = datetime.strptime(date_str, '%m/%d/%Y').strftime('%Y-%m-%d')

    # 1. Create journal entry
    je_id = models.execute_kw(DB, UID, KEY, 'account.move', 'create', [{
        'move_type': 'entry',
        'journal_id': CHASE_JOURNAL_ID,
        'date': pay_date,
        'ref': memo,
        'line_ids': [
            [0, 0, {'account_id': CHASE_ACCOUNT_ID, 'debit': amount, 'credit': 0.0, 'name': memo}],
            [0, 0, {'account_id': AR_ACCOUNT_ID, 'debit': 0.0, 'credit': amount,
                    'partner_id': partner_id, 'name': memo}],
        ],
    }])

    # 2. Post the JE (returns None = success)
    try:
        models.execute_kw(DB, UID, KEY, 'account.move', 'action_post', [[je_id]])
    except Exception as e:
        if 'cannot marshal None' not in str(e): raise

    # 3. Get the AR credit line from the JE
    je_ar_line_id = models.execute_kw(DB, UID, KEY, 'account.move.line', 'search_read',
        [[['move_id', '=', je_id], ['account_id', '=', AR_ACCOUNT_ID]]],
        {'fields': ['id']})[0]['id']

    # 4. Find unreconciled AR line on the invoice
    inv_ar_line_id = models.execute_kw(DB, UID, KEY, 'account.move.line', 'search_read',
        [[['move_id', '=', invoice_id], ['account_id', '=', AR_ACCOUNT_ID],
          ['reconciled', '=', False], ['amount_residual', '!=', 0]]],
        {'fields': ['id']})[0]['id']

    # 5. Reconcile — invoice shows payment_state=paid, amount_residual=0
    try:
        models.execute_kw(DB, UID, KEY, 'account.move.line', 'reconcile',
            [[je_ar_line_id, inv_ar_line_id]])
    except Exception as e:
        if 'cannot marshal None' not in str(e): raise
```

## Result
- Invoice: `payment_state=paid`, `amount_residual=0.0` ✅
- Journal entry in Chase Checking (debit) and AR (credit) posted ✅
- Multiple payments on same invoice work — each JE partially reconciles the AR line

## Tradeoff
The JE appears in Chase Checking without a matching bank statement line. For 2019–2024 historical data where we're not doing bank statement reconciliation, this is acceptable. For 2025+ the Chase bank feed handles reconciliation separately.

**Why:** `account.payment.register` wizard behavior in Odoo 19 SaaS — confirmed broken for `payment_method_line_id=41` (Manual, inbound) and for direct `account.payment.create()` + `action_post()`. Both produce `in_process` with no `move_id`.
