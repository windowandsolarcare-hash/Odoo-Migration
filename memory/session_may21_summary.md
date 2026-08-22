---
name: session_may21_summary
description: "2026-05-21: Render Claude rebuild (generic tools + schema prompt), nav button, theme-aware card, 529 retry"
metadata: 
  node_type: memory
  type: project
  originSessionId: 3b84512f-52f2-41f6-b8e7-d6c6919c44ee
---

## Changes shipped 2026-05-21

**Render Claude rebuild (field.py) — biggest change:**
- Removed 8 narrow read tools: `search_customers`, `get_customer_profile`, `get_job_details`, `get_schedule`, `get_next_job`, `get_sales`, `get_sales_week`, `get_jobs_list`
- Added 2 generic tools: `workiz_get` (fetch any job by UUID), `workiz_update` (update any Workiz job fields)
- Replaced SYSTEM_PROMPT with schema-based prompt: full Odoo data model (exact field names), key relationship rules (SOs on Property children), workflow patterns, Workiz facts
- Model now figures out any query itself via `odoo_query` — no dedicated tool per question needed
- READ_TOOL_MAP, WRITE_TOOLS, execute_write_tool, _describe_write were already updated in prior session steps 1-5; this session did steps 6-8

**Navigate-to → big Maps button (field.html):**
- `addVmHistory` detects `maps.google.com` URL in response, renders `.nav-btn` (large blue button) instead of small link
- Type set to `'nav'` (neutral container, no green overlay)
- CSS: `.vmh-answer.nav { background:transparent }`, `.nav-btn { display:block; background:#0284c7 }`

**Voice response text fix (field.html):**
- `.vmh-answer.ok` was `color: #86efac` (bright green) on dark green bg — unreadable in day mode
- Changed to `background: var(--bg-input); color: var(--text)` — readable in both themes
- Green left border still indicates success

**Field Assistant card follows day/night theme (index.html):**
- Added `--pc-bg-from` / `--pc-bg-to` CSS variables
- Dark: `#1e3a5f → #1e293b` (existing navy gradient)
- Light: `#e0f2fe → #f1f5f9` (soft sky blue)
- Toggle button drives it instantly

**529 retry in field.py:**
- Wraps `client.messages.create()` with `for _retry in range(3)` + `except anthropic.APIStatusError` where `status_code==529`
- Sleeps `2**_retry` seconds (1s, 2s) before retry
- Added `time` to imports
