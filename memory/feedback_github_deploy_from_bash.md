---
name: GitHub deployment from Claude Code bash environment
description: Claude Code runs in bash on Windows — use powershell -Command wrapper to deploy to GitHub, not raw bash or Python
type: feedback
---

When deploying files to GitHub from Claude Code, the **preferred method** is direct bash using gh CLI and base64. PowerShell wrapper also works but sometimes fails with CLR errors.

**Why:** gh CLI is accessible from bash directly. Direct bash is faster and more reliable than PowerShell wrapper.

**Preferred (bash directly):**
```bash
SHA=$(gh api "repos/windowandsolarcare-hash/Odoo-Migration/contents/PATH/file.py" --jq '.sha') && CONTENT=$(base64 -w 0 "/c/Users/dj/Documents/Business/A Window and Solar Care/Migration to Odoo/PATH/file.py") && echo "{\"message\":\"DATE | file | desc\",\"content\":\"$CONTENT\",\"sha\":\"$SHA\",\"branch\":\"main\"}" | gh api "repos/windowandsolarcare-hash/Odoo-Migration/contents/PATH/file.py" --method PUT --input - --jq '.commit.sha' && echo "PUSHED"
```

**Fallback (PowerShell wrapper):**
```bash
powershell -Command "\$repo='windowandsolarcare-hash/Odoo-Migration'; \$filePath='PATH/file.py'; \$sha=(gh api \"repos/\$repo/contents/\$filePath\" --jq '.sha').Trim(); ..."
```

For Odoo server action 955 specifically: use Python xmlrpc.client (write a deploy_955.py script, run with `python deploy_955.py`, delete after).
