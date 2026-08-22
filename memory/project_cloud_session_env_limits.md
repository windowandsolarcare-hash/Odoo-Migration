---
name: project_cloud_session_env_limits
description: "Cloud Claude Code session environment limits (found 2026-08-22): gh CLI NOT installed (use GitHub MCP Contents API); outbound network is GitHub-ONLY by default (app/Odoo/wscare.pro all 403) — must open the env network allowlist to verify live or run Operator-cloud."
metadata: 
  node_type: memory
  type: project
  originSessionId: 8aa212a8-bcad-463e-b17d-ebf080940e01
  modified: 2026-08-22T21:40:08.069Z
---

**Discovered 2026-08-22 during the cloud-session rollout (cloud-Portal tested all three domains).** These are the real limits of Anthropic-hosted cloud Claude Code sessions for THIS project:

1. **`gh` CLI is NOT installed in the cloud shell.** Cloud sessions push via the **GitHub MCP Contents API** (the same Contents PUT that `gh api` performs → satisfies the `main`-branch ruleset that rejects `git push` but allows the Contents API). The standing "gh api to main, never git push" rule is unchanged — only the tool differs (MCP instead of gh CLI). Both cloud-Lead and cloud-Portal onboarded fine this way.

2. **Outbound network is GitHub-ONLY by default.** `wscare.pro`, `wsc-field-assistant.onrender.com`, and `window-solar-care.odoo.com` ALL return **403 at the security proxy**. Consequences:
   - A cloud CODE session (Portal, Specialists) can read/reason/edit/push code, but **cannot smoke-test the live app or query Odoo** — our "verify by content, not status code" discipline ([[feedback_odoo_verify_content_not_status]]) must be done by a LOCAL session or DJ for anything a cloud session ships.
   - **Operator-cloud is fully blocked** — Operator works ONLY by calling the app's HTTP endpoints ([[project_new_job_via_app_endpoints]]), which 403 here.
   - **Fix:** open the cloud environment's network allowlist — claude.ai/code → environment settings → Network → **Custom** (add `wscare.pro`, `wsc-field-assistant.onrender.com`, `window-solar-care.odoo.com`) or **Full**. Env changes apply to NEW sessions (a running session keeps its startup network), so restart/relaunch the session after changing it. This is required before Operator-cloud and before any cloud session can self-verify.

**Also relevant (from the mechanics research):** cloud sessions do NOT auto-load `~/.claude` memory (read `./memory/` from the repo — see the CLOUD SESSIONS section in CLAUDE.md); user-scoped MCP servers aren't available (repo `.mcp.json` is); no dedicated secrets store (env vars are visible — don't put API keys there, see [[project_odoo_api_key_rotated_2026-08-22]]); ~4 vCPU/16GB/30GB; sessions persist + resume via claude.ai/code or `claude --teleport`. Related: [[project_claude_remote_control]].
