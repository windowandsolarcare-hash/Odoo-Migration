---
name: Use Python for GitHub deploy when the bash+powershell pipeline chokes
description: CLAUDE.md says use deploy_to_github.sh (bash + powershell base64). It works MOST of the time but occasionally returns "Problems parsing JSON" HTTP 400. When that happens, fall back to a small Python script that does base64+JSON natively. No retry loop — just switch tools.
type: feedback
originSessionId: 96c7eadf-7840-4091-9290-6d3aed1806c8
---
CLAUDE.md prescribes a bash+powershell+base64 pipeline for pushing files to GitHub via the GH API. It works most of the time. Occasionally it returns **"Problems parsing JSON" HTTP 400** — particularly on larger files (300+ lines) and files with lots of nested quotes/special characters. PowerShell's `[System.Convert]::ToBase64String` reliably introduces line breaks that break the JSON payload despite the heredoc approach.

**Why:** 2026-04-29 — pushing `quote.html` (a single 700-line HTML file with embedded JS) failed via the bash script. The Python fallback succeeded on the first try.

**How to apply:**

When `deploy_to_github.sh` (or the inline bash+powershell pattern in CLAUDE.md) returns `"Problems parsing JSON" HTTP 400`, do not retry the same command. Instead, use this Python pattern:

```python
import base64, json, subprocess, tempfile, os

REPO = 'windowandsolarcare-hash/saunders-render-app'

def deploy(path_in_repo, local_path, msg):
    with open(local_path, 'rb') as f: data = f.read()
    content_b64 = base64.b64encode(data).decode('ascii')
    try:
        sha = subprocess.check_output(
            ['gh','api',f'repos/{REPO}/contents/{path_in_repo}','--jq','.sha'],
            stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:
        sha = ''  # new file
    payload = {"message": msg, "content": content_b64, "branch": "main"}
    if sha: payload["sha"] = sha
    fd, tmp = tempfile.mkstemp(suffix='.json', text=True)
    with os.fdopen(fd, 'w') as f: json.dump(payload, f)
    r = subprocess.run(
        ['gh','api',f'repos/{REPO}/contents/{path_in_repo}','--method','PUT','--input',tmp],
        capture_output=True, text=True)
    os.unlink(tmp)
    if r.returncode == 0:
        print('OK', json.loads(r.stdout)['commit']['sha'][:8])
    else:
        print('FAIL', r.stderr[:300])
```

**Why this works:** Python's `base64.b64encode()` returns a single line with no MIME-style breaks. `json.dump()` produces valid escaping. `tempfile.mkstemp` gives a real Windows-friendly path (avoids the `/tmp/...` issue when called from PowerShell-spawned bash).

**Important:**
- This is a fallback, not the default. Stick with the bash script for normal use — it's documented in CLAUDE.md and easier to understand.
- If a file fails twice via bash, switch to Python without trying a third time. Token-wasting retry loops are explicitly called out in `feedback_proactive_inefficiency_capture.md`.
- For multi-file deploys, factor a `deploy()` helper and call it once per file. Don't loop bash and Python separately.

**Related memory:**
- `feedback_github_deployment_bash.md` — the canonical bash approach
- `feedback_proactive_inefficiency_capture.md` — don't retry-loop, switch tools
