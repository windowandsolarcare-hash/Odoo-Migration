---
name: feedback-bash-tmp-not-persistent
description: /tmp does NOT persist between Bash tool calls — use /c/Users/dj/ as intermediate storage and pipe edits in one call
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 7b173fd1-b5b7-43e3-ba55-7c216343fb45
---

`/tmp` is reset between separate Bash tool invocations. Saving a file there in call 1 and reading it in call 2 always fails with `FileNotFoundError`.

**Why:** Each Bash tool call spawns a fresh shell. `/tmp` is not shared across calls.

**How to apply:** When editing a file fetched from GitHub:
1. Do download → Python edit → save to `/c/Users/dj/edited_file.py` ALL in one piped command
2. Push from `/c/Users/dj/` in the next call

**Working one-liner pattern:**
```bash
gh api repos/REPO/contents/PATH --jq '.content' | base64 -d | python3 -c "
import sys
content = sys.stdin.read()
content = content.replace('old', 'new')
sys.stdout.write(content)
" > /c/Users/dj/edited_file.py && echo "saved"
```

Then push using standard PowerShell base64 + gh api pattern from `/c/Users/dj/edited_file.py`.

JSON payload files (`cat > /c/Users/dj/gh_payload.json`) used in the same chained call (`&&`) are fine.
