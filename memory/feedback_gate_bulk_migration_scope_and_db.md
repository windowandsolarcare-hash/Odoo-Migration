---
name: feedback_gate_bulk_migration_scope_and_db
description: "On a destructive BULK migration/sweep, Audit gates the SCOPE-derivation (which DB, population count, DJ-visible list) as a first-class §15 check — not just the sweep logic. App has TWO operational Postgres."
metadata:
  node_type: memory
  type: feedback
  originSessionId: 80181d32-eaf0-44dc-ad58-3287cd412a94
  modified: 2026-10-24T07:20:49.125Z
---

On a **destructive bulk migration/sweep** (e.g. the 2026-10-24 spam-VM backfill "option C"), byte-reviewing the sweep LOGIC is NOT enough. Audit must ALSO gate the **scope-derivation**: against which DB was the population counted, what is the count, and was DJ shown the ACTUAL list he's consenting to sweep? The consent must match the real target, not a census.

**Why:** the spam-VM backfill's sweep logic was correct and my byte-gate held on real data (0 customers swept — partner_id + resolve-backstop gates worked). But DJ approved "sweep all unknowns except 5" after reviewing **34** VMs, while the live inbox had **58** → 53 moved, incl. **12 local likely-real leads he never saw**. Root cause: the expected-count census was built against the WRONG Postgres. His consent was built on an undercount; the sweep did exactly what option C said on the real 58.

**THE APP HAS TWO OPERATIONAL POSTGRES (key infra fact):**
- **SMS_DB_URL** (`sms_store.py:45`) = the LIVE inbox / conversation store (the sms_store PG path). **Closed IP allowlist → a session/MCP CANNOT reach it** (render `query_render_postgres` errors "blocks all external connections"). This is where the backfill actually operated.
- **MEMORY_DB_URL** = `wsc-memory-pillar` (render pg `dpg-danl5vqjnfac7390g8g0-a`) = the ship_cards / scheduler-lock / msg-ledger DB. **Open allowlist → session-reachable** via render MCP. (The other listed PG `momscare-db` dpg-daocj0… is closed.)
- **Verification path when the target DB is unreachable:** the backfill mirrors its authoritative result dict to **Odoo `ir.config_parameter['wsc.vm.spam.backfill.c1']`** (`<iso> <json>` of {moved, moved_norms, kept_protected, kept_customer_backstop, scanned_vm, errors}). Odoo IS session-readable via JSON-RPC with the local key (`C:\Users\dj\_odoo_key_val.txt`, read FROM file, never inline). So even with the inbox DB closed, read the run's own recorded output from Odoo = true content-verify (used it to confirm 53/12/41/5/0 firsthand).

**How to apply:** for any bulk-mutation §15, before DJ consents, confirm (1) which DB the sweep reads (`_bulk_convs(_index_get())` → SMS_DB for the inbox), (2) the population count derived FROM THAT SAME DB, (3) DJ sees the real list/count — not a census built elsewhere. Post-run, verify by CONTENT via the Odoo result-param when the target DB is unreachable. Ties to [[feedback_odoo_verify_content_not_status]], [[feedback_data_location_odoo_vs_postgres]], [[feedback_cant_headlessly_seed_is_security_feature]], [[feedback_auditor_user_perspective_gapfinder]].
