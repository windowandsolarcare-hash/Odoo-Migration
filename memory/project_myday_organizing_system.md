---
name: project_myday_organizing_system
description: "My Day 'keep tasks under control' system (2026-07-12): guided Sweep triage + no dateless captures + auto-park stale >14d. Built ON the existing Waiting/resurface + bulk machinery, not around it."
metadata:
  node_type: memory
  type: project
  originSessionId: 67954fc8-a6c6-48fa-88c2-cfe13d71df3d
---

**Goal (DJ 2026-07-12):** "best way to keep my tasks under control and looking organized." Diagnosis: My Day already had the full toolkit (status To Do/🟡 Doing/⏳ Waiting + "check back on" resurface date + pin + Today/This-week/Earlier sections + Bulk-apply sheet). The list looked out of control not from missing features but because stale items were never *run through* those tools. So the fix = a PROCESS layer + two leak-guards, all reusing existing endpoints (`/api/myday/update` accepts date/time/status/wait_until; `/api/myday/delete`; `/api/myday/done`).

**Three pieces shipped (myday.py 3bcf2a0 / myday.html ff13e00):**
1. **🧹 Guided Sweep** (myday.html) — button in the modebar next to ☑ Select. `openSweep()` builds candidates = source==='task' && !scheduled && (resurfaced OR (status!='waiting' && (no date OR date<today))). One card at a time, big buttons **✓ Done** (→/api/myday/done: Done tab + recur-spawn) · **✅ Today** (blue; update date=today,status=todo,wait_until='') · **⏳ Park…** (reveals +3d/+1wk/+2wk/+1mo → status=waiting,wait_until=date) · **🗑 Delete** · **⏭ Skip** (full-width, no-op advance). Progress "n of N". Done added 2026-07-12 (commit f670cc9) — Delete=junk, Done=finished (kept both per DJ). `_swBusy` guard + 10s AbortController timeout (phone double-tap/hang rules). Bottom-sheet `#sweep-modal` cloned from `#add-modal` pattern (registered in the modal CSS selector lists + `fitModal` array). closeSweep()→load().
2. **No dateless captures** — `/api/myday/add` now defaults a blank `date` to `today_pt().isoformat()`. Fast brain-dump still works but lands on Today, never adrift in "Earlier". Covers BOTH the add form and editor-new (single backend point).
3. **Auto-park stale** — `_autopark_stale(tasks, today)` in `api_myday` (runs each load, right after `_rollforward_recurring`). A to-do overdue >14d with status=='todo', NO priority, not recurring/pinned/scheduled → writes x_myday_status='waiting' + x_myday_wait_until=today+14. Drops into the collapsed ⏳ Waiting group and resurfaces in 2 weeks. Conservative (priority/flagged items stay put); never deletes.

See [[project_myday_recur_rollforward]], [[project_myday_task_lifecycle]], [[project_activities_org_v2]], [[project_myday_action_catalog]]. All three lean on the lifecycle fields already built — do NOT rebuild Waiting/resurface.
