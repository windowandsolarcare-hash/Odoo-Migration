---
name: feedback_verify_collection_and_live_pipe
description: A drift/compile/node/AST-add-only pass does NOT prove an entry landed in the RIGHT collection — verify membership + prove the live end-to-end pipe before trusting a config/exempt-list change.
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 11d2c5cb-9040-46fe-b04b-20ac84f0828f
  modified: 2026-09-23T15:51:48.573Z
---

When adding an entry to a config LIST/collection in a big file (e.g. `PUBLIC_EXACT` in authz.py, a router table, an allow-list), anchoring the insert to a nearby line can silently put it in the WRONG collection. On 2026-09-23 I added `/owner/api/telemetry/beacon` + `/rate` to the auth exempt list by anchoring to `'/owner/api/intake/products',` — but that entry lives in **TECH_GRANTED_OWNER**, not **PUBLIC_EXACT** (its closing `)` looked like PUBLIC_EXACT's). Result: the beacon was never exempt → the owner middleware 401'd the cookieless sendBeacon → telemetry silently non-functional.

**Why the usual gates missed it:** drift-diff showed pure add-only ✅, py_compile ✅, node --check ✅, even an AST "is it add-only" check ✅ — ALL passed, because the edit WAS valid and add-only. None of them checked *which collection* the entry joined. A regex membership test also lied (a non-greedy `.*?` stopped at the first `))`).

**Why:** structural gates prove syntax + no-clobber, not semantic placement. A misplaced-but-valid entry passes every static check.

**How to apply:**
- After editing a config collection, **verify membership semantically**: AST-parse the file, `eval` the specific assignment (with `frozenset`/`tuple` in scope), and assert `path in THE_RIGHT_SET` AND `path not in THE_WRONG_NEIGHBOR`. Don't trust line-proximity or a quick regex.
- For anything reachable over HTTP (auth exempt, a new route, a gate), **prove the LIVE end-to-end pipe post-deploy**: fire the real request and confirm the real effect (beacon POST → 204 → row appears in the DB), plus a control (a known-gated route STILL 401s = the exempt wasn't over-broadened; the mis-anchored neighbor still behaves). Lead's insistence on a live test beacon is what caught this — a green deploy + all-static-checks-pass is NOT proof the feature works.
- Belt: a boot log that SHOUTS the resolved state (e.g. "[telemetry] PG CONFIGURED via MEMORY_DB_URL") so a mis-wire is visible in the deploy log, not discovered via a false-empty view.

Related: [[project_billing_candidates_swr_money_gate]] (the source-audit-test idea — a machine check that every write bumps — is the same spirit: encode the semantic invariant as a test, don't rely on eyeballing). [[feedback_odoo_verify_content_not_status]] (HTTP 200 ≠ success — same "prove the effect, not the status" principle).
