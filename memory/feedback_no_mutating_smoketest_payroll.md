---
name: feedback_no_mutating_smoketest_payroll
description: Never POST to a live payroll/mutation endpoint just to confirm a route exists — it can change real records. clockout_crew with empty body clocked out a live shift during a deploy smoke test.
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 44a83d54-0213-43e9-adfe-064ef69f5445
---

**Why:** 2026-06-08, after deploying the clock rebuild, I "smoke-tested" the new `/owner/api/payroll/clockout_crew` route by POSTing an empty body `{}` to confirm it wasn't a 404. The endpoint falls back to today's `crew.today.<date>` snapshot when no `employee_ids` are given — so it actually clocked out Danny (emp 2), truncating his still-open shift #103 (check_in 08:46 PT) at the test time. I had to reopen it (`hr.attendance write check_out=False`) to restore the prior state.

**How to apply:**
- To confirm a route loaded after deploy, use the **Render deploy status** (MCP `get_deploy` → `status:"live"` vs `update_failed`) — that already proves the file imported and routes registered. Do NOT exercise a mutating endpoint for this.
- If you must hit an endpoint, pick a **read-only** one (e.g. `/api/payroll/status?employee_id=...`) — never a POST that writes.
- Payroll endpoints often **fall back to live data** (crew snapshot, "today") when given empty/partial input. Empty body ≠ harmless no-op.
- General rule: treat every `/api/payroll/*` POST, and any clock/invoice/payment write, as production-affecting. Test those only with data YOU created and will clean up, or not at all. [[project_clock_system_rebuild]]
