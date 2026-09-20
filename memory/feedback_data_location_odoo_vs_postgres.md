---
name: feedback_data_location_odoo_vs_postgres
description: "★ STANDING RULE (DJ adopted 2026-09-20, board I8) — money/business-record-of-truth lives in Odoo; app operational/derived/high-write data lives in Render Postgres. Every \"where does this data live?\" call follows this."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d847a036-234d-4c73-9eca-62500cfee8a7
  modified: 2026-09-20T08:00:43.669Z
---

**DJ's adopted architecture (2026-09-20, board I8 — see `saunders-render-app/3_Documentation/ODOO_STRATEGY_ANALYSIS.md`).** The decision rule for where ANY data lives:

- **→ ODOO** if it's **money or a business record-of-truth**: invoices, payments + reconciliation, sales orders, customers, properties, journals, accounting, multi-company financials (W&SC/Cheryl/Saunders). Odoo is expensive + RISKY to replace here and it's NOT where our pain is — keep it as the money/records system-of-record.
- **→ RENDER POSTGRES** if it's **app operational / derived / high-write data**: memory (done A35/A36), conversations, ideas, feed, notes-metadata, floatnotes, caches, derived views. This is where the speed/flexibility tax lived (the ir.config_parameter JSON-blob hack forced by SaaS "no custom models" → 429s, whole-blob rewrites, N+1s). Postgres = a schema we control, indexed, queryable directly (incl. by Claude).

**Why:** DJ's frustration with Odoo is REAL but SPECIFIC — it's the app-data tax, not Odoo's accounting/multi-company core. The fix is "stop using Odoo as the app's database," NOT "leave Odoo." (Full options a/b/c + reasoning in the strategy doc; DJ chose (b) — Odoo lean + Postgres for app-data.)

**★ SEAM HYGIENE (the one risk to manage — no split-brain):** Postgres app-data may REFERENCE an Odoo record by id (a conversation → partner_id/SO id), but must NEVER duplicate or become a second source-of-truth for money/master data. **One owner per fact.**

**SO-derived caches (clarified 2026-09-20):** Sales Orders STAY in Odoo. But derived read-heavy VIEWS built from SOs (schedule list, HUD counts, today's-jobs) CAN be Postgres summary/index caches that reference the Odoo SO id + carry only non-authoritative summary fields — same playbook as the inbox summary ([[project_inbox_summary_readmodel_a5]]). ⚠ Unlike the inbox (single write chokepoint), SOs write via many flows, so an SO-derived cache MUST state a FRESHNESS strategy (invalidate/refresh-on-SO-write, rebuild-on-cadence, or live-read-with-cache) so it never goes stale vs Odoo.

**How to apply:** conversions run one-at-a-time via the proven migrate-verify-rollback playbook ([[project_memory_pillar_postgres_a35]]); each is a self-contained step, DJ picks the pace. Ordered blob-conversion list is in the perf audit + AGENT_MAIL. NOT candidates: scalars/flags/cursors, replace-whole caches, idempotency dedupe rings, per-entity-keyed blobs (one record per key = no whole-collection savings). See [[feedback_planning_constraints]] (the no-custom-models/no-new-seats constraint this rule works around), [[feedback_durable_foundation_over_shortcut]].
