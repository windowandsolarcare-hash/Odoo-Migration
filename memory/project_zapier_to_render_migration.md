---
name: project_zapier_to_render_migration
description: "Near-term plan to migrate Phases 3/4/5/6 from Zapier to Render — Zapier is just webhook catch + GitHub fetch, so it's a simple redirect"
metadata: 
  node_type: memory
  type: project
  originSessionId: f95b5c02-0629-4ade-8f81-8981d2f629ca
---

## Zapier → Render Migration

**Status:** NEAR-TERM — prerequisite for referral blast (2026-05-28)

**Why Zapier is easy to replace:**
Zapier's role is exactly 2 steps per phase:
1. Catch the webhook (or poll on a timer)
2. Fetch code from GitHub and run it

Render already does both natively. This is not a big port — it's a redirect.

**Phases to migrate:**
- Phase 3: Workiz webhook → point URL at Render instead of Zapier. Render fetches + runs same GitHub code.
- Phase 4: Zapier 5-min poll → replace with Render cron job every 5 min
- Phase 5: Triggered by Phase 6 webhook → same redirect to Render
- Phase 6: Odoo webhook → Render (same pattern as Phase 3)

**Why:** Eliminate Zapier cost entirely. Also unblocks referral blast (webhook cascade is free on Render, expensive on Zapier).

**How to apply:** When DJ is ready, plan a dedicated session. Estimated effort: half a day. Steps: add webhook receiver endpoints in Render for each phase, update Workiz + Odoo webhook URLs, set up Render cron for Phase 4 polling, test each phase, cancel Zapier.
