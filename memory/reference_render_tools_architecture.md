---
name: Render Claude tools architecture
description: Where tools live, how they're structured, and how to add new ones
type: reference
originSessionId: 96c7eadf-7840-4091-9290-6d3aed1806c8
---
## File Location
`C:\Users\dj\Documents\Business\Saunders Render App\routers\owner\dashboard.py`

## Tool Definition Structure

### 1. TOOLS list (line ~1962)
Array of tool definitions. Each entry:
```python
{
    "name": "tool_name",
    "description": "What the tool does",
    "input_schema": {
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "..."},
            "param2": {"type": "integer"}
        },
        "required": ["param1"]
    }
}
```

### 2. WRITE_TOOLS set (line ~2496)
Set of tool names that require confirmation before execution:
```python
WRITE_TOOLS = {
    'tool_name_1', 'tool_name_2',
    ...
}
```

### 3. Tool handlers (line ~977+)
Series of `if tool_name ==` blocks that implement the tool logic:
```python
if tool_name == 'my_tool':
    param1 = args.get('param1')
    # do work
    return "Result message"
```

### 4. _describe_write function (line ~1895+)
Provides human-readable descriptions of what the tool will do (shown in confirmation):
```python
if tool_name == 'my_tool':
    return f"[SYSTEM] Do something\n  Details: {args.get('param1')}"
```

### 5. Tool dispatch (line ~2637+)
Checks tool name against handlers and executes.

## Adding a New Render Claude Tool — 5 Steps

1. **Add to TOOLS list** — name, description, input_schema
2. **Add to WRITE_TOOLS** (if it modifies data)
3. **Add handler** — `if tool_name == 'name':` block with logic
4. **Add description** — `if tool_name == 'name':` in _describe_write
5. **Push to GitHub main** — Render Claude loads tools on session start

## Natural Language Resolution Pattern

For tools that accept identifiers, use `_find_so_by_identifier()` helper (line ~5063):
- Tries numeric SO ID first
- Then SO name ("SO-2024-001")
- Then Workiz UUID
- **Finally: searches by customer name** and finds their most recent open invoiceable SO

This lets users say natural language like "sync Fred Jones open job" and the tool resolves everything automatically.

## Current Tools (as of 2026-05-01)

**Read-only (no confirmation):**
- search_customers, get_customer_profile, get_job_details, get_schedule, get_next_job, get_sales, get_sales_week, get_jobs_list, navigate_to, send_email, save_memory, delete_memory, odoo_query, github_read_file, github_list_dir, start_task_timer, stop_task_timer, refresh_shared_memory

**Write tools (confirmation required):**
- update_workiz_field, update_odoo_contact, post_odoo_note, create_todo, mark_job_done, create_workiz_job, duplicate_workiz_job, record_check_payment, create_purchase_order, send_purchase_order, convert_quote_to_job, push_quote_to_workiz, add_link_to_todo, delete_workiz_job, odoo_write, github_push_file, update_shared_memory
- **NEW (2026-05-01):** sync_so_verify, process_payment_with_sync
