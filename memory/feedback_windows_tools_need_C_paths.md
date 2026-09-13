---
name: feedback-windows-tools-need-c-paths
description: "In Git-Bash, native Windows tools (PowerShell, Windows python) can't read MSYS /c/ paths — pass C:/ paths to them, /c/ only to bash builtins."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-13T12:54:14.192Z
---

When deploying from Claude Code on DJ's Surface, the Bash tool is Git-Bash (MSYS) but it shells out to **native Windows** tools. Those tools do NOT understand MSYS `/c/Users/...` paths — they need `C:/Users/...`.

- `powershell -Command "... Get-Content '/c/Users/dj/x' ..."` → reads NOTHING, base64 comes back **empty (length 0)** → a silent empty/failed push (caught only by the b64-length guard). Pass `C:/Users/dj/x`.
- Windows `python` opening `open(r"/c/Users/dj/x")` → **FileNotFoundError**. Pass `C:/Users/dj/x`.
- Bash builtins (`cat`, `printf`, `gh api`, `base64 -d`, redirection `>`) DO take `/c/Users/...` — only the native-tool calls need `C:/`.

**Why:** burned ~4 tool calls in one session (2026-09-13) on empty-b64 push aborts + a python re-stamp FileNotFoundError, all from passing `/c/` paths into PowerShell/python. The powershell base64 push helper and any inline `python - <<PY` that reads a file are the usual offenders.

**How to apply:** in the push helper, write intermediate files with bash to `/c/Users/dj/<f>`, but hand PowerShell/`python` the **`C:/Users/dj/<f>`** form. A quick tell: if `${#b64}` is 0 or python raises FileNotFoundError on a path you know exists, you passed a `/c/` path to a Windows tool. Pairs with [[feedback_bash_tmp_not_persistent]] and [[feedback_github_deployment_bash]].
