---
name: project_daily_sync_shadow_reverting_odoo
description: "★ The overnight 'WSC Daily Sync' (Render cron /api/cron/daily_sync, 4am PDT) was REVERTING DJ's Odoo edits from Workiz nightly — NOT Zapier. cron.py._run_daily_sync was paused 2026-08-03 but dashboard.py SHADOWS it (registered first) and its copy was still active. Paused dashboard.py's too 2026-08-06 (sos=[])."
metadata:
  type: project
---

**Incident 2026-08-06:** overnight, John Bullock SO 004557/17389 was reverted — date 2026-08-05 15:00→2026-10-15 17:00 (Aug 5→Oct 15) + pricing $330 (Outside Windows & Screens $185 + Solar $145) → $445 (Windows In&Out $300 + Solar $145). DJ blamed Zapier + turned all Zaps off, but it recurred.

**Root cause (found via DJ's emailed report):** the culprit is the **Render app's OWN cron `GET /api/cron/daily_sync`** (fires 4:00 AM PDT), which pulls each SO from Workiz and overwrites Odoo — NOT Zapier. Report email "WSC Daily Sync — ⚠ Issues found" (from windowandsolarcare@gmail.com) showed: 57 processed, **only 1 changed = 004557 (John)**, 54 already-current, 2 errors (003951 'int has no strip' code bug; 004858 no tech — neither changed). So John was the ONLY revert.
- **Shadow bug:** `cron.py._run_daily_sync` was paused 2026-08-03 (early `return`), BUT **dashboard.py has its OWN `_run_daily_sync` (L12856) + `@router.get('/api/cron/daily_sync')` (L13097) and dashboard.py is include_router'd FIRST → it SHADOWS cron.py.** So the paused copy never ran; the live dashboard.py copy kept syncing. (Same shadow pattern as the hemet endpoints — CLAUDE.md paired-changes.)

**Fix 2026-08-06 (lead):** in dashboard.py `_run_daily_sync`, right after the `sos = search_read(...)`, added **`sos = []`** (with a big comment) so the SO-sync loop processes nothing — the report email + downstream triggers still run. Re-enable by deleting that line. Restored John to $330 / Aug 5 8am first (unconfirm→rewrite lines→reconfirm→date_order back; was not invoiced).

**Lesson:** pausing/patching a `/api/cron/*` or any endpoint in cron.py is USELESS if dashboard.py defines the same route — dashboard.py wins. Always check dashboard.py for a shadowing copy. See [[project_status_label_vs_so_state]], [[project_confirmed_so_line_edit]].
