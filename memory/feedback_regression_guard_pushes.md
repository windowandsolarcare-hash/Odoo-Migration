---
name: Regression guard for GitHub pushes — never push from a stale local copy
description: 2026-04-30 incident — another Claude Code chat had a 3565-line copy of dashboard.py and pushed it over the live 5842-line version, wiping 2277 lines (Manage Shifts CRUD, GPS endpoints, Stale SOs, whoami, todos/reactivate). Two guards now exist: (1) safe_deploy.py at C:\Users\dj\safe_deploy.py refuses local-smaller-than-deployed pushes; (2) Render Claude's github_push_file tool refuses voice pushes that drop >100 lines or >25% bytes unless acknowledge_regression:true. Use safe_deploy.py for ALL pushes to dashboard.py and other large files.
type: feedback
originSessionId: 96c7eadf-7840-4091-9290-6d3aed1806c8
---
**Why:** A different Claude Code chat regressed dashboard.py from 5842 lines to 3565 lines in one push. The other chat had been editing what it thought was the current file but was actually a stale snapshot. The push silently wiped Manage Shifts (Danny couldn't see his shifts), GPS endpoints, Stale SOs page, and more. DJ noticed only when "Error: Load Failed" came back. Restoration took ~15 minutes plus an emergency redeploy.

**⚠ RECURRENCE 2026-06-08 — same mistake, by me, by bypassing the guard.** My LOCAL field.html (2866 lines) and dashboard.py (9256 lines) were stale snapshots. I edited them for two small features (Past 14 Days view, photo tweak) and pushed via **raw `gh api ... --method PUT`** — NOT safe_deploy.py — so the guard never ran. This overwrote the live Jun-7 versions (field.html 4243 / dashboard.py 12513), dropping ~1377 + ~3257 lines. Symptom DJ saw: old photo-upload button reappeared, "a lot of changes gone, working on old code." It ALSO broke deploys: an importer expects `tool_check_unpaid_jobs` (dashboard.py line ~712); the stale dashboard.py lacked it → `ImportError` on startup → Render `update_failed`, silently kept serving the last good build. **Recovery:** fetched the last commit before my pushes (field 725120a6 / dashboard 5fc0bbd6), restored verbatim, pushed via safe_deploy.py (guard passed since restoring=bigger), verified deploy `live` + HTTP 200. Nothing permanently lost — git history had every line. **THE LESSON IS NOW DOUBLE:** (a) my local repo copies are chronically stale — assume stale, fetch from GitHub before editing ANY Render app file; (b) safe_deploy.py only protects you IF YOU USE IT — never `gh api PUT` a large file directly, because that path has no guard. See also [[feedback_bash_tmp_not_persistent]], [[project_render_deploy_failed_check]].

**How to apply:**

0. **NEVER push large Render-app files with raw `gh api --method PUT`.** That bypasses the guard entirely (the 2026-06-08 recurrence). Always go through `safe_deploy.py` (CLI) — it fetches current, compares, refuses on regression. Raw gh api PUT is only acceptable for brand-new files or tiny config.

1. **Before editing any large file (>1000 lines) in `Saunders Render App/`** — pull the current GitHub version FIRST and compare to local. Because local is chronically stale, the safest pattern is to fetch GitHub→local, THEN edit, THEN safe_deploy:
   ```bash
   gh api repos/windowandsolarcare-hash/saunders-render-app/contents/<path> --jq '.content' | base64 -d > /tmp/current
   wc -l /tmp/current "<local path>"
   ```
   If GitHub version is significantly larger than local, your local is stale — refresh from GitHub before editing.

2. **Push via `safe_deploy.py`** instead of one-off scripts. Located at `C:\Users\dj\safe_deploy.py`. It does the freshness check automatically and refuses to push if local is >25% smaller or >100 lines shorter than deployed.

   ```bash
   python C:/Users/dj/safe_deploy.py \
     --repo  windowandsolarcare-hash/saunders-render-app \
     --path  routers/owner/dashboard.py \
     --local "C:\\Users\\dj\\Documents\\Business\\Saunders Render App\\routers\\owner\\dashboard.py" \
     --msg   "2026-04-30 | dashboard.py | what changed"
   ```
   Add `--force` only after personally diffing and confirming the deletions are intentional.

3. **Render Claude's `github_push_file` tool** has the same guard server-side (commit `41351838`). Voice-driven pushes refuse if they drop >100 lines or >25% bytes unless `acknowledge_regression: true` is in the call. So even if a voice command tries to push a stale version, it'll be blocked with a clear message.

**Files / commits:**
- `C:\Users\dj\safe_deploy.py` — local deploy helper (added 2026-04-30)
- `Saunders Render App/routers/owner/dashboard.py` — github_push_file with guard (commit 41351838)
- `CLAUDE.md` updated 2026-04-30 with mandatory pre-push checklist

**Override semantics:** When the guard fires, the calling code should:
- DIFF locally and verify the deletions are intentional
- Then re-call with `--force` (CLI) or `acknowledge_regression: true` (Render Claude tool)
- Never bypass blindly — that's how we lost 2277 lines

**Related memory:**
- `feedback_local_vs_deployed_drift.md` — the original observation (2026-04-27) that local Saunders Render App copies can lag deployed
- `feedback_github_deployment_bash.md` — the bash+base64 deploy approach
- `feedback_github_deploy_python_fallback.md` — Python fallback when bash chokes on large files
