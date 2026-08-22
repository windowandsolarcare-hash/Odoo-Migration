---
name: Apr 30 evening session — UX polish, GPS Phase 1, Re-engagement rename, regression guard, gate code, stale SOs
description: Long session. Photo flow polish (Snap button, retry, save to WSC Jobs folder via File System Access API). Activities Mark Done fixes + Done tab + Reopen. record_check_payment v2 (multi-SO + tip detection + empty-SO error). Phase 5 "Follow-up" renamed to "Re-engagement" everywhere. New Render Claude tools: add_link_to_todo, delete_workiz_job. Stats drill-down + Stale SOs page with WZ+Odoo pills. Gate code on active job view. GPS Phase 1 logger (collect pings while clocked in; per-person model with redundancy). REGRESSION INCIDENT: another Claude Code chat pushed a 3565-line dashboard.py over the live 5842-line version, wiping 2277 lines. Fixed + added regression guard at 3 layers (github_push_file tool, safe_deploy.py CLI, CLAUDE.md warning).
type: project
originSessionId: 96c7eadf-7840-4091-9290-6d3aed1806c8
---
## Big strokes

### Activities (mail.activity / project.task work)
- Mark Done now keeps DJ on the Open list (was jumping to Done) — `field.html`/`activities.html` updated
- Mark Done button text resets per activity (was sticking on "✅ Done")
- `/api/todos/done` now reads BOTH mail.activity AND project.task (commit 19854da0); new `/api/todos/reactivate` endpoint with Reopen button on every Done card
- The 3 Mark Fredricksen project.task records that were invisible → now visible

### Linked AWP PO #70 + renamed P00002 → P00101
- Activity #70 "Order screen material" now has a clickable link to the AWP PO (was empty note)
- PO renamed from P00002 to P00101 (DJ wanted the new sequence start to apply); sequence bumped to next=102 to avoid collision
- Activity note updated to match

### New Render Claude write tools
- **`add_link_to_todo(todo_query, url, label?, source?)`** (commit 97f8e7d5) — append a link to an existing to-do. Searches both mail.activity (summary) and project.task (name). CLARIFY when ambiguous.
- **`delete_workiz_job(uuid, partner_name?)`** (commit c4c2e4ff) — PERMANENT delete: Workiz API + Odoo SO unlink + project.task cleanup. **Blocks if invoice linked** to the SO. Order: tasks → SO → Workiz (Workiz fires last so Odoo failures abort safely).

### record_check_payment v2 (commit 0e6726af / 1645e679)
- **so_id is now optional** — when omitted, walks Contact↔Property partners and finds all open invoiceable SOs (state in [sale,done] AND invoice_status='to invoice')
- 0 SOs → friendly error
- 1 SO → proceeds
- >1 SOs → CLARIFY message listing them
- **Tip / amount-mismatch detection**: BLOCKS unless `acknowledge_mismatch:true` (or `tip:true`). Response on success includes a `⚠ TIP REMINDER` line if mismatch was acknowledged ("don't forget to add the tip to Workiz")
- **Empty-SO clean error** instead of opaque "No items available to invoice" Odoo trace
- **`_force_lines_deliverable(so_id)`** helper writes qty_delivered=qty_ordered on real lines before invoicing — fixes products with `service_policy='delivered_timesheet'` failing without timesheets logged

### Property partner naming quirk discovered
- Betsy Justice has 3 partners: Contact `Betsy Justice` + Property `"Betsy Justice, 255 E Avenida Granada"` + Property `"47446 Rabat Dr"` (no name on the 2nd!)
- Name-search "betsy" missed the Rabat property → wrong SO got charged
- Fix: always walk parent_id+child_ids, never name-match
- Saved as `project_property_partner_naming_quirk.md`

