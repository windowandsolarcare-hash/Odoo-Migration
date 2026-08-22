---
name: project_edit_select_empty_first_option
description: "Job-detail edit dropdowns showed the FIRST option when the value was empty — unset Frequency read \"3 Months\", unset Type of Service read \"Maintenance\". Fixed with a blank \"— not set —\" option."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0e6fb90e-8d05-4272-91a3-ed7ee21488d7
  modified: 2026-08-10T23:13:25.418Z
---

**Symptom (DJ, 2026-08-10):** "When I duplicate a job it seems to default to Maintenance and 3 Months, when I know they're not a maintenance customer."

**Root cause (NOT the duplicate endpoint):** `/api/duplicate_job` (dashboard.py 7373) copies `x_studio_x_studio_type_of_service_so` + `x_studio_x_studio_frequency_so` from the source ONLY if present, and sets no defaults — correct. The misleading "Maintenance / 3 Months" came from the **job-detail edit dropdown renderer in v2_field.html** (~L2071, the `r.type==='select'` branch). It only prepended a custom option when the value was non-empty-and-unknown; when the value was **empty**, it prepended nothing, so the browser showed `options[0]` as selected. `_EDIT_SELECT` (brain.py) options start with `'3 Months'` (Frequency) and `'Maintenance'` (Type of Service) → an unset field READ as those. A non-maintenance duplicate (empty type/freq) therefore displayed Maintenance + 3 Months, and saving would have written them.

**Fix (commit 85cbf78):** when `!r.value`, prepend `<option value="" selected>— not set —</option>`. Empty now shows blank (no write, since data-orig stays ""); picking a real option writes normally. Surgical — 3 lines, only the empty-value path.

**General rule:** any HTML `<select>` bound to an optional field must carry an explicit empty/placeholder option, or an unset value silently masquerades as `options[0]`. Same smell could exist in the dup modal `dup-type` (v2_customers.html L730) — job_type falls to DUP_TYPES[0] when the source job_type is blank (not fixed yet; lesser issue since it's only the free job_type field, not freq/type_of_service).
