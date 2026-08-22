---
name: Odoo 19 server action reserved variable names
description: response and result are reserved in Odoo 19 server action eval context — never use them as local variable names
type: project
---

In Odoo 19 server actions, the eval context treats certain variable names as special return values, just like `action`:

- `response` — if set, Odoo uses it as the HTTP response (causes `'Response' object has no attribute 'setdefault'` error)
- `result` — potentially also captured

**Why:** Using `response = requests.get(...)` overwrites Odoo's internal response variable, causing the requests.Response object to be returned as the action result, which crashes `clean_action()`.

**How to apply:** In ALL server action code, never use `response` or `result` as local variable names. Use `workiz_resp`, `workiz_data`, `api_resp`, `api_result`, or similar prefixed names instead.
