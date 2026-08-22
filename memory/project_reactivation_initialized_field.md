---
name: project_reactivation_initialized_field
description: FUTURE BUILD — add x_studio_reactivation_initialized field to fix new customers appearing on reactivation report prematurely
metadata: 
  node_type: memory
  type: project
  originSessionId: f95b5c02-0629-4ade-8f81-8981d2f629ca
---

## Reactivation Initialized Field

**★ RESOLVED 2026-07-07 — the phantom 2019-01-01 stamps were CLEARED.** The planned "add an initialized field" build turned out unnecessary: the current Outreach classifier decides "lapsed" by **last visit date**, not by `x_studio_last_reactivation_sent`, so the field no longer does double-duty. Action taken: deleted `x_studio_last_reactivation_sent = '2019-01-01'` from all **239** partners carrying it (set False); the **274** real recent send dates (mostly 2026-spring) left intact. Rollback list = `C:/Users/dj/phantom_reactivation_rollback.json`. Also added a permanent guard in reactivation.py `api_outreach_timeline`: never reports `2019-01-01` as a real send even if re-stamped. Blank `x_studio_last_reactivation_sent` now truthfully means "never sent." (Triggered by DJ seeing the fake "Reactivation sent · 2019-01-01" in the Outreach review facts panel.) Original 2026-05-28 design kept below for history.

**Status:** ~~FUTURE BUILD — designed, not built (2026-05-28)~~ → resolved 2026-07-07 (above)

**Problem:**
`x_studio_last_reactivation_sent` on res.partner does double duty — it tracks both "was a reactivation text sent" and "when was this record initialized." New customers have a blank field, so they appear on the reactivation report immediately even though they're active. The 2019 bulk stamp solved this initially but is misleading — future Claude sessions will assume those customers actually received a text on that date.

**Solution: Add a second field**
- `x_studio_last_reactivation_sent` — ONLY written when a reactivation text actually goes out. Never stamp this for initialization purposes.
- `x_studio_reactivation_initialized` — date field, stamped by Phase 3 when a new customer SO is created. Means "this record is in the system, don't show yet."

**Updated reactivation report filter logic:**
- Last reactivation sent > 1 year ago → show
- Field blank AND initialized > 1 year ago → show (lapsed, ready to reactivate)
- Field blank AND initialized < 1 year ago → hide (new customer, too soon)
- Field blank AND not initialized → show (pre-system customer, never touched)

**Why:** DJ explicitly does not want phantom send dates. The 2019 stamp was a one-time compromise. Going forward, data integrity matters — a blank `x_studio_last_reactivation_sent` should always mean the customer genuinely never received a text.

**How to apply:** When building this:
1. Create `x_studio_reactivation_initialized` date field on res.partner via Odoo API
2. Add Phase 3 stamp when new SO creates a new partner
3. Update reactivation candidates endpoint filter logic in dashboard.py
4. Backfill existing active customers with today's date (they're already in the system)
