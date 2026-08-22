---
name: Odoo 19 payment model field names
description: Correct field names for payment recording in Odoo 19 — memo vs communication vs ref
type: project
originSessionId: 55b3b70b-11bb-4b3a-958a-f4be4ab4e3c1
---
In Odoo 19, payment model field names differ from what you might expect:

- `account.payment.register` wizard: memo field is `communication` (NOT `memo`, NOT `ref`)
- `account.payment`: memo field is `memo` (NOT `ref` — ref field does not exist in Odoo 19)

**Why:** These changed between Odoo 16→17→19 and are easy to get wrong.

**How to apply:** When creating payments programmatically:
```python
# account.payment.register (preferred, handles reconciliation automatically)
wiz_id = odoo_rpc('account.payment.register', 'create', [{
    'payment_date': today,
    'journal_id': 6,
    'amount': amount,
    'communication': f'Stripe - {so_name}',   # NOT memo, NOT ref
}], {'context': ctx})
odoo_rpc('account.payment.register', 'action_create_payments', [[wiz_id]], {'context': ctx})

# account.payment (direct, requires manual reconciliation)
pay_id = odoo_rpc('account.payment', 'create', [{
    'payment_type': 'inbound',
    'partner_type': 'customer',
    'partner_id': partner_id,
    'amount': amount,
    'currency_id': currency_id,
    'journal_id': 6,
    'date': today,
    'memo': f'Stripe - {so_name}',   # NOT ref
}])
```

Context for account.payment.register must include:
```python
ctx = {'active_model': 'account.move', 'active_ids': [invoice_id], 'active_id': invoice_id}
```
