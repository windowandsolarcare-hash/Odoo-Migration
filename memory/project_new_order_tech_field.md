---
name: project_new_order_tech_field
description: "New Order (new_job.html) Tech field is intentionally dead while Workiz is live — tech is assigned in Workiz, not here. Don't re-require it."
metadata: 
  node_type: memory
  type: project
  originSessionId: 7956af31-4ad6-40dd-8ba9-78afecbbbbd2
---

# New Order "Tech" field is a no-op while Workiz is live (2026-07-01)

The New Order flow = `static/owner/new_order.html` (type picker) → `/owner/new-job` = `static/owner/new_job.html`, backend `routers/owner/new_job.py` `POST /api/intake/create-job`.

**Fact:** `create-job` RECEIVES `tech_name` but does NOT use it. It's only referenced in the commented-out "===== ODOO SO CREATION — DISABLED WHILE WORKIZ IS LIVE =====" block (`x_studio_x_studio_workiz_tech`). The Workiz job clone (SA 1338, `clone_ctx`/`clone_extra`) is never passed tech. Tech is assigned by DJ **in Workiz** after the job is created (backend comment line ~494: "DJ finalizes line items / tech / status in Workiz").

**Bug fixed:** the frontend hard-blocked submit with `if (!tech) { showToast('Select a tech'); return; }`. If the employees list didn't load, the dropdown had no options → DJ literally couldn't proceed ("it asks to choose tech, it shouldn't"). Removed the requirement and hid the Tech `field-group` (`display:none`), keeping the markup.

**Why:** while Workiz is the system of record, New Order only creates the Workiz job (Phase 3/Zapier then builds the Odoo SO). Tech isn't part of that path.

**How to apply:** do NOT re-add a required-tech check to New Order while Workiz is live. When Workiz is RETIRED, un-hide the Tech field, restore the requirement, and uncomment the Odoo SO-creation block in new_job.py (which writes the tech). Same "after Workiz retires" trigger as [[project_calendar_job_move_postworkiz]] / [[project_job_end_time]].

## Line items — same "Odoo only after Workiz leaves" story (DJ, 2026-07-02)
DJ: "can't send line items to workiz. keep it for odoo only once workiz leaves." Correct — **Workiz has no API to add real line items.** New Job currently (a) drops them into the Workiz job as a `LINE ITEMS TO ADD:` note via SA 1338 `clone_line_items`, and (b) `njCopyItems()` cycles each price+name through the clipboard so DJ pastes them into Workiz → Items by hand. The hand-entered items do NOT reach Odoo today (the SO is built later by Phase 3/Zapier from the Workiz webhook, without them).

The SAME commented "ODOO SO CREATION — DISABLED WHILE WORKIZ IS LIVE" block in new_job.py already creates `sale.order.line` from the posted `lines`, so at cutover the entered line items flow straight to the Odoo SO. **Decision (DJ deferred / "no preference"): leave as-is until cutover — no interim capture-to-Odoo store** (Workiz is leaving imminently; not worth the complexity). Keep the SERVICES editor (`S.lines` / "+ Add Service") — it's the future Odoo source. So the cutover flip = un-hide tech + restore tech requirement + uncomment the SO block (which writes BOTH tech AND the line items). Don't try to make line items post to Workiz — it can't.
