---
name: project_accounting_next_priorities
description: "★ DJ-set Accounting priorities to surface when he asks 'what do we need to do' (set eve of 2026-10-11, for 2026-10-12+). #1 Set up Saunders Printing on Odoo. #2 Investigate the additional info the old-accountant session gave + figure out the migration state (don't delete anything irreversible)."
metadata:
  node_type: memory
  type: project
  originSessionId: d70db154-b1dd-424c-b2a7-f87afca1d69d
  modified: 2026-10-12T07:36:19.195Z
---

**DJ asked (2026-10-11 night) to be REMINDED of these when he next asks "what do we need to do" (i.e. 2026-10-12+).** Surface this list proactively on that ask.

**#1 — SET UP SAUNDERS PRINTING ON ODOO (one of the most important).** Build/finish Saunders Printing (Odoo company 3) in Odoo — its books + its own Schedule C (DJ self-files two Schedule Cs: W&SC + Saunders Printing, both sole-prop under his 1040). Plan + facts in [[project_saunders_printing_migration_plan]]: company 3; two accounts (Amex 11003 = expenses, 2025 business ~$12,290 already pulled, + Chase checking = revenue + debit); ~$20k/yr revenue, ACCRUAL basis (watch cross-year invoice/paid); build 2024 first then 25+26; old QuickBooks 2010 Desktop (Parallels VM, no API — likely skip for taxes, build from Amex + Chase + 2024 template); DJ will download the Amex + Chase data. NOTE Amex also carries the Apr-15-2026 $4,000 US Treasury payment = 2025 federal credit, and the Apr-15-2025 $3,800 = 2024.

**#2 — FIGURE OUT THE OLD-ACCOUNTANT'S ADDITIONAL INFO + THE MIGRATION STATE.** The prior Accounting session ("old act" [9dec17] as of 2026-10-11, did most of the earlier work) gave additional information to figure out. GOAL: understand what's going on with the QB→Odoo migration (it looks like it didn't run right — see the Workiz double-import proof in [[project_2025_schedule_c_categorized]]). GUARDRAIL (DJ 2026-10-11): **do NOT delete anything unless it's reversible** — investigate and understand first; any money/book change goes through Operator or a DJ-approved batch, never raw RPC by Accounting ([[feedback_assistant_use_app_workflow_not_raw_api]]). The definitive validation is the account-by-account Odoo-vs-QuickBooks 2025 tie-out (the Workiz tie-out method applied to every account).

**Context:** this is the tax-first / finish-the-migration push. Tax deadline ~Oct 15 2026. See [[project_dj_tax_filing_2025]], [[project_accounting_migration_unfinished]], the Accounting handoff doc (saunders-render-app/3_Documentation/ACCOUNTING_SESSION_HANDOFF.md).
