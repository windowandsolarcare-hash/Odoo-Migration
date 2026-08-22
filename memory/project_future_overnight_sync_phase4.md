---
name: Future Task — Overnight Sync via Action 955
description: Switch _run_daily_sync to call action 955 instead of _sync_so_with_workiz for task sync + unified code path
type: project
originSessionId: 941c4896-3b5a-44bd-a6aa-b5805837b580
---
Switch the overnight batch sync (`_run_daily_sync` in dashboard.py) to call `_phase4_full_sync()` (action 955) instead of `_sync_so_with_workiz()`.

**Why:** Action 955 is the single source of truth (header + lines + tasks). Overnight sync currently skips task sync and duplicates field logic. Unifying means one code path everywhere.

**How to apply:** When ready to implement:
- Replace `_sync_so_with_workiz(so['id'])` calls in `_run_daily_sync` with `_phase4_full_sync(so['id'])`
- Keep existing sleep logic (1.5s between calls, 20s pause every 20 calls)
- Summary email: track ok/fail counts instead of per-field diffs (action 955 returns ok + message)
- Optional: add richer return payload to action 955 if per-field diff in email is wanted
- Only loss: granular "field X changed A → B" detail in email body
