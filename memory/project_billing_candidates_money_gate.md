---
name: project_billing_candidates_money_gate
description: Billing candidates SWR money-gate — _billing_mutated must be called with its KIND (so_id/noop/fresh) on every billing write
metadata:
  node_type: memory
  type: project
  originSessionId: 4a3934c7-cb02-4949-8807-74eee8a68861
  modified: 2026-09-27T16:55:46.623Z
---

**The billing-candidates cache (`specialist_billing.py` `_candidates_cached`) is a money gate: an acted/paid job must NEVER re-show.** SWR: fresh→instant, TTL-stale→last-good+bg refresh. P1 (2026-09-27, Lead option B) capped the previously-UNCAPPED synchronous rebuild leg (which could hang a billing card-tap → 502 under Odoo-slow):

- `_billing_mutated(so_id=None, noop=False, fresh=False)` bumps `_CAND_MUT` AND records the mutation KIND in `_ACTED_LOG[mut]` (int so_id | 'noop' | 'fresh'; bounded 512).
- **Every state-changing billing write MUST call it with the correct KIND** (completeness = the money-safety): **REMOVAL → `so_id=`** (send_zelle, send_cc, reschedule_later, hold, dismiss, settle); **ACK-only → `noop=True`** (mark_seen, mark_seen_one); **DATA-change / force-fresh → `fresh=True`** (sweep, sync_job — sync_job is modify-in-place = corrected $, NOT a removal, so it must NOT be filtered). A write that bumps mut WITHOUT a kind reads back as unaccounted (None).
- `_candidates_cached` mutated leg: if every mutation since the cached mut is `int`/`'noop'` → serve last-good FILTERED of the removed so_ids INSTANTLY (non-blocking, money-safe); if ANY is `'fresh'`/`None` → DEGRADE to synchronous-fresh `detect_candidates` (never stale/wrong). Cold/key-change → `_cand_cold_capped` (kick + wait ≤ `_CAND_COLD_CAP`=8.0s, matches feed `_LIVE_COLD_CAP`, else last-good/empty).

**Why:** a forgetful future billing write = a double-collect/double-ask bug. **How to apply:** any NEW `@router.post` under `/api/billing` that changes state MUST call `_billing_mutated(<kind>)` — pass `so_id` if it removes a job, else `noop`/`fresh`. Regression guard: `2_Testing_Tools/test_billing_mutated_kinds.py` asserts the branch decisions (run it after touching the kind-map or the `all()` guard).

Known LOW-PRI gap (2026-09-27): `api_job_zelle_request`→`_zelle_request_core` arms the awaiting tracker (job leaves candidates, `detect_candidates:239` `if so_id in awaiting: continue`) but does NOT call `_billing_mutated()` → a brief double-ASK window until SWR refresh (double-ask, not double-charge). Fix = add `_billing_mutated(so_id=so_id)` there. `2_Testing_Tools/` push redeploys → see [[feedback_testing_tools_not_build_filtered]].
