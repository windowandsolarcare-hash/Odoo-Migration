---
name: Render App — April 18 2026 State
description: Current state of app.py and index.html as of 2026-04-18 — all features, tools, recent changes
type: project
originSessionId: af1a8616-ff12-43ea-9d82-c48e3900955e
---
# Render App Current State — 2026-04-18

---

## RECENT CHANGES (this session)

### app.py
- `api_upcoming`: now fetches `project.task` records for upcoming SOs → adds `task_names` list to each job → enables Solar/Window service type on future day rows
- `api_upcoming`: extended from 10 → 14 calendar days (guarantees 10 work days Mon-Fri)
- `_render_timer_stop`: log description now includes PT start + end times: `[Render Timer] 1234 Main St | 8:15 AM – 10:32 AM`
- `POST /api/attachment`: new endpoint — accepts base64 image, creates ir.attachment on SO in Odoo. Params: access_code, so_id, filename, content_type, data
- `tool_github_list_dir`: new tool for Render Claude — lists files/dirs in GitHub repo. Empty path = root. Returns dirs as [folder/] and files with sizes.

### index.html
- Future day rows now use `job-name-wrap` div (fixes dollar amount right-justification)
- Solar/Window service type subtitle now shows on future day rows (from task_names)
- `.job-svc` font size: 11px → 13px
- Saved request library: localStorage `wsc_saved_qs`, max 15 recent + unlimited starred. Tap to reuse, ☆ to pin. Shows below Send button in Command tab.
- Timer stop: GPS timeout 5s → 2s. `_timerStopping` guard prevents double-tap. Button disables immediately on tap.
- Photo section: above payment section, gallery picker (not camera-only), multiple files, uploads to Odoo as ir.attachment, thumbnail previews
- Mic button: moved into header between date block and sun/theme button. No longer fixed/floating overlay.
- Tab renamed: "7-Day" → "10-Day"
- Time label on done jobs: shows `2.5h` or `45m` LEFT of `$190/hr` — quick visual check if timer logged correctly
- `_timerStopping` guard + button disable on stop

---

## CLAUDE TOOLS IN app.py (full list as of 2026-04-18)

**Read tools:**
- search_customers, get_customer_profile, get_job_details, get_schedule, get_next_job
- get_sales, get_sales_week (Mon-Sat), get_sales_month (Mon-Fri only, returns days dict)
- get_jobs_list, navigate_to
- odoo_query, github_read_file, github_list_dir (NEW), refresh_shared_memory

**Write tools (require confirmation):**
- update_workiz_field, update_odoo_contact, post_odoo_note, create_todo
- mark_job_done, create_workiz_job, duplicate_workiz_job
- start_task_timer, stop_task_timer, record_check_payment
- odoo_write, github_push_file, update_shared_memory

**Utility:**
- save_memory, delete_memory

**Direct API endpoints (not Claude tools):**
- POST /api/timer/start — starts Render timer
- POST /api/timer/stop — stops Render timer, creates timesheet, reverse-geocodes GPS
- POST /api/payment — records payment, creates invoice, posts chatter
- POST /api/attachment — NEW: uploads photo to Odoo SO as ir.attachment
- GET /api/upcoming — schedule lookahead (14 calendar days)
- GET /api/dashboard — today's schedule + stats

---

## KEY BEHAVIOR RULES (system prompt)

- MONTHLY JOB LISTS: always use Odoo SOs, never Workiz API with only_open
- Timer: always use task_id from session context for stop, never re-search
- Payment: customer known from session, use partner_id + so_id directly
- get_sales_week = Mon-Sat (no Sunday)
- All Render-created tasks/notes tagged [Render]

---

## TIMER SYSTEM

- Start: stores UTC start in ir.config_parameter key `render.timer.{task_id}`
- Stop: reads param, calculates elapsed, creates account.analytic.line, clears param
- Description format: `[Render Timer] 1234 Main St, Palm Desert CA | 8:15 AM – 10:32 AM`
- Voice stop (no GPS): `[Render Timer] | 8:15 AM – 10:32 AM`
- Moves task to In Progress (stage 18) on start
- Clears Odoo's own timer_start to prevent conflicts

---

## UPCOMING / SCHEDULE DISPLAY

- Left panel (mobile closed): shows today's jobs + future work days with jobs
- Future days: job-name-wrap, Solar/Window subtitle, right-justified amounts, WZ+SO pills
- 10-Day tab (desktop right panel): full 14-calendar-day lookahead, all work days with jobs
- Saved requests: localStorage, pin/star favorites, tap to reuse

---

## PHOTO ATTACHMENT

- Photo section appears above payment section when job is opened
- Gallery picker (not camera-forced), multiple files allowed
- Upload immediately on selection → Odoo ir.attachment on SO
- Thumbnail preview with ✕ to remove
- Clears when new job selected
