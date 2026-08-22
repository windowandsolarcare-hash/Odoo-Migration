---
name: project_render_deploy_failed_check
description: "If pushed changes don't appear live on the Render field app, check list_deploys for update_failed — a startup crash keeps the old build serving."
metadata: 
  node_type: memory
  type: project
  originSessionId: 52666f46-c84b-4f55-ad04-3ed2f2d38410
---

If changes pushed to `windowandsolarcare-hash/saunders-render-app` don't show up live (old icon, old behavior) even though the GitHub commit succeeded: the deploy is probably failing. Render autoDeploy is **on** (`autoDeploy: yes`, trigger commit) for service `srv-d78le0fkijhs738dsli0`, but when a deploy fails Render keeps the **last good build running** and silently serves stale code.

**How to check (render MCP, workspace tea-d78l9fqdbo4c7388n9og must be selected first):**
1. `mcp__render__list_deploys` serviceId `srv-d78le0fkijhs738dsli0` — look for `status: update_failed`.
2. `mcp__render__list_logs` resource `["srv-d78le0fkijhs738dsli0"]`, narrow startTime/endTime to the failed deploy window, direction backward — the traceback shows the real error.
3. Confirm what's actually live by curling the asset and comparing bytes/pixels, e.g. `curl https://wsc-field-assistant.onrender.com/static/icon-192.png`.

`update_failed` (vs `build_failed`) = build/pip succeeded but the app crashed on startup (uvicorn `config.load_app` import error) or health check failed. Almost always a Python error in `main.py` or an imported router.

**2026-06-06 incident:** `routers/auth.py` `_SW_JS` was committed with newlines *inside* the string-literal quotes → `SyntaxError: unterminated string literal` → `main.py`'s `from routers import auth` crashed → every deploy update_failed for ~40 min. Fixed by joining the adjacent string literals onto single lines. After the fix, the next deploy went live in ~2 min and all the queued icon/manifest commits shipped together.

**Why:** A stale-serving Render app looks exactly like "my push didn't work." It's not the push — it's a failed deploy. Always verify deploy status, not just the GitHub commit.

**How to apply:** After pushing to this repo, if the user reports the change isn't visible, check list_deploys before re-pushing or second-guessing the file. Run `node --check`/`py_compile` before pushing code files (see [[feedback_field_html_js_syntax_check]]). Related: [[project_pwa_manifest_on_every_page]].
