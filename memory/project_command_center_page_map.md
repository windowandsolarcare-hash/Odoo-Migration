---
name: project_command_center_page_map
description: "★ DJ's daily schedule = schedule_hub.html (/owner/command-center \"Command Center\"). Tapping a job opens field.html (/owner/field?open_so). NOT v2_schedule.html (dead preview)."
metadata: 
  node_type: memory
  type: project
  originSessionId: 4d5f391d-cfd7-405f-80b1-9446eb93cb87
  modified: 2026-07-23T00:39:38.799Z
---

★ **Verified 2026-07-22 from DJ's own screenshot.** Which page is which — do NOT guess, this cost a whole session of edits to the wrong files:

- **DAILY SCHEDULE = `static/owner/schedule_hub.html`, route `/owner/command-center`.** This is what DJ calls "the Command Center" and uses every day. Blue gradient "📅 Command Center" header, buttons New Order / Add to schedule / Next available by city / Investigate, pills **On the schedule / Calendar / Needs scheduling**, Window/Solar/Combo legend, Past Jobs accordion, collapsible day sections. Confirm by grepping the file for "Command Center" + "Needs scheduling" + "Investigate".
- **JOB DETAIL = `static/owner/field.html`, route `/owner/field`.** Command Center's `onScheduleTap(r)` (schedule_hub.html ~line 379) does `location.href='/owner/field?open_so='+entity_id+'&from=cc'`. So "Kristen **in detail**" = field.html opened via `?open_so`. field.html is NOT dead — it IS the detail page. My field.html surgical repaint fix (commit 5e790718) for the 3x-flash/scroll-jump WAS on the right page.
- **DEAD/PREVIEW — do NOT edit for daily use:** `v2_schedule.html`, `v2_field.html`, `v2_home.html`, etc. (the `/static/owner/v2_*.html` redesign previews) are NOT what DJ uses. I wrongly deployed gate/flash fixes to v2_schedule.html + v2_field.html first — harmless but useless. `index_classic.html`, `quick.html` also legacy.

**Card rendering on the Command Center:** cards are painted by `WSCKit.renderResult(container, rows, {onRow:onScheduleTap})` from `static/owner/report_kit.js`. Each row = `{title,subtitle,meta,extra,amount,badges:[{label,tone}]}`. **`extra` is `esc()`-escaped plain text — cannot inject colored HTML there.** For a colored label use a **badge**: tones map to `.wsc-badge.<tone>` in common.css → `ok/warn/danger/info/muted/accent` (danger=red). Row builders live in schedule_hub.html (~line 345 the calendar/day builder, ~line 463 the on-schedule day builder).

**Gate code (2026-07-22, commit 31b2d5cb):** job rows carry `j.gate` (from `/api/calendar_jobs` → SO `x_studio_x_gate_snapshot` → property `x_studio_x_gate_code` → ''). Added a **red `NO GATE CODE` danger badge** when `!j.gate && !isPersonal(j)` to BOTH row builders. Gate value itself still shows via `extra` (`🔑 <code>`).

**How to apply:** ANY schedule-card feature → `schedule_hub.html` (+ maybe report_kit.js for shared card structure). ANY job-detail feature → `field.html`. If a request says "the schedule"/"the card"/"command center", it means these two files — verify against a screenshot, do NOT assume field.html's own schedule tab or the v2 previews. Related: [[project_field_refresh_rerenders_open_job]], [[project_owner_page_nostore_stale]], [[project_render_app_redesign]].
