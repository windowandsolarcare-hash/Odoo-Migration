---
name: project_clock_system_rebuild
description: THE clock-in/out spec + rebuild plan. Offline-first local-authoritative clock state, timestamped sync queue, whole-crew clockout at home, manual End Day backup. Read FIRST before touching any clock code.
metadata:
  node_type: memory
  type: project
  originSessionId: ff199142-d29c-4bba-851b-f9d45aa43d20
---

# Clock-in/out rebuild — spec, confirmed bugs, design (DJ approved 2026-06-08)

## ✅ BUILT & DEPLOYED 2026-06-08 (live commits dashboard a628f9e1 / field 32f9efef, deploy `live`)
All 4 bugs fixed + offline-first foundation + End Day, in dashboard.py (NOT timeclock.py — timeclock.py's payroll routes are SHADOWED; main.py includes owner_dashboard before owner_timeclock so dashboard.py's `/owner/api/payroll/*` win).
- **Bug #2 (offline wrong time):** `clockin_crew` now honors body `check_in` (device ISO/UTC tap time) via new helper `_parse_client_ts`. Frontend `doCrewClockIn` sends `new Date().toISOString()`; queued retries reuse the saved ts.
- **Bug #3 (stale overwrite):** `clockin_crew` checks open att's PT date (`_att_pt_date`). Same-day → leave untouched (report `already`), never overwrite. Prior-day → close it (check_out = check_in+1min, flags for review) + create fresh. Return now includes `already[]`.
- **Bug #1 (crew not clocked out at home):** new `_crew_today_ids()` + `_crew_home_clockout(driver, co_utc, cancel=)` called at ALL 3 home-arrival sites (gps_ping, webhook transition enter, webhook location ping) right after the driver's own clockout/cancel. Clocks out / cancels the rest of `crew.today.<date>`.
- **Bug #4 (no manual clockout):** new `POST /api/payroll/clockout_crew` {employee_ids?, check_out?} — offline-safe, idempotent (skips already-out), falls back to crew snapshot. Frontend: 🏁 **End Day** button in the clock bar (was break-bar), double-tap guarded, saves intent to localStorage `wsc_pending_clockout` BEFORE fetch, drains via `_flushPendingClockout()` on load + `online` event.
- **UI:** clock bar shows `● Clocked in <time> · Crew: N`. Frontend persists crew in localStorage `wsc_crew_today`.
- **⚠ Stage 3 NOT done:** Break button is NOT yet offline-queued (still direct POST). localStorage `wsc_shift`/`wsc_clock_queue` authoritative-state model from the spec was simplified — current impl uses per-action pending keys (`wsc_pending_clockin`/`wsc_pending_clockout`) not a unified queue. Good enough for the 4 bugs; revisit if break offline-safety needed.
- **⚠ DO NOT run mutating smoke tests on payroll endpoints** — see [[feedback_no_mutating_smoketest_payroll]]. clockout_crew with empty body clocked out a live shift during testing; had to reopen att #103.

## FOLLOW-UP FIX 2026-06-08 (commit f602b2b0): stale crewSetDate suppressed crew screen
**Symptom:** DJ pressed a job's Navigate button, no crew screen appeared, even though he was clocked OUT. **Root cause:** the Navigate gate is `if (_fieldClockedIn || _crewSetToday())` where `_crewSetToday()` reads client-only localStorage `crewSetDate` (stamped by Let's Go / `_markCrewSet`). It was NEVER cleared when the server clocked the crew out (home auto-detection / mid-day clockout) — only End Day cleared it. So after an auto-clockout, the flag stayed = today → Navigate skipped the crew screen AND skipped re-clock-in → working unclocked. **Fix:** new `_refreshClockState()` is the single source of truth — fetches `/api/payroll/status`, and on a DEFINITIVE `clocked_in:false` clears `crewSetDate` + `wsc_crew_today` (offline/throw → keep last state, never clear on uncertainty). Called in `_initFieldEmployee` + on a new `setInterval(_refreshClockState, 60000)` so a mid-day clockout self-heals within 60s without reload. **Lesson:** any client flag that gates a clock action must be reconciled against server clock state, because the server can clock you out behind the app's back (GPS home detection).

---


DJ's #1 goal: **make clock-in and clock-out CORRECT.** Job-detail editing is separate/later ([[project_workiz_exit_field_editability]]). Build in a FRESH session (clean context) — payroll-critical + multi-file (field.html + dashboard.py), the two files that regressed 2026-06-08. Fetch fresh from GitHub, push via safe_deploy.py, node --check + py_compile. [[feedback_regression_guard_pushes]]

