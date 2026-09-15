---
name: project_stale_so_payment_execute_payment_import
description: routers/owner/payments.py references _execute_payment (defined in dashboard.py) without importing it → NameError on the tech Cash/check/credit path; fixed with a lazy import
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-15T14:03:03.315Z
---

**`_execute_payment` is defined in `routers/owner/dashboard.py` (~line 4755), NOT in `routers/owner/payments.py`** — but payments.py CALLS it in several places (`_stale_so_payment`, the cash/zelle record endpoints). Those payments.py sites were never given an import, so calling them raises `NameError: name '_execute_payment' is not defined` at runtime.

**How it surfaced (F2, 2026-09-15):** the tech app's Cash/Check/Credit path is `tech/payments.py → owner.payments._stale_so_payment → _execute_payment`. In LIVE mode that NameErrored the moment a tech tapped Cash (DJ hit it in his walkthrough). It was MASKED during the collect-only test because test mode logs-not-executes (never reaches `_stale_so_payment`). The owner's OWN cash/zelle endpoints in payments.py don't show it because they're DEAD (shadowed by dashboard.py copies per the route-shadow rule) — so the tech wrapper was the first LIVE caller.

**Fix:** lazy import at the call site inside `_stale_so_payment`:
```python
from .dashboard import _execute_payment
result = _execute_payment(so_id, amount, method, memo, use_date, source='StaleSOPage')
```
Lazy (function-local) because dashboard.py is heavy and imported through main.py's include order — a module-level `from .dashboard import ...` risks a circular import. Same pattern as `carddoor.py`'s `from .dashboard import _create_stripe_tip_link` and `_stripe_record_and_close`.

**Lesson:** when reusing a payments.py helper from a NEW caller, verify every name it references is actually in payments.py's namespace — several canonical money functions live in dashboard.py and are only reachable via lazy import. Part of [[project_tech_app_architecture]] (the tech money wrappers).
