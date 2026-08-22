---
name: project_blower_banner_gutter
description: "Command Center \"bring the blower\" banner — pops when TODAY has a gutter job (by job type OR gutter line item). Dismissable per-so_id."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-08-18T15:57:42.275Z
---

**Built 2026-08-18 (DJ):** DJ keeps forgetting his blower on gutter jobs. Now the **Command Center (v2_command.html)** shows a bright dismissable banner — "🪣 GUTTER JOB TODAY — BRING THE BLOWER!" with the customer name(s)+time — whenever **today's** schedule has a gutter job. He taps "✓ Got it" to clear it once the blower's packed; a NEWLY scheduled gutter job (new so_id) makes it reappear.

**Gutter detection (backend, `dashboard.api_calendar_jobs`):** added a per-job `gutter` boolean = job_type contains 'gutter' (e.g. 'Gutter - Inspect and Clean') **OR** any line item name matches (batch `sale.order.line search_read [order_id in <range SOs>, name ilike 'gutter']` → set of gutter SO ids). The line-item path matters because a **Combination-of-Services** job can have a gutter line without the gutter job type. Verified vs live: 50 gutter-type SOs + line items like "Clean Gutters / Inspect and Clean Gutters". Commit dashboard 9cb158e.

**Frontend (v2_command.html, commit 0d2378f):** `#blowerBanner` div at top of `<main class="body">` (bright #fff3cd/#f0c000 so it pops on light AND dark themes). `loadTodayBar()` already loads TODAY's jobs via `calendar_jobs?start=today&end=today` → passes `tjobs` to `checkBlowerBanner()`. Banner shows the today-gutter jobs whose so_id is NOT in `localStorage['wsc_blower_cleared']` (JSON array, capped 200). `clearBlower()` adds the shown so_ids to that set + hides. Scope = TODAY only ("catches my attention when I leave"). This is the dismissable-banner pattern DJ referenced ("a banner I have to clear"). See [[project_postpone_needs_scheduling]] (same command-center file).
