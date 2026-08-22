---
name: Render Claude write tools — what each one does + invocation rules
description: Catalog of all WRITE_TOOLS available to Render Claude in Saunders Render App. Each is in the WRITE_TOOLS set in dashboard.py and triggers a confirmation preview before execution. Use this when adding new tools or debugging which tool fires on a voice command.
type: reference
originSessionId: 96c7eadf-7840-4091-9290-6d3aed1806c8
---
**READ when adding a new write tool, debugging tool routing, or onboarding to the Render Claude codebase.**

## Pattern: every write tool has 4 wiring points

In `Saunders Render App/routers/owner/dashboard.py`:

1. **Implementation** in `execute_write_tool(tool_name, args)` — the actual Odoo/Workiz writes
2. **Preview** in `describe_write_tool(tool_name, args)` — the confirmation text DJ sees
3. **Schema** in `TOOLS = [...]` list — Anthropic native format with description + input_schema
4. **Membership** in `WRITE_TOOLS` set — tells the runtime to require confirmation

If any of those are missing, the tool either won't show, won't preview, or won't execute.

## Current write tools (as of 2026-04-30)

### Workiz writes
- `update_workiz_field` — write any field on a Workiz job + sync to SO snapshot if applicable
- `create_workiz_job` — make a new Workiz job (Phase 3-style)
- `duplicate_workiz_job` — copy an existing job with a new date (preserves all fields including gate code, pricing, notes — auto-finds source UUID from partner_id if not given)
- `mark_job_done` — set Workiz status=Done
- `delete_workiz_job` — PERMANENTLY delete Workiz job + cancel/unlink Odoo SO + delete linked tasks (added 2026-04-30 night, commit c4c2e4ff). **Blocks if any invoice is linked** to the SO. Order: Odoo tasks → Odoo SO → Workiz delete (Workiz fires last so Odoo failures abort cleanly). Phase 4 does NOT auto-clean Workiz deletes — this is the only tool that handles it.

### Odoo customer writes
- `update_odoo_contact` — patch any field on res.partner
- `post_odoo_note` — chatter post on a record
- `create_todo` — creates **`project.task`** with `project_id=False` (Odoo "To-do" app pattern). **v2 (2026-04-30, commit 1645e679)**: dropped the `[Render] Follow-up:` title prefix, made `partner_id` optional (omit for personal todos), schema only requires `note` + `days`. Title is DJ's actual phrase; partner_id auto-anchors when DJ names a real customer. System prompt rule: "follow up with X" → always create_todo.
- `add_link_to_todo` — append a clickable URL to an existing to-do (added 2026-04-30 night, commit 97f8e7d5). Resolves todo by ilike search on summary/name, handles BOTH mail.activity (writes `note`) and project.task (writes `description`). Returns CLARIFY when multiple match. Voice phrases: "link the AWP po to the order screen to-do", "attach this URL to the [name] follow-up", "stick this on activity #70".

### Odoo task/timer writes
- `start_task_timer` — Render-owned timer; bypasses Odoo's flaky native timer
- `stop_task_timer` — closes the timer + creates the timesheet entry (with GPS reverse-geocode for actual address)

### Odoo invoice/payment writes
- `record_check_payment` — creates invoice + registers payment + posts chatter; Phase 6 syncs to Workiz. **v2 (2026-04-30, commit 0e6726af)**: `so_id` is now optional — when omitted, walks Contact↔Property partners and finds all open invoiceable SOs. Returns CLARIFY if >1, friendly error if 0. **Tip detection**: BLOCKS when `amount != SO total` unless `acknowledge_mismatch:true` (or `tip:true`) is passed. On success with mismatch, response includes a TIP REMINDER for DJ to add the tip to Workiz manually. Empty SO returns clean error instead of opaque Odoo trace.

### General Odoo
- `odoo_write` — generic escape hatch for any model/method (write, create, unlink, action_*, run, message_post)

### GitHub
- `github_push_file` — push file to main branch with commit message

### Memory
- `update_shared_memory` — update SHARED_MEMORY.md on GitHub

### Render Quote Tool support (NEW 2026-04-29 / 2026-04-30)
- `create_purchase_order` — vendor PO with natural-language vendor + product resolution
- `send_purchase_order` — emails PO using vendor's `x_default_po_template_id` (or default)
- `convert_quote_to_job` — clears QUOTE ONLY watermarks + sets job_type from quote-line product
- `push_quote_to_workiz` — accepts customer-approval phrasing ("customer approved", "they accepted", "X is a go"). Prepends [Render] block to Workiz JobNotes with line items + 4-step checklist for DJ to complete in Workiz.

## Read tools (no confirmation, in READ_TOOL_MAP)

- `search_customers` — by name → partner_id, Workiz IDs, active SO info
- `get_customer_profile` — full contact profile from res.partner
- `get_job_details` — SO + tasks + Workiz refs for a partner
- `get_schedule` — jobs for a date
- `get_next_job` — next confirmed job from now
- `get_sales` / `get_sales_week` / `get_jobs_list` — sales aggregates
- `navigate_to` — generates Google Maps link
- `send_email` — Gmail draft (NOT a confirmation-required write because no business state is touched)
- `save_memory` / `delete_memory` — local memory key/value
- `odoo_query` — generic Odoo read
- `github_read_file` / `github_list_dir` — read GitHub repo
- `refresh_shared_memory` — re-pull SHARED_MEMORY.md

## Vendor + product resolution helpers (in same file)

- `_resolve_vendor_by_query(query)` — searches `res.partner` with `supplier_rank>0` matching name OR `x_aliases`. Returns dict (single best match) or None.
- `_resolve_product_for_vendor(vendor_id, part_query)` — three-pass match: (1) exact `product.supplierinfo.product_code`, (2) exact `product.product.default_code`, (3) keyword token match on product name restricted to vendor's catalog. Returns dict (unique match), list (ambiguous → caller asks for clarification), or None.

These are the helpers that make `create_purchase_order` accept "5/16 almond" and resolve it to AWP-1017AL.

## Adding a new write tool — checklist

1. Implement in `execute_write_tool` — return a string status message starting with `[ODOO]`, `[WORKIZ]`, `[GITHUB]`, etc.
2. Add a preview block in `describe_write_tool` — multi-line summary of what'll happen
3. Add schema entry in `TOOLS` list — name, description (be generous, give voice trigger phrases), input_schema with required fields
4. Add tool name to `WRITE_TOOLS` set
5. Test with a voice command — verify preview shows correctly, confirm fires execution

## Voice phrase rules (from session 2026-04-30)

DJ rarely says SKUs or technical terms. Tool descriptions should include 4-6 example phrases DJ might use, like the `push_quote_to_workiz` tool's description has:
- "customer approved the quote"
- "they accepted"
- "Bud's a go"
- "go ahead with [customer]'s quote"

Generic phrasing tells Claude when to fire each tool, even when DJ uses casual language.

## Related memory

- `project_quote_tool.md` — customer Quote Tool architecture
- `project_awp_vendor_setup.md` — AWP vendor record + custom fields
- `project_todo_models_in_odoo.md` — why create_todo writes to project.task
- `feedback_proactive_inefficiency_capture.md` — preview-first pattern philosophy
