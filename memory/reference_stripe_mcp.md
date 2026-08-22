---
name: Stripe MCP configuration
description: Stripe MCP server added to Claude Code — lets Claude look up payments, charges, customers directly from Stripe
type: reference
originSessionId: 55b3b70b-11bb-4b3a-958a-f4be4ab4e3c1
---
Stripe MCP configured in `C:\Users\dj\.claude\mcp.json` via `@stripe/mcp` npx package.

Live secret key: `[STRIPE_KEY — in Render env]`

**Requires Claude Code restart to activate** — MCP config is only read at startup.

After restart, tools load as `mcp__stripe__*` and can look up:
- Payment intents / charges by ID
- Customers by email or ID
- Checkout sessions by ID
- Refunds, invoices, subscriptions

The same key is stored in Render env var `STRIPE_SECRET_KEY` for the field assistant app.
