---
name: project_memory_read_fail_open_phantom_empty
description: "Memory-page \"No decisions yet\" scare (A37) = _load fail-open-to-[] on a transient Odoo 429, NOT data loss. User reads must distinguish error from empty."
metadata: 
  node_type: memory
  type: project
  originSessionId: d847a036-234d-4c73-9eca-62500cfee8a7
  modified: 2026-09-20T03:08:21.815Z
---

**Incident A37 (2026-09-19):** DJ's Memory page (v2_memory.html) suddenly showed "No decisions recorded yet" — looked like his decisions store had been wiped (fear was a whole-blob clobber from tonight's stacked deploys + newly-live fleet hooks). **It was NOT data loss.** Raw read of `ir.config_parameter` key `wsc.memory.decisions` = 61 valid-JSON records intact (38.9 KB, all company_id=1, newest 2026-09-18). The read path self-recovered on reload.

**Root cause:** `memory_store.py` `_load` (~:44-45) does `except Exception: return []` — it fails OPEN to an empty list on ANY transient Odoo error. Trigger = a transient Odoo **429** (rate-limit) during stacked deploys + fleet-hook traffic on the 0.5-CPU worker. The empty [] then rendered as the "nothing yet" empty-state = looked identical to data loss.

**NOT the cause (ruled out):** company_id filter (records are int 1, `_COMPANY` is int 1 — match; deployed-logic sim returned 59). Not a clobber. Not the fleet hooks — they write DIFFERENT param keys (`wsc.memory.fleet_decisions` / `solved_errors`, company_id='fleet'), never `wsc.memory.decisions`.

**Why:** a read that swallows an error into an empty result is indistinguishable, at the UI, from "you genuinely have nothing" — on a USER'S OWN data that's a false "your data vanished" scare. Fine as fail-open posture for the fleet BYPRODUCT capture (losing one observation on a blip is OK); NOT fine for a user-facing read.

**How to apply — the durable principle (error ≠ empty on user-facing reads):**
1. `_load` must SIGNAL read-failure distinctly (raise / sentinel), not swallow to [] — callers must tell "threw" from "genuinely empty."
2. Memory GET endpoints (get_decision + meetings/etc.) return `{ok:false, error:'read_failed'}` on that; v2_memory.html renders "Couldn't load — tap to retry" + auto-retry once, NEVER the "nothing yet" copy.
3. Bounded retry/backoff on the Odoo `get_param` for 429s (a couple of short-backoff retries).
4. Carry the SAME guard into the Postgres read path post-A35-flip (a PG blip can also read empty).

**★ Migration corollary (A36):** the migration COPY read has the identical fail-open — a 429 mid-copy would read [] and migrate an EMPTY store. Migration read MUST retry AND verify count>0 vs the Odoo count before trusting; abort the copy if a store that should have records reads empty. Migrate stays HELD until that guard is in.

Ownership: fix in memory_store.py + v2_memory.html (both Builder-2's held files during the A35/A36 Postgres move). The Postgres move itself removes the 429-prone Odoo read for migrated stores, but the error≠empty contract is needed regardless. See [[feedback_odoo_verify_content_not_status]], [[feedback_durable_foundation_over_shortcut]]. Odoo 429 under stacked deploys / loop-hammering is a known infra gotcha (space out calls).
