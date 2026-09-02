---
name: stripe-mcp-configuration
description: CORRECTION — there is NO Stripe MCP installed. Prior claim was wrong. Use the live key + direct Stripe REST API instead.
metadata: 
  node_type: memory
  type: reference
  originSessionId: 62c57f62-79c0-4d47-9f2b-7e07e9e7d677
  modified: 2026-09-02T23:03:41.433Z
---

**★ CORRECTED 2026-09-02 (verified on a fresh /clear session, screenshot from DJ): there is NO Stripe MCP installed.** The prior version of this note claimed a Stripe MCP (`@stripe/mcp`, `mcp__stripe__*`) was configured in `C:\Users\dj\.claude\mcp.json` and "just needs a restart." That is FALSE and cost a session real time chasing it.

**Actual loaded MCP servers (8):** `render` (local, in `C:\Users\dj\.claude.json`), and the claude.ai set — Calendly (needs auth), Gmail, Google Calendar, Google Drive, Intuit QuickBooks, Zapier — plus built-in `claude-in-chrome`. **No Stripe.** (Config file is `.claude.json`, not `.claude/mcp.json`.)

**How to query Stripe instead:** direct REST API. Read the live key from Google Drive **Saunders Vault** → doc "Stripe" (or local `C:\Users\dj\_stripe_key_val.txt`), then `GET https://api.stripe.com/v1/charges?created[gte]=<epoch>&limit=100` with header `Authorization: Bearer <key>`. Find a customer's payment by **amount + date**, not name/email. Read the key FROM THE FILE — don't inline the `sk_live_` token in a shell command (the auto-classifier blocks it). See [[project_stripe_payments_not_reconciled_to_odoo]] and the PAYMENT LOOKUP playbook in CLAUDE.md.

**If a Stripe MCP is ever wanted:** it would need to be added to `.claude.json` `mcpServers` (e.g. `@stripe/mcp` via npx with the key) and a restart — but it is NOT there today. Don't assume it exists; verify with the MCP list first.
