---
name: project_command_center
description: "Schedule Command Center (schedule_hub.html) — routed /owner/command-center, its data endpoint, and how its cards were enriched to match Field Assistant."
metadata: 
  node_type: memory
  type: project
  originSessionId: 8794a0de-b651-444b-8ec4-52ed56f6927d
---

**Schedule Command Center** = `static/owner/schedule_hub.html`, served at **`/owner/command-center`** (route added 2026-06-24 in `routers/owner/scheduler.py`, commit 0fe0c6c, no-store). URL: https://wsc-field-assistant.onrender.com/owner/command-center . 3 pills: ⚠️ Needs scheduling · 📅 On the schedule · 📆 Calendar. Has IndexedDB offline cache (cache-first-then-revalidate, db `wsc_cc`).

## Data endpoint — `/owner/api/calendar_jobs` (SHADOW)
Defined TWICE: `dashboard.py` (~L7844, route `@router.get('/api/calendar_jobs')`) and `calendar.py` (L14). **dashboard.py WINS** (registered first in main.py L136 vs L147) — edit the dashboard.py copy, the calendar.py one is dead. Returns `days{YYYY-MM-DD:[jobs]}`. Per-job fields: `time, name(customer), city, addr, uuid, status, job_type, so_id, so_name` + (added 2026-06-24, commit 68487c8) **`amount` (amount_total), `frequency` (x_studio_x_studio_frequency_so), `workiz_link`** + (added 2026-06-25, commit 62609ec) **`partner_id`** = customer/parent partner (`ship_parent_id or SO partner_id or shipping id`) — added to power per-card 📜 Text history. Filter: state in sale/done, workiz_status != Canceled.

## 📜 Text history button on Command Center cards (2026-06-25, commit d26dcb8)
Each job card (On-the-schedule + Calendar-day rows) now has a **📜 Text history** button (the imported Workiz SMS viewer — same `/owner/api/text_history?partner_id=` backend as Field Assistant). schedule_hub.html: `addTHButtons(container, rows)` runs AFTER each `WSCKit.renderResult` (renderResult has no per-row button support — inject post-paint, reading partner_id off the rows array by `data-i`, stopPropagation so the 📜 tap doesn't trigger the row's open-in-field nav). Self-contained modal `#th-modal`/`.th-card` + `openTextHistorySC`/`_thParse`/`_thIsMe`/`_thWhen`/`closeTHSC` + local `_esc` (schedule_hub has no global esc; WSCKit.esc exists but not exposed as bare `esc`). Shows "No imported text history yet" when partner has none. See [[project_workiz_chat_export_to_odoo]].

## Cards enriched to match Field Assistant (DJ 2026-06-24, commit 52ceb73)
DJ: Command Center cards were too sparse vs the Field Assistant schedule. Field card = status dot · time · customer · service+frequency · tags · WZ/SO links · $amount · ⋯ menu (field.html `renderSchedule` ~L1881). Enriched the Command Center "On the schedule" + calendar-day rows (via WSCKit.renderResult row model: title/amount/subtitle/meta/extra/badges) to show **customer · $amount · address · (time · service · frequency) · status**. Added `svcLabel(jt)` (mirrors field.html `labelFromJobType` L5815: combination→Combo, solar→Solar, window→Window, gutter→Gutter, commercial→Commercial, touch→Touch up, quote→Quote, else first word) + `jobMeta(j)` + `jobAmt(j)` helpers in schedule_hub.html.

## Personal Time cards show the note (2026-06-24, commits 1ac35c6 backend / 294665a frontend)
Like Field Assistant: a Personal Time block's note shows on the card. Note lives in SO `x_studio_x_studio_notes_snapshot1`, cleaned by dashboard.py `_personal_time_desc()` (strips `[Job Notes]` prefix). calendar_jobs now returns `description` (= that note) when `name=='Personal Time'`. schedule_hub.html helpers: `isPersonal(j)` (name or job_type == 'Personal Time'), `jobSub(j)` (Personal Time → description, else address), `jobMeta`/`jobAmt` suppress service/$ for Personal Time. e.g. card reads "Personal Time · 3:30 pm · Dad viewing".

## Timezone: "today" must be Pacific
schedule_hub `isoPlus()` was UTC (toISOString) → showed tomorrow after 5pm PT. Fixed Pacific-anchored (commit e7f71e7). See [[project_utc_today_bug]].

