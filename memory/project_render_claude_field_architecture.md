---
name: project_render_claude_field_architecture
description: "Render Claude field.py tool architecture: 2 generic tools + odoo_query + schema-based prompt. READ before adding any field assistant tools."
metadata: 
  node_type: memory
  type: project
  originSessionId: 3b84512f-52f2-41f6-b8e7-d6c6919c44ee
---

## Architecture (as of 2026-05-21)

**File:** `routers/owner/field.py` in `windowandsolarcare-hash/saunders-render-app`

### Tool philosophy
Generic over specific. The model reasons from a schema prompt and calls `odoo_query` for any data lookup — no dedicated tool per question. Only add a new tool when the action can't be expressed as an odoo_query/odoo_write call.

### READ_TOOL_MAP (read-only tools)
| Tool | What it does |
|---|---|
| `odoo_query` | Any Odoo read — model, method, args, kwargs |
| `workiz_get` | Fetch Workiz job by UUID → full job dict |
| `navigate_to` | Returns Google Maps URL (rendered as big blue button in UI) |
| `send_email` | Send email via Odoo mail.mail |
| `save_memory` / `delete_memory` | Odoo ir.config_parameter key-value store |
| `github_read_file` / `github_list_dir` | Read files from GitHub repo |
| `refresh_shared_memory` | Reload SHARED_MEMORY.md from GitHub |
| `check_unpaid_jobs` | Check for uninvoiced Done SOs |
| `find_next_opening` | Suggest scheduling openings |

### WRITE_TOOLS (require confirmation or immediate mode)
`odoo_write`, `record_check_payment`, `schedule_job`, `create_todo`, `duplicate_workiz_job`, `start_task_timer`, `stop_task_timer`, `sync_so_verify`, `process_payment_with_sync`, `workiz_update`, `github_push_file`

### SYSTEM_PROMPT structure
1. Who you are + voice-first context
2. Primary tools (odoo_query, odoo_write, workiz_get, workiz_update)
3. ODOO DATA MODEL — exact field names for sale.order + res.partner
4. KEY RELATIONSHIP RULE: SOs on Property child partners, not Contact directly
5. Workiz facts (SubStatus rules, defaults, quirks)
6. Odoo rules (date_order, chatter format, etc.)
7. Workflow patterns (schedule, field session, payment, reactivation query, etc.)

### Why: background
Prior to 2026-05-21, 8 narrow tools (search_customers, get_job_details, etc.) required Claude to use the right specific tool per question. The schema-based approach lets it compose any query from first principles, which handles edge cases the narrow tools couldn't. Twilio/phone-agent use case was the trigger — narrow tools are too brittle for open-ended AI conversations.

### 529 retry
`_agent_loop` wraps `client.messages.create()` with 3-attempt retry on `anthropic.APIStatusError` status 529. Backoff: 1s, 2s.
