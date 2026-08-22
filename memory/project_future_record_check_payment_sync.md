---
name: Task — Add sync to record_check_payment
description: Add _phase4_full_sync() call into record_check_payment tool before invoice creation so Render Claude syncs Workiz before every payment
type: project
originSessionId: 941c4896-3b5a-44bd-a6aa-b5805837b580
---
Add `_phase4_full_sync(so_id)` into the `record_check_payment` tool handler in dashboard.py, right before the invoice creation path (after SO is resolved and validated, before draft_inv lookup).

**Why:** System prompt routes ALL Render Claude payments to `record_check_payment`, but that tool does zero Workiz sync. Payment gets recorded against whatever is in Odoo, not fresh Workiz data.

**How to apply:** Insert after SO state/line checks, before the invoice path (~line 1615 in dashboard.py). Keep all existing safeguards (multi-SO disambiguation, mismatch detection, tip handling). Just add:
```python
_phase4_full_sync(so_id)
# Re-fetch SO after sync in case lines/amount changed
so_data = odoo_rpc(...)
```