## INTENDED SPEC
1. **Offline-first** — no cell signal in some spots; clock state lives LOCALLY (localStorage) and syncs when network returns. This is the whole reason it's app-side, not Render/Odoo-direct.
2. Press **Navigate** (open job detail) → if clocked in, just navigate; if not, show **crew screen**.
3. Crew screen: mark who's driving with you → **Let's Go** → navigates AND starts the day (clock-in) for everyone marked.
4. **OwnTracks** tracks GPS through the day (already works — pings to webhook).
5. Arrive **home** → auto-stop shifts for the **WHOLE crew**.
6. **Break button** on schedule → pause clock for lunch.

## CONFIRMED BUGS (current code, why it never worked)
1. 🔴 **Home arrival clocks out only DJ, not the crew.** OwnTracks webhook (dashboard.py ~9606 enter / ~9649 ping-home) finds `_find_open_att(emp_id)` for DJ's TID only. Crew clocked in via `clockin_crew` (saved in ir.config_parameter `crew.today.<PT-date>`) never get clocked out. MUST: on home arrival, clock out every employee in the crew snapshot.
2. 🔴 **Offline clock-in records WRONG time.** `_savePendingClockin` (field.html ~2291) stores `{employee_ids, date}` — NO timestamp. Backend `clockin_crew` (dashboard.py ~8924) stamps `check_in = now_utc` at POST time. Offline clock-in at 8am that syncs at 11am records 11am. MUST: record device timestamp at tap; backend honors provided check_in.
3. 🟠 **Stale-shift overwrite.** `clockin_crew` line ~8937: if an open att exists (prior day never closed), it WRITES today's check_in onto it instead of creating fresh. MUST: if open att is from a prior PT day, close it (or leave + create new), never overwrite.
4. 🟠 **No manual clock-out in field app.** If GPS doesn't fire, shift runs forever. Only recovery is /timeclock page.

## APPROVED DESIGN
**Local owns the clock; Odoo is the durable record.** Every event (in/out/break-start/break-end) recorded in localStorage with the REAL device timestamp at the moment it happens, queued, and synced to Odoo `hr.attendance` with its ORIGINAL timestamp whenever signal exists.

**Clock-OUT = Auto at home (whole crew) + manual "End Day" backup** (DJ chose this 2026-06-08). Auto for convenience; End Day button guarantees correctness when GPS misses. End Day works offline (queues with timestamp).

### Build stages
1. **Foundation (offline core):**
   - localStorage `wsc_shift` = authoritative state `{clocked_in, crew:[{id,name}], clock_in_ts(ISO PT), break:{...}}`.
   - localStorage `wsc_clock_queue` = events `{type:'in'|'out'|'break_start'|'break_end', emp_ids, ts_iso, idem_key}`.
   - Sync flush on app load + on `online` event + periodic; POST events with their timestamps; idempotency keys prevent double-create.
   - Backend: `clockin_crew` accept explicit `check_in`; NEW `clockout_crew` with explicit `check_out` + emp list; FIX stale-shift overwrite.
2. **UI:** header status ("Clocked in 8:02a · Crew: 2"), **End Day** button (clocks out whole crew, offline-safe), Break button offline-safe. Keep existing Navigate→crew-modal→Let's Go flow (it's good); make its clock-in carry the real timestamp.
3. **Auto clock-out whole crew at home:** OwnTracks webhook — on home arrival, read `crew.today.<date>` snapshot and clock out ALL of them (with check_out=now; arriving home = has signal). Keep the <30min short-trip cancel but only for DJ's own shift, and reconsider whether it should cancel the crew too.

### Key existing pieces (current good code)
- Frontend: `openNav()` (~2250), `openCrewModal()` (~2259), `doCrewClockIn()` (~2313), `_savePendingClockin/_flushPendingClockin` (~2291), break fns (~1327), `_fieldClockedIn`, `_initFieldEmployee` (~1293, reads /api/payroll/status). clockin-bar.js (shared top green "Clocked In" bar) was TEMP-DISABLED on field.html during the rebuild test — **RE-ENABLED 2026-06-09** (commit d8b5b61a). It now shows on every owner page incl. field.html + weekly_reports.html. So field.html has BOTH the top clockin-bar AND the bottom break-bar (Break + End Day) — redundant status display but different buttons; coexist fine (top bar z-index max; bottom break-bar z-index 55). Double clock-in is safe because clockin_crew treats a same-day open att as `already` (no overwrite).
- Backend: `/api/payroll/clockin_crew` (8924), `/clockout` (8957, single), `/status` (9095), `/break` (8991), `_find_open_att` (9169), OwnTracks webhook (9568). Store = Odoo `hr.attendance`. Crew snapshot = ir.config_parameter `crew.today.<PT-date>`.
- TID→emp map: ir.config_parameter `owntracks.tid.<TID>`. Home coords: `owntracks.home.<emp>.lat/lng/radius`. [[project_owntracks_home_detection]]

## Related
[[project_owntracks_setup]] · [[project_owntracks_home_detection]] · [[session_jun03b_clockin_bar]] (disabled bar) · [[project_timer_architecture]] (localStorage+queue pattern to mirror)
