---
name: No guessing on Odoo field names
description: Never guess at Odoo field names. Verify in CLAUDE.md field table, memory files, or by querying Odoo directly before using any field.
type: feedback
originSessionId: 96c7eadf-7840-4091-9290-6d3aed1806c8
---
Never guess at Odoo field names — not for sale.order, res.partner, or any model.

**Why:** DJ introduced `commercial_partner_id` on sale.order without verifying it exists. Field was invalid — broke the live stale SOs endpoint immediately after deploy. This codebase took months to build and bad field guesses cause real outages.

**How to apply:**
1. Check CLAUDE.md field table first
2. Check memory files (project_*.md) for known fields
3. If not found: query Odoo via JSON-RPC (`search_read` with the field, or `fields_get`) before writing any code
4. Never assume a field exists because it "should" exist in standard Odoo — this instance has heavy customization and some standard fields are absent (e.g. `account.payment` has no `ref` field in Odoo 19)