### Photo flow — three improvements
1. **📸 Snap Photo button** on active job (commit b76b9495) — uses `capture="environment"` to bypass the gallery chooser, opens camera direct
2. **Auto-retry** on weak signal (commit 3d1748d7) — 3 attempts, exponential backoff (1s/2s/4s)
3. **Saves a copy to phone Downloads OR a user-picked folder** (commit ec91e94d) — File System Access API. DJ picks "WSC Jobs" folder once, then silent writes thereafter. Android Gallery auto-creates the album.
- **Filename rename**: from `17775678…jpg` (device timestamp) to `WSC_JeffO_2026-04-30_165107_1.jpg` (customer + date + time + seq) — same name on phone and Odoo

### Pull-to-refresh disabled site-wide
- All 7 HTML pages got `overscroll-behavior-y: contain` so DJ's scroll gestures don't trigger Chrome's full-page reload
- field.html refresh interval kept at 5min (real fix was the gesture)

### Stats day drill-down
- New `WZ` + `S0xxxx` pills under each row (commit ae76650c) so DJ can investigate from the day-list view

### Stale SOs cleanup page
- New `/owner/stale_sos` page (commit 3c72fcc8) — filterable by year + Workiz status + customer search; rows show customer / date / job type / amount + WZ + Odoo pills
- Tile on owner hub (red-bordered 🧹 Stale SOs)
- 320 stale SOs found ($56.7k aggregate); biggest cohort = 2025 "Submitted" (190 SOs / $30k)

### Gate code on active job (commit e446d8ed)
- Between address and Navigate button: `🔑 Gate: 1234` (amber) when set, or `NO GATE CODE` (red caps) when empty
- Backend: `gate_code` added to `/api/dashboard` schedule response
- Source: `x_studio_x_gate_snapshot` on sale.order

### Re-engagement terminology rename
- Phase 5's customer cycle reminder titled "Follow-up: X — Y" → "Re-engagement: X — Y" (commit fb5de5b6)
- Phase 5 chatter prefix "[Phase 5] Re-engagement Task created..."
- create_todo lost the `[Render] Follow-up:` prefix — now uses DJ's actual phrase as title; partner_id is OPTIONAL (personal todos no longer require a customer)
- Render Claude system prompt: "follow up with X" → always create_todo (personal); "Re-engagement" reserved for Phase 5
- isFollowupTodo predicate matches both new "re-engagement" + legacy "follow up"/"reactivation" keywords
- DJ renamed Workiz SubStatus "Follow Up Trigger" → "Re-engagement Trigger" + JobType "Follow Up Lead" → "Re-engagement Lead" — Render constants updated to match (commit 02190a29)
- **Task #25 closed as obsolete** — no need to extend SMS to project.task; clean split now: mail.activity (legacy SMS only) vs project.task (cycle reminders + personal todos)

### Manage Shifts backend (commit 390bfdd2)
- Frontend was already deployed but the 5 backend endpoints (/api/payroll/shifts list + shift/create + shift/update + shift/delete + gusto_export) had never been built → "Error: load failed"
- Added all 5 endpoints + `_force_lines_deliverable`-style helpers (`_shift_id`, `_split_shift_id`, `_utc_to_pt_str`, `_pt_str_to_utc_iso`, `_round_quarter`, `_format_shift_for_ui`)
- Backed by the SAME ir.config_parameter JSON storage (no schema change)
- Surfaces the open shift (clocked-in but not out) so DJ sees live work-in-progress
- Edit-then-update on the open shift converts it to a closed shift in the JSON log + clears the clockin marker

### GPS Phase 1 — data collection (commits 38c3030a + 6d4b5d21 + 466c97d1)
- New Odoo Studio model `x_gps_ping` (id 1024): employee_id, timestamp, lat, lng, accuracy, shift_id, active_so_id, active_task_id
- POST `/api/payroll/gps_ping` endpoint
- `gps_tracker.js` shared module (window.WSC_GPS.start/stop/isActive) — used by timeclock.html AND field.html
- timeclock.html: starts watcher in updateClockUI when clockedIn=true
- field.html: polls /api/payroll/status every 60s + on visibilitychange → starts/stops watcher based on the same source-of-truth clock state
- New `/api/whoami` endpoint resolves access_code → employee_id for field.html
- Throttle: 5min OR 100m moved (whichever fires first). Battery-friendly.
- Two-person scenario: both phones ping independently with own employee_id; phase 3 will create per-person timesheets. Bonus: redundancy if one phone dies (phase 2 auto-detect "rode together today" via overlap)
- Tasks #39/40/41 queued for Phases 2-4

