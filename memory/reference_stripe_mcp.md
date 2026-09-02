---
name: stripe-mcp-configuration
description: "Stripe MCP is CONNECTED (2026-09-02) as a claude.ai connector — READ-ONLY, live account. Tools = mcp__claude_ai_Stripe__*, visible in a NEW session. Direct-key REST is the fallback."
metadata: 
  node_type: memory
  type: reference
  originSessionId: 62c57f62-79c0-4d47-9f2b-7e07e9e7d677
  modified: 2026-09-02T23:13:31.406Z
---

**Stripe MCP is connected as of 2026-09-02** — added by DJ as a **claude.ai connector** (Connectors panel, "Web" type, same family as Gmail/Google Drive/QuickBooks/Zapier), **READ-ONLY**, on the **LIVE** account "Windowandsolarcare" (Test-mode sandbox NOT enabled).

- **Tool prefix:** `mcp__claude_ai_Stripe__*` (claude.ai-connector naming). If deferred, load with `ToolSearch("stripe")` first.
- **A connector added mid-session is NOT visible to that session** — the tool list is fixed at session start. Use it from a **fresh session**. (Verified: the session where DJ enabled it could not see the tools.)
- **Read-only by design** — good. Any actual money move (charge/refund) still goes through the app + Operator, never a raw MCP/API write. See [[feedback_assistant_use_app_workflow_not_raw_api]].

**History / correction:** an earlier version of this note claimed a `@stripe/mcp` server was configured in `C:\Users\dj\.claude\mcp.json` "needing a restart." That was FALSE (no such server; config file is `.claude.json`) and cost a session real time — see the 2026-09-02 Hollenbeck incident. It is now genuinely installed, but as a claude.ai connector, not a local npx server.

**Fallback if the MCP tools aren't present:** direct Stripe REST — read the live key from Google Drive **Saunders Vault** → doc "Stripe" (or local `C:\Users\dj\_stripe_key_val.txt`), then `GET https://api.stripe.com/v1/charges?created[gte]=<epoch>&limit=100` with `Authorization: Bearer <key>`. Find a customer's payment by **amount + date** (billing name may be misspelled; billing email = the business email). Read the key FROM THE FILE — don't inline the `sk_live_` token in a shell command (auto-classifier blocks it). See [[project_stripe_payments_not_reconciled_to_odoo]] and the PAYMENT LOOKUP playbook in CLAUDE.md.
