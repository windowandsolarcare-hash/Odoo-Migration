---
name: Render Claude session history persists to Odoo (survives redeploys)
description: 2026-04-26 — Render Claude conversation history moved from in-memory _sessions dict to Odoo ir.config_parameter (key=render.session.{session_id}). Survives redeploys, restarts, free-tier sleep.
type: project
originSessionId: 96c7eadf-7840-4091-9290-6d3aed1806c8
---
**Bug discovered 2026-04-26:** Render Claude was losing all per-customer context whenever code was pushed. Root cause: `get_history` / `save_history` / `clear_history` used an in-memory dict `_sessions` that gets wiped on every Render redeploy and free-tier sleep. We pushed multiple fixes today, each one wiped Render Claude's working memory of the active customer (e.g., Kristin Acker).

**Fix (commit 455754d on saunders-render-app):** session history now persists to Odoo `ir.config_parameter` under key `render.session.{session_id}`. The three helpers (`get_history`, `save_history`, `clear_history`) now read/write Odoo. Trim is still last 40 messages with the existing tool_result-orphan protection. Per-turn cost is 1 Odoo read + 1 write — fast enough.

**System prompt also updated** (commit 455754d) with two new sections:
- **CONTEXT PRESERVATION** — pronouns default to most recently discussed customer; never re-search the active customer; UUID/partner_id/so_id stick once known.
- **NO TRIAL-AND-ERROR** — use existing tools as documented; don't retry blindly on errors; if no tool exists, plan with DJ first then execute once.

**Why:** DJ pays per Anthropic API call. Re-search burns tokens. Wrong API formats burn tokens. Lost context burns tokens twice (once for the lost work, once to re-do it).

**How to apply:**
- When asked about Render Claude memory, this is now backed by Odoo — wipes only happen if `clear_history` is explicitly called.
- If DJ wants to manually clear a session, delete the `render.session.{session_id}` ir.config_parameter row.
- If session storage grows unbounded over months, add periodic cleanup of rows with `write_date` older than X days. Not built yet — wait for evidence of pressure.
- If you want to TEST the persistence, push any change → Render redeploys → query Odoo for `render.session.*` keys to confirm history rows are still there.
