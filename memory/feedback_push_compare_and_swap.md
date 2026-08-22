---
name: feedback_push_compare_and_swap
description: "Every Contents-API push MUST PUT with the sha fetched when you READ the file, never a freshly re-fetched sha right before the PUT — so a concurrent change 409s instead of silently clobbering. The durable fix for the multi-session clobber class."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 8aa212a8-bcad-463e-b17d-ebf080940e01
  modified: 2026-08-22T22:56:45.936Z
---

**When pushing a file via the GitHub Contents API (gh api or GitHub MCP), PUT with the `sha` you fetched at the moment you READ/based-your-edit-on the file — NEVER re-fetch a fresh `sha` right before the PUT.**

**Why:** if you re-fetch the sha immediately before pushing, your PUT always succeeds even when another session changed the file in between — silently overwriting their work. If instead you send the sha from when you read it, GitHub returns **409 (stale sha)** on any concurrent change, so you CATCH it → re-fetch → re-apply your edit on top.

**How to apply:**
- Read file → capture BOTH content and its `sha` together. Edit locally. PUT with THAT captured sha. On 409: re-read (new content + new sha), re-apply your change, retry. Never "just grab a fresh sha and force it through."
- This is optimistic concurrency / compare-and-swap. Lead's AGENT_MAIL pushes already do this (read sha+content together, PUT with it) — that's why they're collision-safe.

**★ GOTCHA (will bite whoever copies this) — use the BLOB sha, not the COMMIT sha.** The sha you pass to the PUT must be the **blob sha from `contents/<path>` (`--jq '.sha'`)** — the file's content hash — NOT the **commit sha from `commits?path=…`**. Both are 40-hex and both look right in a variable named `sha`. Pass the *commit* sha and GitHub rejects EVERY push as a conflict, which reads like "the guard is broken" and tempts the next person to just drop the flag — turning the safety feature into the reason it gets removed. (Mail-watchers often store *commit* shas for change-detection, so this mix-up is one copy-paste away — keep the two uses separate.)

**On a 409/abort: re-fetch, re-apply YOUR change on top of THEIRS, push again. NEVER `--force` past it.** `--force` is only for "I have personally diffed and the deletions are intended," never for clearing a red conflict message. A claim/coordination protocol is a statement of *intent*; the race is decided at *write time*, so only a check at the moment of writing can prevent it.

**Why the weaker guards are NOT enough** (proven 2026-08-22, two Portal sessions raced portal files twice in 20 min):
- **"Claim the file in mail" failed** — a 44-second race: the other session was already mid-flight when the claim posted.
- **The line-count / byte regression guard failed** — the clobber was −14 lines, which read as a normal small edit, not a regression.
- Only the **sha compare-and-swap** actually caught a clobber (the rejected-on-stale-sha push is how the collision was even discovered).

Related: [[feedback_multiagent_collision_field_html]], [[feedback_regression_guard_pushes]], [[feedback_gh_push_empty_file_guard]], [[project_cloud_session_env_limits]]. Governing context: one-writer-per-file ownership on the SESSION ROSTER is the first defense; compare-and-swap is the backstop when two sessions touch the same file anyway.
