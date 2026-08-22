---
name: odoo_rpc write() positional vs kwargs — CRITICAL
description: odoo_rpc 4th arg is kwargs, not positional. write(vals) needs vals INSIDE args list or it crashes with "unexpected keyword argument"
type: feedback
originSessionId: 96c7eadf-7840-4091-9290-6d3aed1806c8
---
`write(vals)` takes `vals` as a positional argument, NOT a keyword argument. The `odoo_rpc` function signature is:

```python
def odoo_rpc(model, method, args, kwargs=None):
    # kwargs is passed as **kwargs to the Odoo method
```

**WRONG — passes vals as **kwargs, causes TypeError:**
```python
odoo_rpc('sale.order', 'write', [[so_id]], {'field': value})
#                                ^^^^^^^^  ^^^^^^^^^^^^^^^^
#                                args      kwargs — WRONG for write()
```

**RIGHT — vals inside the args list as the second positional arg:**
```python
odoo_rpc('sale.order', 'write', [[so_id], {'field': value}])
#                                ^^^^^^^^^^^^^^^^^^^^^^^^
#                                args includes both id list AND vals dict
```

**Why:** Odoo's `write(self, vals)` signature makes `vals` a positional argument. When passed as `**kwargs`, Python raises `TypeError: SaleOrder.write() got an unexpected keyword argument 'field_name'`.

**How to apply:** Any time you write `odoo_rpc(..., 'write', ...)`, the values dict MUST be the second element inside the args list. This applies to `write` on any model (`sale.order`, `sale.order.line`, `res.partner`, `account.move`, etc.).

**Exception — methods that DO take keyword args (4-arg form is correct):**
- `message_post(body=..., subject=...)` — keyword args, so `odoo_rpc(..., 'message_post', [[id]], {'body': text})` is fine
- `search_read(domain, fields=..., limit=...)` — keyword args OK

**Discovered:** 2026-05-02 — `_sync_so_with_workiz()` had 4 broken write calls. Error: `SaleOrder.write() got an unexpected keyword argument 'date_order'`. Fixed commit `17d277ee`.
