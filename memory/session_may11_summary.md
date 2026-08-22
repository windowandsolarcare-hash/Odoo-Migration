---
name: Session May 11 Summary
description: 2026-05-11 session — ql_panel.js UI fixes (CF tags, customer tab, voice autocomplete, sticky headers), dashboard.py scheduling UUID fix, 45-day lookahead, get_customer_jobs tool, reactivation scheduling flow (tabled)
type: project
originSessionId: 38d7e751-242a-410e-8fc3-0b58bb4701dd
---
## Render App — ql_panel.js (commit 914b07f1, 31,622 bytes)

### CF Tag Fix
- SO `partner_id` may point to a property child record whose PARENT holds the partner category (e.g. "CF")
- Fix: `_get_jobs_for_date` fetches `parent_id` alongside `category_id`; looks up parent partner categories and merges them into the child's set
- **Why:** Barbara Scott's CF tag wasn't showing because the category was on the main contact, not the property

### Customer Tab — Mobile Fix
- `#office-panel` is CSS `display:none` on mobile (width < 600px) — the customers pane lives inside it
- Fix: 👤 button forces `#office-panel` to `position:fixed; inset:0` as a fullscreen overlay with "✕ Done" dismiss button
- From other pages: sets `localStorage.setItem('ql_open_tab','customers')` before navigating to field.html; polling block on field.html load auto-opens customers pane

### Voice Modal Autocomplete (`#vm-ac-panel`)
- When a command template has `____` and `field:'customer'` or `field:'city'`, selecting it slides up an autocomplete panel
- Customer search: fetches `/owner/api/search` (350ms debounce)
- City search: filters static `CITIES` array
- Selecting a result replaces `____` in the textarea
- Panel positioned at `top:132px; left:0; right:0; bottom:0` inside `.vm-sheet`
- iOS autofill bar suppressed: `type="search"` + `autocapitalize="off"`
- 18 commands have `field:'customer'`, 1 has `field:'city'`

### Sticky Headers
- Added to 6 pages via CSS: `.ac-header,.rc-header,.hdr,.tc-header,.qheader,.hub-header{position:sticky!important;top:0!important;z-index:200!important;}`

## Render App — dashboard.py (commit 8f0959cd, 536,983 bytes)

### get_customer_jobs Tool (NEW)
- Fast customer job lookup: fuzzy name match → walks property children → returns all SOs with ✅/📌 flags
- Added to READ_TOOL_MAP and TOOLS list (before find_next_opening)
- Replaces multi-step AI reasoning that was very slow

### find_next_opening — UUID Fix
- `_find_scheduling_openings` now queries for any open/Submitted SO for the customer
- Includes in response: `Existing open job: S00123 (Submitted) — source_uuid='ABCD1234' ← pass this to schedule_job`
- Claude can now pass the correct UUID directly — was previously passing wrong value
- **Why:** `find_next_opening` never returned UUIDs before; Claude was guessing wrong value for `source_uuid`

### _create_new() — Submitted Job Fallback
- Previously failed with "No Done jobs found" when customer only had Submitted jobs
- Now falls back: if no Done SOs, looks for any open/Submitted SO with a UUID as the source
- Prevents "No Done jobs found" error for new/reactivation customers

### Scheduling Lookahead
- `LOOKAHEAD_DAYS` extended from 14 → 45 days in `_find_scheduling_openings`

### System Prompt Additions
- CARRY CUSTOMER CONTEXT ACROSS TURNS rule: once a customer is named, carry them through follow-up questions
- SUBMITTED / GRAVEYARD JOB CASE rule: treat Submitted Sunday jobs as reschedulable, not blockers

## Reactivation Scheduling Flow — TABLED

**Scenario (Bruce Johnson):** Reactivation SMS fired → created a Submitted Workiz job → Bruce texted in directly instead of using Calendly → DJ scheduled manually. Odoo showed only 2 SOs (missing the reactivation-created Submitted job). Concern: overnight sync may not pick up reactivation jobs.

**Two tasks created:**
1. CHECK: Bruce Johnson — does Odoo show 3 SOs after overnight sync? (Task #1)
2. FUTURE: 2-open-job detection and reactivation path routing (Task #2)

**Planned logic (not built):**
- 2 open SOs → Claude asks DJ: reactivation call-in or other open job?
- 1 open SO from reactivation lead → auto-route: schedule + close CRM lead (mark won + clear graveyard UUID)
- 1 open SO, no reactivation → normal path

**Note:** `_update_uuid` already clears `x_workiz_graveyard_uuid` and `x_workiz_graveyard_link` on the lead. What's missing: marking lead as won + the clarifying question logic.
