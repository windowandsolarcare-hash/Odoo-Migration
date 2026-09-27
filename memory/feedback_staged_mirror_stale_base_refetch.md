---
name: feedback_staged_mirror_stale_base_refetch
description: "A staged/mirror file built before a later ship is STALE-BASE — pushing it reverts that ship. ALWAYS re-fetch LIVE + re-apply at merge, never push the mirror."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 93ae5c9a-b2db-49a9-8fa8-84d13000c2ae
  modified: 2026-09-27T22:07:10.042Z
---

**THE TRAP (near-catastrophe, 2026-09-27):** In the stage-and-hold deploy model, work is built + mirrored to
`3_Documentation/review/...` and held for DJ's "deploy". A mirror built at time T does NOT contain changes
that shipped to that same file AFTER T. Pushing the stale mirror at merge time **reverts** everything that
landed in between. Real case: `review/usage_pace/main_built.py` was built BEFORE the numInstances=2
advisory-lock guard shipped (commit f51206cb). It had NONE of `_sched_singleton` / the 20 wrapped add_jobs /
`_READY` / the deepened `/healthz`. Pushing it would have reverted the guard → the scheduler double-fires at
2 instances → **double customer texts** — the exact disaster the guard prevents. Lead caught it at QC.

**Why:** every session, and DJ's "deploy" trigger, can be hours/many-commits after a mirror was built.
Shared/high-traffic files (`main.py`, `v2_apps.js`, `authz.py`, `dashboard.py`, `reminders.py`, `memory_store.py`)
are the danger — several in-flight branches touch them, and each ships on its own schedule.

**THE RULE — at MERGE/PUSH time, NEVER push a staged mirror file. Re-fetch LIVE + RE-APPLY the transform:**
- Treat every review-mirror as a QC artifact + a record of *what change to make*, NOT the bytes to ship.
- At merge: `gh api .../contents/<path>` LIVE → apply ONLY your change (small string insert / regex) onto the
  fresh content → verify a **clean diff vs LIVE** (only your lines, 0 unexpected removals) → then commit.
- **Verify the OTHER guy's changes survived:** grep for the tokens of any recently-shipped feature on that
  file (e.g. after re-applying to main.py, confirm `_sched_singleton` ×N + the 20 `add_job(_sched_singleton`
  wraps + `/healthz` 503 are STILL there). A clean +N-line diff proves nothing reverted.
- New files (no live version) are safe to take from the mirror as-is (no drift possible).
- This is also why the launcher/label collisions resolve: re-fetch-live means v2_apps.js carries whatever
  label shipped meanwhile (e.g. the KB "Knowledge Base" rename), not the mirror's stale "Memory".

**How to apply:** pre-push gate 1 ("fetch the live file first, never edit a stale copy") applies to STAGED
mirrors too — a mirror is a stale copy the moment anything else ships to that file. When you flag "re-fetch
live at push" (correct instinct), actually DO the re-fetch+re-apply+diff-verify, don't push the mirror.
Ties to [[feedback_regression_guard_pushes]], [[feedback_local_vs_deployed_drift]], [[feedback_verify_collection_and_live_pipe]].
