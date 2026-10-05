---
name: project_holds_coverage_one_source
description: "Maintenance-advance / booking-request DRAFT reserves ('holds') now surface as ghost rows on the board + Schedule Calendar, from ONE source: scheduler.holds_list_for_range() -> a SEPARATE top-level `holds` key in /owner/api/calendar_jobs (never inside `days`). SHIPPED LIVE 2026-10-05 (deploy a41af4cc)."
metadata:
  node_type: memory
  type: project
  originSessionId: c2b57d38-a392-4882-ad3e-470c2240e939
  modified: 2026-10-05T07:43:27.557Z
---

**Shipped 2026-10-05 (deploy a41af4cc), DJ "deploy". Origin: Operator BUILD SPEC 2026-10-03** — a morning looked wide-open on the board but was fully held by maintenance-advance DRAFT jobs the scheduler reserves but the sale/done calendar couldn't see. DJ wants holds KEPT and VISIBLE "like jobs that aren't really jobs yet."

**ONE SOURCE OF TRUTH (the whole point — don't let it fork again):**
- `routers/owner/scheduler.py` → **`holds_list_for_range(date_from, date_to)`** returns the flat display list `[{slot(ISO UTC), time, end, name, city, so_id, so_name, kind, notice_sent, state}]` (reshaped from the already-live `held_details_for_range`). `kind` ∈ `maint` / `request` / `hold`. FAIL-OPEN to [].
- **`GET /owner/api/holds/in_window`** is now a THIN WRAPPER over it (byte-identical output; still live).
- **`dashboard._build_calendar_jobs`** adds a **SEPARATE top-level `holds` key** to `/owner/api/calendar_jobs` (built from the same helper). ★ It is NEVER inside `days` — so holds can't leak into job totals / pay / skipped math. `_empty` fallback carries `holds: []`.

**Consumers (all read that one `holds` key; labels identical everywhere):**
- `static/owner/v2_command.html` `_loadOnExtras`: reads holds off the already-cached calendar_jobs payload (same cjson key `'cal:on'`, no extra network). The separate `/api/holds/in_window` FETCH was RETIRED here.
- `static/owner/v2_calendar.html`: ghost "Hold" rows in month-cell dot + week chips + day-modal rows + upcoming, via shared helpers `_mergeHolds()` (race-free per-date REPLACE across load/loadUpcoming/ensureDayLoaded) + `holdsForDate()` + `_holdLabel()`. Tap → opens the SO (`v2_job.html?open_so=`). NEVER counted in job totals; month job-count excludes holds.
- **Labels (same as the board):** `request`="booking request"/"Request — pending" (info); `maint`="maintenance hold"/"Hold — notice sent[, confirmed]" (info) or "Hold — notice NOT sent" (warn); else "hold"/"Hold" (info).

**My Day:** DROPPED by Lead's call — `v2_myday.html` is a to-do/reminders view with no per-day job list; the board + Schedule Calendar cover holds.

**How to apply / gotchas:** if you ever need holds in a new view, read the `holds` key off `/owner/api/calendar_jobs` (or call `scheduler.holds_list_for_range`) — do NOT add a second derivation or re-add the separate `/api/holds/in_window` fetch (that's the divergence we just removed). No route was added/removed by this change. See [[feedback_reuse_canonical_endpoint]], [[feedback_check_endpoint_map_first]].
