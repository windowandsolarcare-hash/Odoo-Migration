---
name: project_odoo_get_param_returns_false_unset
description: "Odoo ir.config_parameter get_param returns boolean False (NOT None/'') when a key is UNSET — a default-safe flag must treat False as 'unset', or an unset flag misreads as 'false'"
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-15T12:00:49.302Z
---

**Odoo `ir.config_parameter.get_param(key)` returns boolean `False` when the key is UNSET** — not `None`, not `''`. (When set, it returns the stored string, e.g. `'1'`/`'0'`.)

**Why it bites:** any "default-safe" flag that decides ON/OFF from a stored string will misread the unset state. Classic bug shape:
```python
v = odoo_rpc('ir.config_parameter', 'get_param', [KEY])   # UNSET → False
if v is None or str(v).strip() == '':                      # ← False is NEITHER None NOR '' → skips the default!
    v = DEFAULT
return str(v).lower() not in ('0','false','off','no')      # str(False)='False' → 'false' → returns False (OFF!)
```
So an unset flag meant to default ON silently defaults OFF (LIVE). This exact trap was caught building the tech collect-only test mode ([[project_tech_app_architecture]]): default-safe TEST-ON would have read as LIVE while unset — a money/data-integrity hazard.

**How to apply:** when reading a config param that gates a default, treat `False`/`None`/`''` as "unset → use my default":
```python
if v is None or v is False or str(v).strip() == '':
    v = DEFAULT
```
General rule: never assume `get_param` returns a string; the unset sentinel is `False`.
