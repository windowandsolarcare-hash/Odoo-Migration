---
name: feedback_windows_python_path_and_append_guard
description: "TWO burns (2026-08-27): (1) Windows python CANNOT read bash-style /c/Users/... paths — use C:/Users/... always. (2) The b64>1000 push guard is NOT enough for APPEND-ONLY files (AGENT_MAIL.md) — a partial write passes it and clobbers history. Guard on combined>=prior length."
metadata:
  node_type: memory
  type: feedback
  originSessionId: 8aa212a8-bcad-463e-b17d-ebf080940e01
  modified: 2026-09-03T15:59:56.142Z
---

**Two related burns on 2026-08-27 that together truncated AGENT_MAIL.md to a single entry (recovered from git history commit a1702632).**

**1. Windows python cannot open `/c/Users/...` (MSYS/bash-style) paths.** git-bash `>` redirects resolve `/c/Users/dj/foo` to `C:\Users\dj\foo` fine, but when a `python - <<'PY'` heredoc (Windows python) then does `open('/c/Users/dj/foo')` it raises `FileNotFoundError`. **ALWAYS use Windows-style `C:/Users/dj/...` inside python** (read, write, os.path.exists, os.remove). This exact mismatch silently made a `mail_old.md`/`mail_good.md` concat step read NOTHING, so the "combined" file was only the new entry.

**2. The `b64 length > 1000` push guard does NOT protect append-only files.** For AGENT_MAIL.md (and any file where you PREPEND to existing content), a truncated payload that contains ONLY your new entry can still be >1000 b64 chars, so it sails past the guard and **overwrites the entire history**. The empty-file guard ([[feedback_gh_push_empty_file_guard]]) only catches near-zero.
- **Fix / rule:** for append-only mail/log pushes, guard on **combined length >= prior file length** (or line-count >= prior), not a fixed floor. Fetch prior content, build combined = new + prior IN PYTHON (Windows paths), assert `len(combined) > len(prior)` AND `prior_first_heading in combined`, THEN push with compare-and-swap ([[feedback_push_compare_and_swap]]).
- **Cleanest pattern:** do the WHOLE mail edit inside ONE python block (read prior via `open('C:/...')`, mark ✅ via `.replace(tgt,'✅ '+tgt,1)`, prepend new entry, base64, fetch head sha via `subprocess`, write payload json) — no bash/python path handoff, no temp-file concat across tools. And do NOT `rm` your recovery source until the push is CONFIRMED (I deleted the good copy in the same command whose python had already failed).

**3. ★ NEVER assert your integrity-check ANCHOR on the heading you're about to modify (bit me 3× on QC-mark pushes, 2026-09-02/03).** When marking an entry ✅ you do `combined = new_entry + cur.replace(target_heading, '✅ '+target_heading, 1)`. If your guard then asserts `original_first_heading in combined`, it FAILS — because that first heading is exactly the one you just prefixed with ✅, so the un-prefixed form is gone from `combined`. The AssertionError aborts the python, `mail_payload.json` never gets written, the later `gh api --input` runs against a missing file, `$NEWSHA` comes back EMPTY, and (if you unconditionally `echo "$NEWSHA" > baseline`) you WIPE the baseline file to empty while the mark never landed. **Fixes:** (a) anchor the guard on YOUR OWN entry's unique text (`assert "<my unique subject>" in combined`) + `len(combined) > len(cur)+N`, NEVER on the modified heading; (b) only write the baseline when the push actually returned a sha — `test -n "$NEWSHA" && echo "$NEWSHA" > baseline` (guards against clobbering baseline on a failed push). Recovery if baseline got emptied: re-fetch live `.sha` and diff; the mark is idempotent so just redo it.

Recovery when it happens: `gh api "repos/<owner>/<repo>/contents/<path>?ref=<good_commit_sha>" --jq '.content' | base64 -d` to pull any prior version; find the good commit via `gh api "repos/.../commits?path=<path>"`. Related: [[feedback_bash_tmp_not_persistent]], [[feedback_regression_guard_pushes]], [[feedback_push_compare_and_swap]].
