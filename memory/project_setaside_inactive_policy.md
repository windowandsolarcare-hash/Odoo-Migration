---
name: project_setaside_inactive_policy
description: "Set-aside / \"make inactive\" policy — Moved = archive only; Passed away = archive + Do Not Call. \"Inactive\" means Odoo archived (active=False) so they vanish from every forward-looking list. Same flow in Analytics + Reactivation."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0ce92b3e-6626-4807-9e45-23722f7fcba2
---

DJ's policy for parking a customer he won't deal with again (set 2026-06-11):

- **"Inactive" = Odoo archived (`active=False`)**, NOT a field value. The `x_studio_activelead` selection only has Active / Lead Only / Do Not Contact — there is no "Inactive" value. Archiving makes the contact disappear from EVERY forward-looking list (reactivation, analytics lapsed, blasts, scheduling) because Odoo's default `active_test` hides archived records.
- **Moved** → `active=False` only. Keep activelead = 'Active' — **moved customers stay OFF the Do Not Call file** (kept clean; a mover may come back).
- **Passed away** → `active=False` **AND** `x_studio_activelead='Do Not Contact'`.
- **Restore (un-set-aside)** → `active=True` + activelead='Active' (brings them back to working lists, clears DNC).
- Other set-aside reasons (Too far, Price complaints, Hard to deal with, Low value, Not worth the time, One-time job) = **soft park only** — stored in the `analytics.setaside` ir.config_parameter, hidden from the lapsed list, NO archive, NO DNC. Only Moved/Passed away touch the partner record.

**The set-aside bucket is SHARED both ways (fixed 2026-06-11):** the reactivation candidates endpoint (dashboard.py) reads `analytics.setaside` and excludes those pids via `['id','not in', setaside_ids]`. So a soft-park reason (Hard to deal with / Too far / etc.) that does NOT archive the contact still removes them from BOTH the Analytics lapsed list AND Reactivation. Before this fix, soft-parked contacts (e.g. Cheryl Robinson 23630, "Hard to deal with") still leaked into reactivation. Reverse direction already worked because reactivation's "Set aside" writes to the same bucket.

**Where it lives:** the single source of truth is the Customer Analytics endpoint **`POST /owner/api/analytics/setaside`** (`routers/owner/analytics.py`, `api_setaside_set`). Set-aside membership + reason are stored as JSON `{pid: reason}` in ir.config_parameter key `analytics.setaside`. Reactivation reuses this SAME endpoint (reactivation.html `confirmAside()` posts `{pid, on, reason}`) so behavior is identical in both screens.

**Reactivation UI (2026-06-11):** the old "🚫 Inactive" button was BROKEN — its onclick injected `${JSON.stringify(c.name)}` (double-quoted) inside a double-quoted `onclick="..."`, breaking the handler for every card. Replaced with "💤 Set aside" → reason bottom-sheet (chips matching Analytics: Moved/Passed away/Too far/…) → posts to analytics setaside. Old dead dashboard.py routes `/api/reactivation/mark_inactive` + missing `mark_active` are no longer used.

**DNC + "true customers is present" refinement (2026-06-11):** present/forward KPIs exclude PARKED = set-aside bucket OR DNC, where DNC = `x_studio_activelead=='Do Not Contact'` OR `phone_blacklisted` (STOP). This now includes the **true_customers** headline card (DJ decided it's a PRESENT KPI = current customer base, not all-time). `base['true_customers']` = present (excl parked+DNC); `base['true_customers_all']` = all-time, kept as the denominator for historical ratios (rev/customer, avg jobs, lifetime_repeat_pct) and the base of retention/Pareto/leaderboard. Live numbers after change: true_customers 507 present / 585 all-time, active 355, lapsed 152, active_pct 70. Implemented in analytics.py reconciliation block via `_parked(c)`.

**STOP now archives (2026-06-11):** the Workiz STOP handler (live = `ir.actions.server` id **954**, triggered by `base.automation` id 6 webhook uuid f64d0bc1-…) sets blacklist + `x_studio_activelead='Do Not Contact'` + marks opp Lost AND now `contact.write({'active': False})` (archive) as a final step. Two-step deploy done: GitHub `1_Production_Code/odoo_webhook_stop_handler.py` + live action 954 patched. STOP customers were already excluded from present KPIs + reactivation via DNC; archiving makes them fully inactive too.

**Analytics KPI rule (2026-06-11):** set-aside contacts are excluded from PRESENT/FORWARD KPIs (active, lapsed, upcoming, leads, active_repeat — in analytics.py `compute`, the reconciliation block) but KEPT in HISTORICAL totals (true_customers, revenue, retention by year, leaderboard, Pareto, mix) because they WERE customers. Rationale (DJ): "active/lapsed look at today and the future → exclude; backward-looking data → keep." The raw `customers`/`leaderboard` arrays still contain set-aside contacts (historical); the analytics.html FRONTEND filters them from the working list via `!SETASIDE.has(pid)`. Analytics is served from a CACHE (`analytics_customer_cache`); after changing compute logic, POST `/owner/api/analytics/recompute` to refresh (cron also recomputes 5am).

**IMPORTANT — archiving a CONTACT does NOT remove them from analytics true-customers:** the analytics rolls customers up via active **Property** child records + Done SOs, not the contact's active flag. Archived contacts whose Property children are still active still appear in true_ids. To hide from PRESENT KPIs, they must be in the set-aside bucket (the KPI exclusion keys on `setaside_ids`). Richard Rodner (23575) was DNC but NOT set aside / NOT archived → showed as Active; fixed by setting him aside as Moved.

**One-time cleanup done 2026-06-11:** went through the existing 56 set-asides — archived all 6 "Passed away" (+DNC) and all 24 "Moved" (cleared the 6 that were wrongly on DNC). The other 26 (soft-park reasons) left untouched. See [[project_customer_analytics_datamodel]] [[project_do_not_contact_forward_looking]] [[project_reactivation_route_shadowed_in_dashboard]].
