---
name: project_odoo_api_key_rotated_2026-08-22
description: The Odoo API key was ROTATED 2026-08-22. The old key 7e92006fd5c71e4fab97261d834f2e6004b61dc6 is DEAD (Access Denied). Never use it. New key lives in Render env ODOO_API_KEY + a local key file — never in any committed file.
metadata: 
  node_type: memory
  type: project
  originSessionId: 8aa212a8-bcad-463e-b17d-ebf080940e01
  modified: 2026-08-22T20:14:34.314Z
---

**Odoo API key rotated 2026-08-22** after Portal caught the live key sitting in plaintext in committed `CLAUDE.md` (lines 47-49) + `CLAUDE_CONTEXT.md` + `MASTER_PROJECT_CONTEXT.md`.

- **OLD key `7e92006fd5c71e4fab97261d834f2e6004b61dc6` is REVOKED / DEAD** — authenticating with it returns **Access Denied**. Do NOT use it. It still appears (as a dead string) in ~50 one-off scripts, the 4 dormant Zapier phase scripts, and 3 memory files (`feedback_render_put_env_vars`, `feedback_send_email_with_attachment`, `project_render_conversation_log`) — those are harmless now (dead) but should be scrubbed if convenient.
- **NEW key** lives in **Render env var `ODOO_API_KEY`** (service `wsc-field-assistant` srv-d78le0fkijhs738dsli0, key named `render-app-2026-08` in Odoo) and in a LOCAL key file on DJ's machine. **Never written into any committed/GitHub file** — that's the whole lesson ([[project_memory_mirror_secret_scanning]], [[feedback_api_keys_via_file]]).
- **What changed in code:** `main.py:77` and `routers/printing/watcher.py:27` were de-hardcoded to `os.environ.get('ODOO_API_KEY','')` (shared/odoo.py already read env). Three Workiz-era keys were deleted in Odoo (Workiz retired 2026-08-03); only `render-app-2026-08` remains.
- **How the app auths now:** everything reads `ODOO_API_KEY` from env — one source. Verified 2026-08-22: new key auths (1,596 partners), app `/owner/api/intake/search` returns customers, old key rejected.
- **OPEN follow-up:** cloud sessions (running against the GitHub repo, no local file) will need a way to get the Odoo key for raw RPC — env/secret injection, TBD. Local sessions read the local key file. Governance still says prefer app endpoints over raw RPC ([[feedback_assistant_use_app_workflow_not_raw_api]]).

Checklist doc: `Odoo-Migration/3_Documentation/ROTATE_ODOO_KEY.md`.
