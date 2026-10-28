---
name: feedback_windows_python_msys_path_and_crlf_files
description: On this Surface, python3 invoked from git-bash is Windows-native — it CANNOT open /c/Users/... MSYS paths (silent FileNotFound); use C:/Users/... And some repo files (AGENT_MAIL.md) are pure CRLF — a naive utf-8 read+rewrite strips every \r and corrupts a surgical edit
metadata:
  node_type: memory
  type: feedback
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-28T01:53:21.326Z
---

Two traps that silently wasted a push cycle (2026-10-27, Specialists, AGENT_MAIL insert):

**1) Windows-native python3 can't resolve git-bash MSYS paths.** In a Bash-tool pipeline, `wc`/`base64`/`ls`/`gh` accept `/c/Users/dj/x` (MSYS mount), but `python3` here is the **Windows** interpreter — `open('/c/Users/dj/x')` throws `FileNotFoundError` even though the file exists. When a heredoc `python3 - <<PY` crashes on that open, the shell **keeps going** and the next `base64 -w0 <file>` reads the UNMODIFIED file, so a `gh api ... PUT` pushes the original bytes back (a no-op commit that LOOKS like success — it prints a commit sha). **Fix:** always pass python a Windows path — `r'C:/Users/dj/x'` (forward slashes are fine). git-bash tools accept `C:/Users/...` too, so use `C:/Users/...` EVERYWHERE for cross-tool files.

**Why it's insidious:** the push "succeeds" (commit sha returned) but your edit never landed — the blob sha is unchanged. Verify the blob/size changed, not just that a commit came back.

**2) Some living repo files are pure CRLF (`\r\n`), notably `3_Documentation/AGENT_MAIL.md` (24k+ CRLF, 0 LF).** A naive `open(p,encoding='utf-8').read()` on Windows python uses universal-newline mode → strips every `\r` on read; rewriting then drops ~1 byte/line (AGENT_MAIL shrank 564063→540859, −23KB) = a massive non-surgical diff touching every line, and a size guard rightly aborts it. **Fix for a surgical append/insert into a CRLF file:** read **binary** (`open(p,'rb')`), detect EOL (`raw.count(b'\r\n')` vs LF-only), build your inserted block joined with the file's EOL, `raw.find(b'### ')` the anchor, splice bytes, write **binary**, and assert head+tail bytes are preserved and the file only GREW. (The CLAUDE.md rule "`.replace('\r\n','\n')` before string-replace" is for files you then push as LF — do NOT LF-normalize a file that must stay CRLF; preserve its EOL instead.)

**Guard pattern:** after editing, assert new byte-size ≥ original (for an append) and `grep -q` your inserted marker in the file BEFORE computing base64; abort the PUT if either fails. This catches both traps. See [[feedback_bash_tmp_not_persistent]], [[feedback_gh_push_empty_file_guard]], [[feedback_github_deployment_bash]].
