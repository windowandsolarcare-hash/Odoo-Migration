---
name: shift_review.html authoritative source is AppData temp file, not local repo
description: The local repo copy of shift_review.html is an old simplified version. Always edit/deploy from the temp file path. Deploying the local repo copy wipes the live version.
type: feedback
originSessionId: 7ad343ab-c028-433d-86f6-989416b269ac
---
The local repo copy at `C:\Users\dj\Documents\Business\Saunders Render App\static\owner\shift_review.html` is an OLD simplified version (~290 lines). The full live version (~770 lines) lives at:

```
C:\Users\dj\AppData\Local\Temp\shift_review_current.html
```

**Why:** The local repo was never updated when the full Phase 2 version was deployed. One session accidentally deployed the local repo copy and wiped 480 lines of the live page.

**How to apply:**
- ALWAYS fetch the current version from GitHub before editing shift_review.html:
  ```bash
  gh api repos/windowandsolarcare-hash/saunders-render-app/contents/static/owner/shift_review.html \
    --jq '.content' | base64 -d > /tmp/shift_review_current.html
  ```
- Edit the fetched copy, then deploy using the Python base64 pattern (not bash+PowerShell)
- Never touch the local repo copy at the Saunders Render App path

**Deploy method for shift_review.html:** Python only (no bash+PowerShell base64 — $TEMP doesn't resolve in PowerShell subshell, causes silent empty content). Use safe_deploy.py or the Python inline pattern.