### REGRESSION INCIDENT — 2277 lines wiped, restored
- 22:47 UTC, commit `a6bb406e` by `windowandsolarcare@gmail.com` replaced dashboard.py with a 3565-line version (was 5842 lines), wiping Manage Shifts CRUD, GPS endpoints, Stale SOs, whoami, todos/reactivate
- Cause: a different Claude Code chat had a stale local copy and pushed it
- Restored from my (current) local in commit `ad98b65c`

### Regression guard — three layers (commit 41351838 + safe_deploy.py + CLAUDE.md update)
1. **Render Claude `github_push_file` tool** — fetches current GitHub version, refuses if new content drops >100 lines OR >25% bytes. Override with `acknowledge_regression: true`.
2. **`C:\Users\dj\safe_deploy.py`** — same guard for any Claude Code chat. CLI: `python safe_deploy.py --repo X --path Y --local Z --msg "..."`. Use `--force` to override.
3. **CLAUDE.md updated** with mandatory pre-push checklist + warning about the incident at top of Deployment section. Memory note `feedback_regression_guard_pushes.md`.

## Files touched tonight (Saunders Render App repo)

- `routers/owner/dashboard.py` — many edits (final ~290k bytes / ~5900 lines)
- `static/owner/field.html` — Snap Photo, retry, folder picker, gate code display, GPS watcher, refresh tweaks, pull-to-refresh disabled
- `static/owner/timeclock.html` — Manage Shifts integration with shared gps_tracker.js, pull-to-refresh disabled
- `static/owner/activities.html` — Mark Done UX, Reopen button, isFollowupTodo predicate updated, pull-to-refresh disabled
- `static/owner/stale_sos.html` — NEW page
- `static/owner/quote.html` — pull-to-refresh disabled
- `static/owner/reactivation.html` — pull-to-refresh disabled
- `static/owner/index.html` — Stale SOs tile + pull-to-refresh disabled
- `static/owner/gps_tracker.js` — NEW shared module
- `static/tech/index.html` — pull-to-refresh disabled

## Files touched tonight (Odoo-Migration repo)

- `1_Production_Code/zapier_phase5_FLATTENED_FINAL.py` — "Follow-up" → "Re-engagement" titles + chatter messages

## Memory files added/touched

- `project_invoice_qty_delivered_gate.md` — NEW (the Betsy Zelle case)
- `project_property_partner_naming_quirk.md` — NEW
- `project_reengagement_flow.md` — NEW (replaces project_followup_flow.md)
- `project_gps_timesheet_autofill.md` — NEW
- `feedback_regression_guard_pushes.md` — NEW
- `reference_render_claude_write_tools.md` — extended with add_link_to_todo, delete_workiz_job, record_check_payment v2, create_todo v2

## Open future tasks (parked)

- **#17** Workiz Quote substatus + webhook for instant sync (DJ-blocked on Workiz substatus + automation creation)
- **#39** Phase 2: Cluster pings into stops + match to customer properties
- **#40** Phase 3: Auto-create per-person timesheet entries from matched stops + review UI
- **#41** Phase 4: Mileage logs + native Android wrapper for background GPS

## DJ's manual / blocked items

1. Workiz "Quote" SubStatus + automation webhook for the Quote workflow (still blocked since Apr 30 morning)
2. Workiz auto-text rule for JobType=Quote (don't text customers about coming for a quote visit)
3. Workiz cell-phone area code spec for `Re-engagement Trigger` SubStatus rename — verify the automation still fires on the renamed substatus

## Things to verify after Render redeploy

- Time Clock → Manage Shifts loads (was failing for both DJ and Danny)
- Active job view shows gate code or NO GATE CODE
- Field Assistant pull-to-refresh is dead
- Stale SOs page accessible at /owner/stale_sos
- 📸 Snap Photo button works on active job