## REPLACE Field Assistant — Phase 1 WRAP (DJ 2026-06-28/29)
DJ's goal: make Command Center the front door and WRAP Field Assistant (don't rewrite the money/payroll/timer code — reuse its endpoints). Decided Path B (CC shell, reuse Field's engine). Phase 1 shipped:
- **CC is the hub PRIMARY card** — `static/owner/index.html` big top card now → `/owner/command-center` (was Field Assistant); also added a "Schedule (Command Center)" tile + `commandcenter` HELP entry to the Schedule & Dispatch group. Field Assistant stays as a group tile (it's the engine).
- **Seamless CC→Field handoff** (already mostly built): CC row tap → `onScheduleTap` → `/owner/field?open_so={so_id}&date_raw={d}&from=cc`. field.html on `from=cc`: hides schedule list + shows "Opening…" overlay (boot ~L1512), opens the job panel by id, back button (`.ap-close`) relabeled **"‹ Schedule"**, `apBack()` does `history.back()` → returns to exact CC state. CC remembers last pill via **`localStorage wsc_cc_view`** (`_saveView` in `show()`, restored at init).
- **🔁 Reschedule button ON cards** — `addRescheduleButtons(container, rows)` in schedule_hub.html (mirrors addTHButtons; reads `entity_id`/`title`, skips rows whose `_status` contains 'done'). Wired into On-schedule (cur+past), Calendar-day, AND Needs-scheduling lists.
- **Needs-scheduling cards now OPEN like any job** — `show('need')` onRow changed from `openReschedule` → `onScheduleTap` (opens the full Field panel, so a late Zelle/cash can be taken there). mapJob + skipped rows got `_draw` (+ skipped got `partner_id`).
- **🔁 Reschedule in the job 3-dot menu** (field.html) — new `job-rs-modal` (day/time only, reuses te-sheet styles) + `rescheduleJobFromMenu`/`openJobRsModal`/`submitJobRs` → POST `/owner/api/schedule/reschedule`. Menu item added in `toggleJobMenu` for real Workiz jobs (`uuid && soid`); shared by row menus AND the active-panel ⋯ (`toggleActiveJobMenu` sets data-attrs → toggleJobMenu). Reschedule via Workiz = see [[project_cc_reschedule_via_workiz]].
- **Paid jobs drop off "needs scheduling"** — calendar_jobs now returns **`paid`** (bool, via `_paid_status_by_so` which needs `invoice_ids` in the read). schedule_hub `_isSkipped` returns false when `j.paid` → a paid late-pay job stops showing as missed (and loses the red "skipped" badge on the schedule). DJ's "take the payment from the list and it drops off" flow.
- **Past Jobs sort fixed** — CC On-schedule past list now **newest-first** (`.reverse()`) to match Field Assistant (`/owner/api/past_jobs` returns `date_order desc`, "newest first"). CC had been oldest-first.

## Phase 2 (in-place job sheet) — BUILT then REVERTED 2026-06-29
Built an in-place job sheet (tap → instant `#jobsheet` slide-up, so_full detail + actions + "Open full job" handoff, payment/timer/photos kept in Field). **DJ REJECTED it same night** — he likes tapping a job going STRAIGHT to the full screen (Field panel), did NOT want the extra tap to reach payment. Fully reverted (commit b223e4e): all `onRow` back to `onScheduleTap` (tap → `/owner/field?open_so&from=cc` → full panel), sheet CSS/HTML/JS removed. ★ LESSON: DJ wants ONE tap to the full working screen; do NOT insert a lightweight preview layer between the list and the job. Any future "no page load" goal must bring the FULL panel (incl payment) in-place, not a stripped preview. Phase 2 is effectively on hold / needs a different approach.
KEPT from this session (DJ likes): overdue maintenance window 6mo→**1yr**; **Needs-scheduling buckets collapsible** (`renderNeedGroups`, state per-bucket in `localStorage wsc_ns_c:<name>`); reschedule buttons on cards; paid-drops-off.

## cc-mode overlay gotchas (field.html, fixed 2026-07-01)
- **Customer Brain "‹ Back" landed on the wrong screen.** From a CC-opened job, "👤 View Customer Brain" opens the office panel as a full-screen overlay (`openCustomersTab`) with its own back button. That back handler did only `off.style.cssText=''` — which in cc-mode on a WIDE screen reverts the office panel to a visible right COLUMN instead of hiding it, so DJ landed there instead of the job. Fix: back now `off.style.display='none'` (force-hide) + `if(activeJob) openJob(activeJob,false)` (re-show the job, which was never closed). Lesson: clearing an overlay's inline style reverts it to its base CSS (a column on desktop) — force `display:none` to truly hide.
- **z-index stacking in cc-mode:** the job panel `#active-panel.open` is z-index **300**, the Customer-Brain overlay is **500**. `#toast` was **200** → any toast was hidden behind the job panel. Bumped toast to **9999**. Rule: any field.html overlay/toast shown while a job is open must exceed 300 (Customer Brain 500). See [[project_navigate_next_address]].

## Gotcha: jobs opened via openJobById (CC handoff / search) lost their Workiz link (fixed 2026-06-30)
`field.html openJobById` builds the active job from `/api/so_history` and used to hardcode `workiz_link:'' , workiz_uuid:''` → the ⋯ menu's "Open in Workiz" (and any uuid-dependent item) grayed out even when the SO HAS a Workiz job. Fix: `so_history` (dashboard.py) now returns `so.workiz_uuid` + `so.workiz_link`; openJobById fills them; AND `toggleJobMenu` now falls back to building `https://app.workiz.com/root/job/${uuid}/1` when `data-workiz` is empty. Lesson: jobs opened from CC/search go through so_history, not the dashboard job object — any field the menu needs must be returned by so_history too.

## Still TODO
- "No page load" on tap is still wanted in principle, but ONLY if it brings the full job (payment/timer/photos) in-place — a preview-then-open-full layer is rejected. Big build; needs DJ testing. On hold.
- Phase 3 = port the full ⋯ action menu (WZ/SO/Property links, sync, add note, mark done, delete) onto CC cards.
- "To be scheduled" buckets to refine with DJ: 🔁 Skipped (past non-Done, non-paid = jobs he missed) · ⚠️ Overdue (Submitted next-jobs past target) · 📋 Upcoming to place. From `/api/scheduled_sos` (see [[project_scheduled_sos_shadowed_in_dashboard]]) + frontend skipped-detection.
- Long-term (NOT now per DJ): retire the old `calendar.html`.
