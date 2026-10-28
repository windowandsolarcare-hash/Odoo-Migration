---
name: project_pt_timezone_pytz_vs_zoneinfo_split
description: "The Render app has TWO different `_PT` Pacific-timezone objects by module — pytz (booking.py, booking_requests.py) vs zoneinfo (shared.py → scheduler.py and anything via `from .shared import *`). They need OPPOSITE idioms: pytz REQUIRES `_PT.localize(naive)` (`.replace(tzinfo=pytz_PT)` attaches the LMT −7:52:58 offset = the Maguire/Kathy-Sell :23 bug); zoneinfo's `.replace(tzinfo=_PT)` is ALREADY DST-correct and `.localize()` AttributeErrors. Check which _PT a module uses before 'fixing' a tz line."
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-28T22:17:09.980Z
---

**Discovered 2026-10-28 (Specialists, caught by Lead §15 firsthand before ship).** The app uses TWO different Pacific-time `_PT` objects, and they demand OPPOSITE code:

- **pytz `_PT = pytz.timezone("America/Los_Angeles")`** — `routers/booking.py:30`, `routers/owner/booking_requests.py:27`. On a **pytz** zone you MUST use **`_PT.localize(naive_dt)`**. Attaching it any other way — `naive.replace(tzinfo=_PT)`, `datetime.datetime(..., tzinfo=_PT)`, `datetime.combine(d, t, tzinfo=_PT)` — attaches the zone's **first historical entry = LMT (Local Mean Time) = −7:52:58**, NOT PST/PDT. Result: a time lands ~7 min early and **date-independent** (LMT never changes), e.g. 12:30 PM → **20:23:00 UTC** on any date. That was the root cause of the long-open booking odd-minute `:23` drift (SO 17758 Kathy Sell, 17777 Terence Maguire) — the approve writer at `booking_requests.py:310` used `.replace(tzinfo=_PT)`. Fix = `_PT.localize(...)`. See [[project_booking_approve_grid_and_time_override]].

- **zoneinfo `_PT = ZoneInfo("America/Los_Angeles")`** — `routers/owner/shared.py:10`, and therefore **`scheduler.py`** (which does `from .shared import *`, no local pytz) and every other module that imports `_PT` from shared. **zoneinfo resolves the correct DST offset per-instant**, so **`naive.replace(tzinfo=zoneinfo_PT)` is ALREADY CORRECT** (12:30 Nov19 → 20:30:00 UTC, −8). zoneinfo has **NO `.localize()` method** → calling `_PT.localize(...)` raises `AttributeError`. In code wrapped in `try/except` (the scheduler write paths are) that AttributeError is **swallowed → the endpoint silently fails** (reschedule / set-time return "Bad date/time", holds vanish). So scheduler.py NEVER had the LMT bug, and "converging it to .localize()" is a REGRESSION. (Caught here: a prior §15 rev wrongly localized scheduler.py 762/1414/1598/1665 — reverted.)

**RULE before touching ANY Pacific-tz conversion:** first check which `_PT` the module binds — grep the file for `import pytz` / `_PT =` / `from .shared import`. pytz → use `.localize()`; `.replace(tzinfo=...)` is the bug. zoneinfo → `.replace(tzinfo=...)` is right; NEVER add `.localize()`. **`.localize()` is a pytz-only method.** `py_compile` / `node --check` CANNOT catch this — it's a runtime `AttributeError` inside try/except; you must trace the `_PT` source or actually exercise the Python path (a quick `python -c` repro of both `.replace` and `.localize` on the real zone settles it instantly).

**Day-bound query filters have the same split** (deferred, low-impact): `booking.py`'s `combine(d, time(0,0), tzinfo=_PT)` midnight bounds are pytz → ~7-min-off (real but harmless at midnight, fix later with `.localize()`); `scheduler.py`'s equivalents are zoneinfo → already correct, leave alone. See [[feedback_windows_python_msys_path_and_crlf_files]] (write-side tz twin of that display class), [[feedback_no_guessing_on_fields]].
