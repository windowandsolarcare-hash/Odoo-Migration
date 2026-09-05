---
name: project_shared_star_import_scoping_gap
description: "A new owner router that needs dashboard.py's quote calc/constants (QUOTE_DIFFICULTY, _calc_quote_total, QUOTE_PRODUCT_*, _quote_breakdown_text) must LAZY-IMPORT them from routers.owner.dashboard — `from .shared import *` does NOT surface them (runtime NameError)."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-05T08:22:28.059Z
---

**Gotcha (bit `accept_to_job` 2026-09-05, QC-caught before it reached DJ):** several owner routers do `from .shared import *` at module top and then use dashboard.py-defined quote names — `QUOTE_DIFFICULTY`, `QUOTE_PRODUCT_IN_OUT` (141), `QUOTE_PRODUCT_OUTSIDE` (103), `_calc_quote_total`, `_quote_breakdown_text` (all defined at `routers/owner/dashboard.py` module scope, ~lines 6334–6451). But `from .shared import *` does NOT reliably surface those names into a sibling router's namespace — a new endpoint referencing them throws a runtime `NameError: name 'QUOTE_DIFFICULTY' is not defined` on first call. (Underscore names are excluded from `import *` unless in `__all__`, and the shared re-export chain doesn't carry all of them; the exact why matters less than the fix.)

**Fix / pattern:** in the new endpoint, LAZY-import what you need from dashboard.py inside the function body (avoids any module-load/circular-import issue):
```python
from routers.owner.dashboard import (QUOTE_DIFFICULTY, QUOTE_PRODUCT_IN_OUT,
    QUOTE_PRODUCT_OUTSIDE, _calc_quote_total, _quote_breakdown_text)
```
(Existing quotes.py endpoints — api_quote_save/update — reference the same names and appear to work, so don't assume `from .shared import *` covers you; verify with a real call. A functional throwaway QC catches this class of bug that `py_compile` + boot-check do NOT — the NameError only fires at call time.)

**The broader lesson (why the money-write QC matters):** `py_compile` and a boot/route probe passed while `accept_to_job` was still broken — the NameError only surfaced when the endpoint actually ran its logic. For any money/data-write endpoint, run a FUNCTIONAL QC on throwaway data (create test SOs, exercise every path, clean up) before it's trusted — that's what caught this. See [[project_auth_enforce_operator_gap]] / [[feedback_verify_limits_before_declaring]].
