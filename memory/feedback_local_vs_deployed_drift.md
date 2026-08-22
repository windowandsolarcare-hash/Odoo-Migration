---
name: Local Saunders Render App copy may lag deployed code — diff before pushing
description: 2026-04-27 — pushed local dashboard.py and unintentionally regressed two prior Workiz quirk fixes (commits 7cbd848 + 405a31d) because the local file was older than what was running on Render. Diff before deploy.
type: feedback
originSessionId: 96c7eadf-7840-4091-9290-6d3aed1806c8
---
When editing `C:\Users\dj\Documents\Business\Saunders Render App\routers\owner\dashboard.py` (or any file in that repo), the local copy may be stale relative to what's deployed. This bit me on 2026-04-27: I deployed follow-up endpoints, and the deploy overwrote two earlier `workiz_post` fixes (UUID auto-inject for update/delete, and Status="Pending" auto-inject when SubStatus present) because my local file pre-dated those commits.

**Why:** the dashboard.py at `C:\Users\dj\AppData\Local\Temp\deployed_dashboard.py` is a snapshot pulled FROM Render at some point. The repo working copy is at `C:\Users\dj\Documents\Business\Saunders Render App\routers\owner\dashboard.py`. They drift independently. The temp file got updated when those Workiz fixes happened (or when DJ pulled fresh from Render); the repo working copy didn't.

**How to apply:**

Before deploying any change to that repo, run a fast sanity check:

```bash
gh api repos/windowandsolarcare-hash/saunders-render-app/contents/routers/owner/dashboard.py --jq '.content' | base64 -d > /tmp/remote_dashboard.py
diff /tmp/remote_dashboard.py "C:/Users/dj/Documents/Business/Saunders Render App/routers/owner/dashboard.py" | head -200
```

If the diff shows changes you don't recognize as your own work — STOP. Either:
1. Pull the remote version into the local working copy first, then layer your edits on top
2. Or pinpoint exactly which lines have drifted and reapply the fix as part of your push

**Specific fixes that exist in the deployed code and could be lost on a sloppy push** (verify these before deploying any dashboard.py change):
- `workiz_post()` should auto-inject `UUID`/`ID` for job/update and job/delete endpoints (regex match on URL path)
- `workiz_post()` should auto-inject `Status="Pending"` when `SubStatus` is in body
- `_sessions` history is persisted to Odoo `ir.config_parameter` under `render.session.{id}` (not just in-memory)

If you're unsure whether the local file has the fix, grep for the regex `^def workiz_post` and look for the lines `re.match(r'^job/(update|delete)/...` and `if 'SubStatus' in data and 'Status' not in data`. Both should be present.

**Token cost of this rule:** ~5 seconds to run the diff. Cost of getting it wrong: 30+ minutes to re-diagnose a bug we already fixed.
