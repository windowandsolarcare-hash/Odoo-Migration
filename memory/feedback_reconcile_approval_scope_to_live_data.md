---
name: feedback_reconcile_approval_scope_to_live_data
description: "When a human approval is SCOPED TO A DATA SET ('sweep the N I reviewed'), the gate must reconcile the code's ACTUAL scope against the LIVE data — never a proxy/queryable copy. Verifying the CODE firsthand is not verifying the DATA PREMISE firsthand; §15 requires both. Burned 2026-10-24 by the spam-VM backfill over-reach (census off a stale DB)."
metadata:
  node_type: memory
  type: feedback
  originSessionId: c357000c-2b48-423f-90ce-2e1b8f1f9669
  modified: 2026-10-24T07:19:12.793Z
---

**Burned 2026-10-24 (spam-VM backfill, option C):** the sweep was GREEN'd by Lead + Audit on CORRECT code ("file all unknown-number VMs except the 5 protected") plus a census of "34 unknown VMs" that DJ reviewed. The census was built by querying **wsc-memory-pillar (MEMORY_DB_URL — the scheduler-lock DB, a STALE subset copy)**, NOT the **live inbox (SMS_DB_URL — a different Postgres that BLOCKS external session connections** so the in-process sweep reached it but a session census cannot). Live had **58** unknowns → the one-shot swept **53**, over-reaching ~24 convs DJ never reviewed — **12 of them LOCAL service-area numbers (442/760) = likely real customers buried in Spam.** Fully reversible (nothing deleted), contained via a one-shot Not-spam reversal of the 12 local, but a real over-reach that both review gates missed.

**Root cause:** the CODE was verified firsthand; the DATA PREMISE (the "34" the human approval was scoped to) was taken as given. DJ approved "sweep THE 34 I saw minus 5"; the code was "sweep ALL unknowns minus 5" — equivalent ONLY if the census == live unknowns. It wasn't.

**How to apply:**
1. For any destructive/bulk op scoped to "the N DJ reviewed," **firsthand-reconcile N against the LIVE store before it runs** — the code's actual scope must equal the human-approved scope.
2. If the live store **can't be queried from a session** (ext-blocked like SMS_DB_URL): that's a FLAG, not a pass. Route the census through the ONLY working read path (the app/DJ), or treat the op as higher-risk and have DJ confirm the actual LIVE count — never substitute a stale proxy DB because it's the only one you can reach. See [[feedback_cant_headlessly_seed_is_security_feature]].
3. **Verifying the CODE firsthand ≠ verifying the DATA PREMISE firsthand; §15 requires BOTH** ([[feedback_audit_stamp_confirm_firsthand]]).
4. Know your stores: [[feedback_data_location_odoo_vs_postgres]]; SMS_DB_URL (live inbox) ≠ MEMORY_DB_URL (wsc-memory-pillar, stale lock-DB). Ties to [[feedback_verify_collection_and_live_pipe]].
