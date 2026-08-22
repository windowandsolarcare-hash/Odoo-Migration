---
name: project_analytics_audit_base
description: "Customer Analytics (analytics.py) audited 2026-07-25 — every RAW number ties to Odoo exactly. Fixed two DISPLAY bugs: unified the customer base to DNC-only exclusion (set-asides now COUNT; base 492→545) so all cards+ratios reconcile, and fixed Active-repeat % to active_repeat/active (was wrongly the active rate)."
metadata:
  node_type: memory
  type: project
  originSessionId: 44fd339a-14fd-42e2-adef-f1ae97081400
  modified: 2026-07-26T05:33:41.516Z
---

**2026-07-25 (DJ: "look closely at customer analytics one by one, see if it's accurate").** Audited every KPI against live Odoo.

**Raw data = 100% accurate** (independently recomputed from Odoo, all matched exactly): properties 919, qualifying Done jobs (company 1, workiz_status Done, amount_total>0) = 2504, total_revenue $432,443, true-customers-all 596, contacts 700, lifetime_repeat 358, avg_job_value $173, jobs/cust 4.2. Active = 30-month recency on the most-recent job, rolled up to the parent CONTACT (Workiz dupes each address as fresh property records; per-property would falsely split/lapse a customer — that's why the unit is the contact/parent_id).

**Two DISPLAY bugs found + fixed (data was fine, the framing was wrong):**

1. **Inconsistent base.** The "True customers" card showed 492 (excluded BOTH set-asides AND Do-Not-Contact), but the ratios (Repeat %, Rev/customer, Jobs/customer) divided by 596 (all-time), and the two on-screen percentages used different denominators. DJ's call: ONE base = **exclude Do-Not-Contact only; INCLUDE set-asides** (they're still customers — set-aside just parks them from the reactivation flow). New base **545** (= 596 − 51 DNC; the 70 set-asides stay counted, 17 overlap). Set-aside counts (`_get_setaside`) vs DNC (phone_blacklisted OR x_studio_activelead='Do Not Contact'): among 596 true customers → 51 DNC, 70 set-aside, 17 both. **Impl (analytics.py commit cfa37ec):** `_parked(c)` changed from `pid in setaside_ids or c['dnc']` → `bool(c['dnc'])`; ratios (`active_pct`, `lifetime_repeat_pct`, `revenue_per_customer`, `avg_jobs_per_customer`) recomputed over `base['true_customers']` (545) instead of the all-time 596. Now Active(364)+Lapsed(180)+Upcoming(1)=545=True, and every ratio divides by 545. Lifetime revenue ($432,443), total jobs (2504), avg job value ($173) stay ALL-TIME (historical "ever" totals). Set-asides still show as the `💤N` sub-badge on Active/Lapsed.

2. **Active-repeat % was the wrong field.** The "Active repeat" card paired the count (283) with `active_pct` (the overall active rate 73%), which is unrelated. Added `base['active_repeat_pct'] = active_repeat/active` and pointed the card at it (v2_analytics.html commit 2edbede). Now "286 · 78.6%" = of active customers, share who are repeat.

**New live values after recompute:** True 545, Active 364 (66.8%), Lapsed 180, Upcoming 1, Leads 101, Repeat 358·65.7%, Active-repeat 286·78.6%, Lifetime rev $432,443, Rev/cust $793, Avg job $173, Jobs/cust 4.59, interval 268d, lifespan 33mo. **Analytics is CACHED (recompute at ~05:00 daily or via POST /owner/api/analytics/recompute);** the page won't reflect code changes until a recompute runs. See [[project_button_color_inherit_darkmode]], [[feedback_no_guessing_on_fields]].
