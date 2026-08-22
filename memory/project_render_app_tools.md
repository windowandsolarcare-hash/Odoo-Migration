---
name: Render app GPT tools — current list
description: 20 tools available to GPT in the Render field assistant app as of 2026-04-12
type: project
originSessionId: b189e64a-a6d4-46d1-a70f-a6b34dca7361
---
Current tools in app.py (20 total):

Read tools: search_customers, get_customer_profile, get_job_details, get_schedule, get_next_job, get_sales, get_sales_week, get_jobs_list, navigate_to

Write tools (require confirmation): update_workiz_field, update_odoo_contact, post_odoo_note, create_todo, mark_job_done, create_workiz_job, duplicate_workiz_job, start_task_timer, stop_task_timer

Utility: send_email, save_memory, delete_memory

**Key rules built into tool descriptions:**
- get_sales_week = Mon-Sat only (no Sunday), use for weekly revenue queries
- get_jobs_list = Workiz browse only, NEVER for revenue (pulls by creation date not job date)
- duplicate_workiz_job = copies all fields from most recent job, schedules on new date
- All Render-created tasks/notes tagged with [Render] breadcrumb

**How to apply:** When adding new tools, follow the pattern: Python function + TOOLS list definition + WRITE_TOOLS set (if write) + READ_TOOL_MAP or execute_write_tool handler + _describe_write entry (if write).
