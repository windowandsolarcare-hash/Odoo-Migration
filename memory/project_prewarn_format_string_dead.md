---
name: project_prewarn_format_string_dead
description: "The warn-before-action (prewarn) matcher was SILENTLY DEAD from ship until 2026-10-05 — a literal % in a %-formatted regex raised ValueError on every call, swallowed by a fail-open try/except, so no warnings ever injected + prewarn_shadow stayed 0 rows. Lesson: a pyflakes 'unsupported format character' is a REAL runtime bug — run it, never dismiss."
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-06T04:41:25.042Z
---

`routers/owner/memory_store.py` `_prewarn_tokens` built its regex as
`re.findall(r'[a-z0-9_./%-]{%d,}' % _PREWARN_TOKEN_MINLEN, ...)`. The char-class literal contains a `%`
(for percent-encoded paths); Python's `%`-format operator reads `%-]` as a conversion spec →
**`ValueError: unsupported format character ']' (0x5d)` on EVERY call** (verified by running
`'[a-z0-9_./%-]{%d,}' % 5`).

**Blast radius:** `hook_prewarn` (`POST /owner/api/memory/hook/prewarn`) calls `_prewarn_tokens(command)` inside
a `try/except` that is **fail-open → `match:null`**. So the tokenizer threw on every command → caught → the
matcher NEVER matched → **no warnings ever injected (even live mode) AND zero `prewarn_shadow` rows ever
written** (the shadow write only runs AFTER a match). PG-verified 2026-10-05 (wsc-memory-pillar `mem_records`):
`prewarn_shadow` = 0 rows, while the match corpus existed (`solved_errors` = 209). So the ~9/30 "precision
review" had NO data — not thin, zero.

**Fix (2026-10-05):** build the pattern WITHOUT %-formatting (identical regex `[a-z0-9_./%-]{5,}`):
`re.findall(r'[a-z0-9_./%-]{' + str(_PREWARN_TOKEN_MINLEN) + r',}', ...)`. After fix, shadow starts collecting
on deploy; needs ≥1 week of fleet activity OR ~30–50 matched rows before a real precision rate (matches are
rare — must clear `_PREWARN_MIN_SCORE` against the lessons).

**Why this matters / How to apply:**
- A pyflakes **`'...' % ... has unsupported format character`** warning is a REAL runtime `ValueError`, not lint
  noise. RUN it before concluding. (I dismissed this exact warning twice this session as a "false positive"
  without running it — it was real. See [[feedback_no_conclusion_from_single_test_sporadic]],
  [[feedback_verify_limits_before_declaring]].)
- Escape a literal `%` in a `%`-formatted string as `%%`, or drop `%`-formatting (concat/f-string) — the latter
  can't be re-broken.
- When a feature "produces nothing" (empty table / no effect), suspect an exception swallowed by a **fail-open
  `try/except`** — the belt that keeps the hot path alive also hides a total outage. Grep the path for the
  broad `except`.
- Related: [[feedback_odoo_verify_content_not_status]], [[project_endpoint_map]] (hook_prewarn is a headless
  NOTIFY_SECRET endpoint).
