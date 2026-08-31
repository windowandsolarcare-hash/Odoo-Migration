---
name: project_cloud_session_env_limits
description: "★ RE-VERIFIED LIVE 2026-08-31: on this project's Default cloud env the allowlist IS OPEN — app (/healthz 200), Odoo (200) and api.render.com (401, i.e. reachable) all answer, so a cloud session CAN verify by content and run Operator-style ops. Do NOT repeat the 'cloud is GitHub-only' claim without testing it. GitHub-only is the DEFAULT for a brand-new env, not a property of cloud sessions. Also: gh CLI NOT installed (use GitHub MCP Contents API for small files, git push + PR for big ones)."
metadata: 
  node_type: memory
  type: project
  originSessionId: 8aa212a8-bcad-463e-b17d-ebf080940e01
  modified: 2026-08-22T22:46:25.984Z
---

**Discovered 2026-08-22 during the cloud-session rollout (cloud-Portal tested all three domains).** These are the real limits of Anthropic-hosted cloud Claude Code sessions for THIS project:

1. **`gh` CLI is NOT installed in the cloud shell.** Cloud sessions push via the **GitHub MCP Contents API** (the same Contents PUT that `gh api` performs → satisfies the `main`-branch ruleset that rejects `git push` but allows the Contents API). The standing "gh api to main, never git push" rule is unchanged — only the tool differs (MCP instead of gh CLI). Both cloud-Lead and cloud-Portal onboarded fine this way.
   - **★ BIG-FILE CONSTRAINT (found 2026-08-22):** the GitHub **MCP push tool takes the whole file content INLINE** (in the session's context) — fine for small files (portal.py ~40KB) but NOT viable for the big ones (`field.py` ~189KB, `dashboard.py` ~748KB): the file blows the context and is error-prone. **RESOLUTION:** an env var **`GITHUB_TOKEN` IS present** in the cloud shell, so for big files a cloud session must push via a **DISK-based Contents-API script** (read file from disk → base64 → `curl` PUT to the Contents API; the file never enters context), NOT the inline MCP tool. That is how a cloud session can safely edit `dashboard.py`/`field.py`. cloud-Portal wrote a `push_gh.sh` doing exactly this.

2. **Outbound network is GitHub-only ONLY until the env allowlist is opened — on our Default env it IS open (re-verified 2026-08-31, see STATUS below).** `wscare.pro`, `wsc-field-assistant.onrender.com`, and `window-solar-care.odoo.com` ALL return **403 at the security proxy**. Consequences:
   - A cloud CODE session (Portal, Specialists) can read/reason/edit/push code, but **cannot smoke-test the live app or query Odoo** — our "verify by content, not status code" discipline ([[feedback_odoo_verify_content_not_status]]) must be done by a LOCAL session or DJ for anything a cloud session ships.
   - **Operator-cloud is fully blocked** — Operator works ONLY by calling the app's HTTP endpoints ([[project_new_job_via_app_endpoints]]), which 403 here.
   - **STATUS 2026-08-22: the allowlist WAS OPENED for this project's Default cloud environment** — `wscare.pro`, `wsc-field-assistant.onrender.com`, and `window-solar-care.odoo.com` are now reachable (cloud-Specialists + cloud-Operator both confirmed `/healthz` → 200 by content). So current cloud sessions on the Default env CAN self-verify and hit the app. (A brand-new/other environment would still start GitHub-only until its allowlist is opened.)
   - **Fix (how it was done):** open the cloud environment's network allowlist — claude.ai/code → environment settings → Network → **Custom** (add `wscare.pro`, `wsc-field-assistant.onrender.com`, `window-solar-care.odoo.com`) or **Full**. Env changes apply to NEW sessions (a running session keeps its startup network), so restart/relaunch the session after changing it. This is required before Operator-cloud and before any cloud session can self-verify.

**Also relevant (from the mechanics research):** cloud sessions do NOT auto-load `~/.claude` memory (read `./memory/` from the repo — see the CLOUD SESSIONS section in CLAUDE.md); user-scoped MCP servers aren't available (repo `.mcp.json` is); no dedicated secrets store (env vars are visible — don't put API keys there, see [[project_odoo_api_key_rotated_2026-08-22]]); ~4 vCPU/16GB/30GB; sessions persist + resume via claude.ai/code or `claude --teleport`. Related: [[project_claude_remote_control]].
