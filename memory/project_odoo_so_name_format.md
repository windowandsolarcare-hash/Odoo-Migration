---
name: odoo-so-name-format
description: "Odoo SO name format — 6-digit zero-padded numbers, no S prefix"
metadata: 
  node_type: memory
  type: project
  originSessionId: 7b173fd1-b5b7-43e3-ba55-7c216343fb45
---

Odoo SO names (sale.order.name) are **6-digit zero-padded numbers with NO prefix**.

Examples: `003575`, `004659`, `001234`

**NOT** `S00123`, `S03575`, or any S-prefixed format — that assumption was wrong.

**Why:** Queried live Odoo on 2026-05-20, last 10 SOs returned: 004659, 004658, 004657...

**How to apply:**
- When DJ says "job 3575", normalize to `str(3575).zfill(6)` = `"003575"` for exact match
- Use `['name', '=', '003575']` in search domain
- Never add S prefix to SO names
