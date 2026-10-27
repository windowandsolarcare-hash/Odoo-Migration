---
name: project_pt_offset_dst_shared_helpers
description: Never hardcode UTC→PT offset; use shared to_pt_naive()/pt_day_bounds_utc() (DST-aware)
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-27T08:28:27.792Z
---

Converting UTC→Pacific with a hardcoded `datetime.timedelta(hours=7)` (and the paired `hours=31` day-window ends) renders times **1 hour LATE Nov–Mar** — 7h is only right during PDT; PST = UTC-8. This is a recurring class. DJ hit it 2026-10-27 on Maguire SO 265042 (date_order 2026-11-19 20:23 UTC showed **1:23 PM** instead of **12:23 PM** PST). Stored times were correct — it was display + GPS day-window query bounds only.

**Rule: never hardcode the PT offset.** Use the canonical DST-aware helpers in `routers/owner/shared.py` (exported in `__all__`, so `from .shared import *` files get them; others import by name):
- `to_pt_naive(dt_utc=None)` — a naive-UTC datetime (or `utcnow()` if None) → **naive** Pacific datetime (DST-correct). For displaying a stored UTC time; returns naive so it drops into existing `.year`/`.strftime`/compare sites.
- `pt_day_bounds_utc(date_pt)` — a Pacific calendar day ('YYYY-MM-DD' or date/datetime) → `(utc_start_str, utc_end_str)` for Odoo day-window queries. End = next Pacific midnight, so DST-transition days (23h spring / 25h fall) are correct, which a fixed `+24h` was not.

`_PT = ZoneInfo('America/Los_Angeles')` is the canonical zone (defined in shared.py; dashboard.py also keeps its own copy). Whole class fixed 2026-10-27 across dashboard.py / hemet.py / cron.py / shift_review.py / voice.py (10 sites, main 620b22e858, Lead+Audit §15 GREEN, atomic single-commit so the additive shared.py helpers land with the consumers — no import-order boot crash).

**Deliberately NOT fixed:** `usage_store.py:26` `_PT = timezone(timedelta(hours=-8))` — internal daily token-usage bucket only (`.date()` on lines 187/213/264), never a displayed time, no scheduling/money/customer impact; -8 is winter-correct, only a ~1h summer midnight-boundary smear, immaterial for a daily count. On the AGENT_MAIL ledger.

**Open tiny follow-up (Lead/Audit/me all flagged, no rush):** voice.py `_cc_pt` still takes day (`du[8:10]`) and year (`du[:4]`) from the RAW UTC string — only the month now comes from the converted dt. Pre-existing, left per surgical rule. See [[feedback_times_in_pacific]].
