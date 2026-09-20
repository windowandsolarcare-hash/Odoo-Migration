---
name: feedback_data_home_odoo_vs_postgres
description: "★ STANDING ARCH RULE (DJ 2026-09-20): money/business record-of-truth → Odoo; app/operational/derived/high-write data → indexed Render Postgres. Convert blobs that make sense."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5149109f-9ad5-4a25-9f72-06b18b7f302b
  modified: 2026-09-20T07:59:18.452Z
---

★ **DJ adopted this as the official standing architecture rule (2026-09-20).** For every "where should this data live?" decision:

- **→ Odoo:** money and business **records-of-truth** — accounting, invoicing, payments + reconciliation, **Sales Orders** (jobs), customer/property master records, multi-company (W&SC + Cheryl + Saunders Printing), financial reporting. Do NOT move these (that's the ruled-out "full migration off Odoo" = rebuild working, regulated accounting).
- **→ indexed Render Postgres:** app‑specific **operational / derived / high‑write** data — memory (Pillar + DJ's memory, done A35/A36), inbox summaries (done), and the rest of the blob stores per PERFORMANCE_AUDIT.md (floatnotes, feed, ideas, etc.).

**Why:** DJ 2026-09-20, after the Memory→Postgres speedup. Root cause of ALL the recurring speed pain (429s, whole-blob load/rewrite, the ir.config_parameter KV hack, N+1s) = the Odoo **SaaS plan blocks custom models**, so app-data got crammed into Odoo's config table. That tax lands entirely on APP-DATA, never on the accounting core. So keep Odoo lean for money; move app-data to Postgres. Full analysis: `3_Documentation/ODOO_STRATEGY_ANALYSIS.md`.

**How to apply:**
- **SEAM HYGIENE (critical, no split-brain):** Postgres app-data may **REFERENCE an Odoo id**, but NEVER duplicate money/master data. One source of truth per fact.
- **Speed on record-heavy screens (e.g. SO-driven schedule/HUD/today's-jobs):** the record stays in Odoo; build a **Postgres summary/index CACHE** that references the Odoo record id (same pattern as the inbox summary read-model). The SO itself never leaves Odoo.
- **Playbook** = the proven A35/A36 migration (migrate-first + verify + rollback; money never moves).
- **Pace:** DJ does it one-at-a-time-see-results. Convert per the audit's prioritized list; no build until DJ picks the next.
- Related: [[feedback_durable_foundation_over_shortcut]], [[feedback_planning_constraints]] (no new Odoo seats / no custom models — the exact constraint this rule works around).
