---
name: project_windows_python_gh_edit_stdin
description: Editing a gh-fetched file — pipe through python3 stdin->stdout; never open() a /c/ MSYS path (Windows python3 throws FileNotFoundError and the edit silently no-ops).
metadata:
  node_type: memory
  type: project
  originSessionId: f9d25f0d-f892-4864-829e-2fda94efd70c
  modified: 2026-09-28T21:48:13.925Z
---

When editing a GitHub file from Claude Code (Git Bash) via `gh api ... | base64 -d`, do the transform with `python3 -c` reading `sys.stdin` and writing `sys.stdout`, then bash-redirect to the file. Do NOT have python `open("/c/Users/...")` — the **Windows** `python3` interpreter cannot resolve MSYS-style `/c/...` paths and throws `FileNotFoundError`, even though bash `wc`/`>` on the same path work fine. So the script keeps running and pushes the **UNMODIFIED** file.

**Symptom (burned 2 pushes at Dispatcher boot 2026-09-28):** a roster row edit reported `FileNotFoundError` on `open('/c/Users/dj/roster_edit.md')` while `wc -c` on the same path returned 8594 bytes — the surrounding `gh api PUT` still fired and pushed the original content (ref never changed). Fixed by switching to `... | python3 -c "s=sys.stdin.read(); ...; sys.stdout.write(s)" > file`.

**Why:** the canonical CLAUDE.md "EDITING A DEPLOYED FILE" pattern already uses stdin->stdout for exactly this reason; deviating to file-path `open()` breaks on Windows.

**How to apply:** (1) always stdin->stdout for the transform; if you MUST pass a path to Windows python, use `C:/Users/...` not `/c/Users/...`. (2) GUARD the push — grep that the expected change is present AND size>1000 BEFORE the PUT — so a no-op/failed edit can never push stale or empty content. Ties [[feedback_bash_tmp_not_persistent]] [[feedback_gh_push_empty_file_guard]].
