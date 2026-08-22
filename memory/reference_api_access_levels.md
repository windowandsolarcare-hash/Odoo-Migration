---
name: API Access Levels — Odoo vs QuickBooks vs Workiz
description: Comparison of what Claude can actually do in each system — important for knowing what's possible when DJ asks for something
type: reference
originSessionId: d77fc6bd-119f-4192-b2c8-a8592257d2b6
---
## Odoo — Virtually Unlimited Access
- Connects via JSON-RPC and XML-RPC APIs
- Every model, every field, every record is accessible
- Can read, create, edit, and delete anything
- Covers: invoices, journal entries, contacts, sales orders, tasks, bank statements, assets, reports, accounting config, chart of accounts, payment journals, bank feeds, activities, documents — everything
- If Odoo can do it through its UI, Claude can do it through the API
- Only exceptions: things requiring physical browser interaction (OAuth logins, file uploads via browser dialog)
- **Bottom line: DJ can ask Claude to do anything in Odoo and expect it to be possible**

## QuickBooks — Very Limited
- Access only through the QB MCP (~8 tools)
- Reporting surface only — not a full API
- Can pull P&L and cash flow summaries, import transactions, update company profile
- Cannot: read individual transactions, edit/delete records, access balance sheet, drill down into categories, reconcile, access vendor/customer lists
- **Bottom line: QB MCP is good for a quick P&L summary only. Not useful for data migration or granular work.**

## Workiz — Moderate but IP-Restricted
- Full Workiz API exists with job CRUD endpoints (create, read, update, delete)
- IP-restricted — blocks calls from local machines (403 Forbidden)
- Claude can only reach Workiz by proxying through a temporary Odoo server action
- Covers: jobs, clients, some custom fields, job status updates
- Does NOT cover: payment history endpoints, financial reporting, full client history
- Rate limit: ~30 calls before HTTP 429 — must sleep 15-30 seconds between batches
- Auth secret required in every URL: `?auth_secret=sec_334084295850678330105471548`
- **Bottom line: Claude can read and write Workiz jobs but it's indirect and rate-limited. Payment history comes from CSV exports, not the API.**

## Practical Implication
When DJ asks "can you do X?" — the answer is almost always yes if X involves Odoo. For QB or Workiz, the answer depends on whether the specific operation is supported by their limited interfaces.
