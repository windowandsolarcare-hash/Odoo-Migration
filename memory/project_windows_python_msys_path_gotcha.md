---
name: project_windows_python_msys_path_gotcha
description: "This box's python3 is Windows Python — it CANNOT open Git-Bash /c/... MSYS paths; keep /c/ file I/O in bash, feed python via stdin/stdout."
metadata: 
  node_type: memory
  type: project
  originSessionId: 561c5d7a-5bd6-416a-8a5e-02c57aaed43d
  modified: 2026-09-14T14:39:02.714Z
---

The `python3` invoked inside a Bash tool call on DJ's Surface is **Windows Python**, not MSYS/Cygwin python. It does NOT understand Git-Bash MSYS paths like `/c/Users/dj/...` — it treats `/c/Users/dj/x.md` as a literal Windows path off the current drive root (`\c\Users\dj\x.md`), which doesn't exist. So **`open('/c/Users/dj/x.md', ...)` inside `python3 -c` throws `FileNotFoundError` — for reads AND for writes** (a `'wb'` open fails because the "directory" `\c\Users\dj` doesn't exist).

**Why it's sneaky:** bash itself resolves `/c/...` correctly, so `some_cmd > /c/Users/dj/x.md` and `base64 -d < /c/Users/dj/x.md` WORK (bash owns the redirect/pipe). The failure only appears the moment PYTHON opens the path directly. So a two-step pattern — bash writes `/c/Users/dj/roster.md` in call 1, python reads it in call 2 — looks like the "/tmp doesn't persist" problem but is really the MSYS-path problem, and it fails even inside a single chained call.

**Real incident (2026-09-14, Lead hourly tick):** a roster CAS re-stamp did `python3 -c "open('/c/Users/dj/roster.md')..."` → FileNotFoundError → `base64 -w0 /c/Users/dj/roster.md` then also failed → empty b64 → came within one step of PUTing an empty SESSION_ROSTER.md. Saved only by the empty-file guard (`[ ${#b64} -lt 1000 ] && exit 1`, see [[feedback_gh_push_empty_file_guard]]). Live file verified intact afterward.

**How to apply — for fetch→edit→push of a GitHub file, do the /c/ or path I/O in BASH and let python work purely on stdin→stdout:**
```
newb64=$(gh api repos/$repo/contents/$path --jq '.content' | base64 -d | python3 -c "
import sys
c=sys.stdin.read()
assert c.count(OLD)==1
c=c.replace(OLD,NEW); assert len(c)>MIN
sys.stdout.write(c)
" | base64 -w0)
[ ${#newb64} -lt 1000 ] && { echo ABORT; exit 1; }   # empty-file guard (also catches python assert failure via set -o pipefail)
```
Use `set -o pipefail` so a python assert failure empties `newb64` and trips the guard instead of pushing garbage. Alternatives that also work: use a native Windows path for python (`C:/Users/dj/x.md` or `C:\\Users\\dj\\x.md`), or use the CLAUDE.md `powershell -Command` base64 pattern. But the stdin/stdout pipe is cleanest and matches the canonical deploy flow. Related: [[feedback_bash_tmp_not_persistent]], [[feedback_github_deployment_bash.md]], [[feedback_push_compare_and_swap]].
