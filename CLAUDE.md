# Claude Code - Project Instructions
**Last Updated:** 2026-04-11
**Migration:** Cursor → Claude Code (permanent)

---

## START HERE

**This file is the single source of truth for new sessions.** CLAUDE_CONTEXT.md and MASTER_PROJECT_CONTEXT.md are deep-reference only — do NOT require reading at session start. Everything critical is in this file.

---

## QUICK REFERENCE

**Project:** Workiz ↔ Odoo sync for Window & Solar Care
**Owner:** DJ Sanders
**Repo:** windowandsolarcare-hash/Odoo-Migration (main only)
**Deploy:** `gh api` to push files - NO git commands

---

## CREDENTIALS

- **Odoo URL:** `https://window-solar-care.odoo.com`
- **Odoo DB:** `window-solar-care`
- **Odoo User ID:** `2`
- **Odoo API Key:** `7e92006fd5c71e4fab97261d834f2e6004b61dc6`
- **Workiz API Token:** `api_1hu6lroiy5zxomcpptuwsg8heju97iwg`
- **Workiz Auth Secret:** `sec_334084295850678330105471548`
- **GitHub Repo:** `windowandsolarcare-hash/Odoo-Migration` (branch: `main`)

---

## CRITICAL RULES

1. **Zapier:** Code in GitHub. Zapier fetches on every run. Push to main = deploy.
2. **Odoo Server Actions — TWO-STEP DEPLOY:** When fixing a bug in a reactivation script or any Odoo server action, you MUST do BOTH steps: (a) update the local file and push to GitHub, AND (b) write the fixed code directly into the Odoo server action via `ir.actions.server` write API. GitHub is the source of truth for version history, but Odoo runs the code stored in its own database — pushing to GitHub alone does NOT update what Odoo executes. Always patch the live server action immediately after updating the file. Key server action IDs: LAUNCH=563, PREVIEW=559 (DNU). Find others by searching `ir.actions.server` where name ilike the script name.
3. **Odoo Server Actions — code restrictions:** NO imports, NO docstrings, NO env.user.message_post in webhooks, NO hasattr, NO response/result variable names
3. **Odoo Webhook payload:** Often already dict - check `isinstance(payload, str)` before json.loads
4. **Workiz STOP:** Filter on SubStatus (not Status). Status stays "Pending"
5. **Property search:** Use `x_studio_x_studio_record_category` = "Property", NOT type="other"
6. **Testing:** YOU create/cleanup test data via API. User never does manually
7. **Workiz custom field:** Use `type_of_service_2` NOT `type_of_service` — API returns/accepts `type_of_service_2`. Using the wrong name causes Phase 5 to create activities instead of jobs.
8. **Odoo action_confirm resets date_order:** After calling action_confirm() on an SO, always write date_order back. Odoo resets it to datetime.now() internally.
9. **date_order = job START time always.** SO `date_order` is always the Workiz `JobDateTime` (start time) converted to UTC. NEVER use `JobEndDateTime`, `date_deadline`, or any end time for `date_order`. This has been the rule since day one — the schedule, the Render app, and all reporting depend on it.
10. **NEVER comment out or remove existing working code without DJ's explicit approval.** This code was built over months, debugged, and agreed to work. Adding new code is fine. But commenting out, deleting, or disabling any existing logic — even temporarily, even with good intentions — requires DJ to say "yes, remove that." If you believe something should be removed, explain why and ask first. Do not act unilaterally.

---

## ODOO CUSTOM FIELD NAMES (EXACT — CASE SENSITIVE)

| Human Name | Model | Field Name | Notes |
|---|---|---|---|
| Workiz UUID | sale.order | `x_studio_x_studio_workiz_uuid` | Unique key for job lookup |
| Workiz Link | sale.order | `x_studio_x_workiz_link` | |
| Workiz Link | account.move (Invoice) | `x_studio_workiz_job_link` | Different from SO field |
| Workiz Tech | sale.order | `x_studio_x_studio_workiz_tech` | |
| Gate Code | sale.order | `x_studio_x_gate_snapshot` | Snapshot at time of job |
| Gate Code | res.partner | `x_studio_x_gate_code` | Master record |
| Pricing | sale.order | `x_studio_x_studio_pricing_snapshot` | Snapshot |
| Pricing | res.partner | `x_studio_x_pricing` | Master record |
| Job Type | sale.order | `x_studio_x_studio_x_studio_job_type` | |
| Frequency | res.partner | `x_studio_x_frequency` | e.g. "3 Months" |
| Type of Service | res.partner | `x_studio_x_type_of_service` | Written from Workiz type_of_service_2 |
| Alternating | res.partner | `x_studio_x_alternating` | "Yes" or "No" |
| Service Area | res.partner | `x_studio_x_studio_service_area` | |
| Workiz Client ID | res.partner | `ref` | Stores "1234" (ClientId numeric) |
| Location ID | res.partner | `x_studio_x_studio_location_id` | Workiz serialId / ClientId |
| Record Category | res.partner | `x_studio_x_studio_record_category` | "Property" for property records |
| Last Property Visit | res.partner | `x_studio_x_studio_last_property_visit` | Date of last visit to this property |
| Last Visit All | res.partner | `x_studio_last_visit_all_properties` | Last visit across all properties |
| Active/Lead | res.partner | `x_studio_activelead` | "Do Not Contact" (exact case) |
| SMS Override | sale.order | `x_studio_manual_sms_override` | Reactivation SMS text |
| CRM Activity Log | res.partner | `x_crm_activity_log_ids` | Activity log entries |
| Prices Per Service | res.partner | `x_studio_prices_per_service` | Pricing menu |
| Last Reactivation | res.partner | `x_studio_last_reactivation_sent` | 90-day cooldown |
| Graveyard UUID | crm.lead | `x_workiz_graveyard_uuid` | |
| Graveyard Link | crm.lead | `x_workiz_graveyard_link` | |
| Historical UUID | crm.lead | `x_historical_workiz_uuid` | |
| Historical Link | crm.lead | `x_studio_x_historical_workiz_link` | |
| Odoo Contact ID | crm.lead | `x_odoo_contact_id` | Linked res.partner ID |

---

## WORKIZ API ACCESS — HOW TO CALL FROM SCRIPTS

**Workiz blocks direct API calls from local machines (403 Forbidden).** The API is IP-restricted to the Render server and Odoo server only.

**To call Workiz from a local Python script or one-off tool, proxy through Odoo:**
1. Create a temporary `ir.actions.server` with the Workiz fetch code
2. Run it via JSON-RPC (Odoo's server can reach Workiz)
3. Use `raise UserError(result_string)` to return data back — captured in `resp['error']['data']['message']`
4. Delete the temp action immediately after

```python
action_id = rpc('ir.actions.server','create',[{'name':'TEMP','model_id':670,'state':'code','code': your_code}])
resp = rpc_raw({'jsonrpc':'2.0','method':'call','id':1,'params':{'service':'object','method':'execute_kw',
    'args':[ODOO_DB,ODOO_USER_ID,ODOO_API_KEY,'ir.actions.server','run',[[action_id]],
            {'context':{'active_id': any_so_id,'active_ids':[any_so_id],'active_model':'sale.order'}}]}})
rpc('ir.actions.server','unlink',[[action_id]])
msg = resp['error']['data']['message']  # your UserError string
```

**Workiz API URL format** (auth_secret required — without it you get 403):
```
https://api.workiz.com/api/v1/{TOKEN}/job/get/{UUID}/?auth_secret={AUTH_SECRET}
https://api.workiz.com/api/v1/{TOKEN}/job/update/{UUID}/
https://api.workiz.com/api/v1/{TOKEN}/job/delete/{UUID}/
```
- Token: `api_1hu6lroiy5zxomcpptuwsg8heju97iwg`
- Auth Secret: `sec_334084295850678330105471548`
- In Odoo server actions: use `requests.get(url)` — `requests` is available in Odoo eval context
- **Rate limit:** ~30 calls before hitting HTTP 429 — sleep 15-30 seconds between batches

**From Render (app.py) and Odoo server actions:** direct calls work fine — no proxy needed.

---

## WORKIZ API CRITICAL DEFAULTS

These defaults prevent Workiz API validation errors. Always use when field might be empty:

```python
'type_of_service_2': str(value or 'On Request')     # NOT type_of_service, NOT empty string
'frequency':         str(value or 'Unknown')          # NOT empty string
'confirmation_method': str(value or 'Cell Phone')    # NOT empty string
'JobSource':         str(value or 'Referral')         # NOT "Reactivation"
'ok_to_text':        str(value or 'Yes')
```

**Workiz Status vs SubStatus — FUNDAMENTAL:**
Workiz has only 5 Status values: Submitted, Pending, In Progress, Canceled, Done.
ALL other statuses (Scheduled, STOP, Lead, etc.) are SubStatus with Status = "Pending".
ALWAYS filter on SubStatus, not Status.

**Workiz API quirks:**
- ClientId: use numeric (e.g. 1040) not "CL-xxx"
- JobDateTime: omit entirely for unscheduled jobs
- All string fields: must be str() — reject None/numbers
- Job create response: returns list `[{UUID: '...'}]` or HTTP 204
- Job GET response: `{"data": [{...job...}]}` — job is inside a list. Always parse: `data = raw['data']; job = data[0] if isinstance(data, list) else data`
- Job GET on deleted job: returns **HTTP 204** (no content), NOT 404. Treat both 204 and 404 as "job is gone"
- type_of_service_2 is the custom field name (NOT type_of_service)

---

## APPROACHES THAT FAILED (DO NOT REPEAT)

| Approach | Error | Fix |
|---|---|---|
| `import urllib.request` in Odoo | forbidden opcode IMPORT_NAME | Odoo blocks ALL imports |
| `exec(code)` from GitHub in Odoo | forbidden opcode | Odoo safe_eval blocks exec |
| Triple-quote docstring in Odoo webhook | Access to forbidden name __doc__ | Use # comments only |
| `env.user.message_post()` in webhook | res.users has no message_post | Remove all logging |
| `json.loads(payload)` when payload is dict | TypeError | `if isinstance(payload, str): payload = json.loads(payload)` |
| `["type", "=", "other"]` for properties | Wrong results | Use `["x_studio_x_studio_record_category", "=", "Property"]` |
| `JobSource = "Reactivation"` | Workiz validation error | Use "Referral" |
| `type_of_service = ""` | Workiz validation error | Use "On Request" |
| `frequency = ""` | Workiz validation error | Use "Unknown" |
| `workiz_job.get('type_of_service')` | Returns None | Use `workiz_job.get('type_of_service_2')` |
| `confirm_sales_order()` then read date_order | Returns current time, not job date | Write date_order back after confirm — Odoo resets it internally |
| `datetime.now()` in Odoo 19 Server Action | 'wrap_module' has no attribute 'now' | Use `datetime.datetime.now()` — datetime is the module in Odoo 19, not the class |
| Server Action via `type="action"` button missing `action = False` | 'Response' object has no attribute 'setdefault' | Always end Server Action code with `action = False` — Odoo 19 tries to use return value as navigation action |
| Using `response = requests.get(...)` in server action | 'Response' object has no attribute 'setdefault' | `response` is a reserved variable in Odoo 19 eval context — rename to `workiz_resp`, `api_resp`, etc. Same applies to `result`. |
| HTML tags in `message_post` body (`<br/>`, `<p>`, `<strong>`) | Tags display as literal text in chatter | Use plain text with ` \| ` pipe separators — Odoo escapes HTML in both server actions (Odoo 17+) and external JSON-RPC calls. Format: `[YYYY-MM-DD HH:MM:SS] Label: Field: Value \| Field: Value` |
| No green indicator in chatter | N/A — previously thought impossible | Unicode emoji works fine — only HTML is escaped. Use `✅` for success, `⚠️` for warnings, `❌` for failures. DJ prefers `✅` on all completion messages. |

---

## GITHUB DEPLOYMENT WORKFLOW

**We use `gh` (GitHub CLI), NOT `git` commands! Push directly to `main`!**

### Claude Code runs this (bash calling PowerShell):
```bash
cd "C:\Users\dj\Documents\Business\A Window and Solar Care\Migration to Odoo"
powershell -Command "
\$repo = 'windowandsolarcare-hash/Odoo-Migration'
\$filePath = '1_Production_Code/zapier_phase4_FLATTENED_FINAL.py'
\$sha = (gh api \"repos/\$repo/contents/\$filePath\" --jq '.sha').Trim()
\$content = Get-Content \$filePath -Raw -Encoding UTF8
\$bytes = [System.Text.Encoding]::UTF8.GetBytes(\$content)
\$base64 = [System.Convert]::ToBase64String(\$bytes)
\$payload = @{
    message = 'YYYY-MM-DD | filename | description'
    content = \$base64
    sha     = \$sha
    branch  = 'main'
} | ConvertTo-Json -Depth 10
\$payload | gh api \"repos/\$repo/contents/\$filePath\" --method PUT --input -
"
```

### User can also run this directly in PowerShell terminal:
```powershell
$repo = "windowandsolarcare-hash/Odoo-Migration"
$filePath = "1_Production_Code/zapier_phase3_FLATTENED_FINAL.py"
$sha = (gh api "repos/$repo/contents/$filePath" --jq '.sha').Trim()
$localFile = "C:\Users\dj\Documents\Business\A Window and Solar Care\Migration to Odoo\$filePath"
$content = Get-Content $localFile -Raw -Encoding UTF8
$bytes = [System.Text.Encoding]::UTF8.GetBytes($content)
$base64 = [System.Convert]::ToBase64String($bytes)
$payload = @{
    message = "YYYY-MM-DD | filename | description"
    content = $base64
    sha     = $sha
    branch  = "main"
} | ConvertTo-Json -Depth 10
$payload | gh api "repos/$repo/contents/$filePath" --method PUT --input -
```

### Notes
- Commit format: `YYYY-MM-DD | filename | description of change`
- For new files (no existing SHA): omit `sha` from payload
- Always push to `main` — Zapier watches main only

---

## MEMORY RULE — CRITICAL

**Whenever you discover something new about this project — a field name, an API quirk, a bug root cause, a Workiz/Odoo behavior, a business decision — write a memory file IMMEDIATELY before continuing. Do not wait until end of session or rely on compaction to capture it.**

Memory directory: `C:\Users\dj\.claude\projects\C--Users-dj-Documents-Business-A-Window-and-Solar-Care-Migration-to-Odoo\memory\`

Use type `project` for technical facts about how the system behaves. Include **Why:** and **How to apply:** lines.

---

## CODE MODIFICATION WORKFLOW

1. Read the current local version first
2. Make the requested changes
3. Save locally
4. Push to GitHub main using deployment script above
5. Confirm to user: what changed, file name, that it's on GitHub main
6. Zapier auto-fetches latest code on next trigger (NO manual Zapier update needed)

---

## PLATFORM MIGRATION RULE

**When migrating code between platforms (Zapier → Odoo, Odoo → Zapier, etc.):**

**NEVER:**
- Simplify, optimize, or "clean up" existing code
- Strip down features, logging, or field mappings
- Remove ANY functionality that exists in the original

**ALWAYS:**
- Copy ALL functionality exactly (1:1 functional duplicate)
- Only change what's technically required for the new platform

**Why:** This code represents months of development. Every detail exists for a reason.

---

## TESTING WORKFLOW

**YOU create and cleanup ALL test data via API. User never manually creates/deletes.**

1. Make code changes locally → push to GitHub main
2. YOU create test data via API (Workiz: `test_create_workiz_job.py` / Odoo: JSON-RPC)
3. Trigger/monitor Zapier
4. Verify results
5. YOU cleanup test data via API

Scripts: `2_Testing_Tools/test_create_workiz_job.py`, `test_cleanup_workiz_job.py`, `test_cleanup_odoo_data.py`

---

## PHASE STATUS

| Phase | Purpose | Trigger | File |
|---|---|---|---|
| 1 | Historical Migration | One-time (complete) | N/A |
| 2 | Reactivation Engine | Odoo Server Action (manual) | ODOO_REACTIVATION_*.py |
| 2B | STOP Compliance | Workiz → Odoo direct webhook | odoo_webhook_stop_handler.py |
| 3 | New Job Creation | Workiz webhook → Zapier | zapier_phase3_FLATTENED_FINAL.py |
| 4 | Job Status Updates | Zapier polling (5 min) | zapier_phase4_FLATTENED_FINAL.py |
| 5 | Auto Job Scheduling | Phase 6 webhook trigger | zapier_phase5_FLATTENED_FINAL.py |
| 6 | Payment Sync | Odoo webhook → Zapier | zapier_phase6_FLATTENED_FINAL.py |

**STOP webhook URL:** `https://window-solar-care.odoo.com/web/hook/f64d0bc1-54fd-45a1-b645-0dcae6ae1728`

---

## KNOWN FIXES & BEHAVIORS (CHANGELOG)

| Date | File | What | Why |
|---|---|---|---|
| 2026-04-01 | phase4 | `confirm_sales_order()` writes date_order back after confirm | Odoo action_confirm() resets date_order to now() internally |
| 2026-04-01 | phase4, phase5 | Read `type_of_service_2` not `type_of_service` | Workiz API returns custom field as type_of_service_2 |
| 2026-04-01 | phase5 | New job payload uses `type_of_service_2` | Write path must match read path |
| 2026-04-01 | phase5 | Added `ok_to_text` and `confirmation_method` to new job payload | Fields were missing from new maintenance jobs |
| 2026-03-19 | phase4 | Property search uses `x_studio_x_studio_record_category` | type="other" returned wrong results |
| 2026-03-19 | reactivation | Fixed PostalCode strip non-digits | Workiz sometimes sends "93117-1234" format |
| 2026-03-19 | reactivation | Fixed last_date_cleaned year (0025 → 2025) | Raw year was 2-digit, needed +2000 |

---

## CONVERSATION ADDITIONS (March–April 2026)

- **STOP Odoo webhook:** URL above — Workiz must send here directly
- **Reactivation CRM Activity:** `{campaign} | {date} | Job #{so_name} | {primary_service}` for x_name; x_description = actual SMS text
- **Contact link on SO:** Related field `partner_shipping_id.parent_id` in Odoo Studio
- **Add-on pricing:** base_price < $70 = no inflation, no $85 floor
- **Phase 5 next date:** Use completed job's JobDateTime, not datetime.now()
- **Phase 5 last_date_cleaned:** Populate on new maintenance jobs
- **Orphaned future jobs:** Leave alone (no auto-delete)
- **Graveyard job:** Always create new (don't reuse existing future job)

---

## CODEBASE ORGANIZATION

- **1_Production_Code/** — Active scripts running the business
- **2_Testing_Tools/** — API test scripts
- **3_Documentation/** — Active manuals
- **4_Reference_Data/** — CSVs and mappings
- **z_ARCHIVE_DEPRECATED/** — Old files

---

## ODOO HTML FIELD COLOR PATTERN (DJ uses this frequently)

To show colored status indicators on Odoo form fields:

1. **Field must be `ttype: html`** (not char — char cannot render HTML)
2. **Add to view as `readonly="True"`** so the rich text editor never appears
3. **Write Bootstrap classes** — these survive Odoo's HTML sanitizer (inline `style=` gets stripped):

```python
'<span class="text-success"><b>OK - details</b></span>'    # green
'<span class="text-danger"><b>MISMATCH - details</b></span>'  # red
'<span class="text-warning"><b>PENDING - details</b></span>'  # orange
'<span class="text-info"><b>INFO - details</b></span>'        # blue
```

**To create a new HTML field via API:**
- Get model ID: search `ir.model` where `model = 'sale.order'` → ID **670**
- Create: `ir.model.fields` create with `ttype: html, store: true`
- If field already exists as char: remove from all views first → unlink → recreate → re-add
- Studio SO form view ID = **1385** (`Odoo Studio: sale.order.form customization`)

---

## COMMUNICATION STYLE

- Be concise — DJ is experienced, skip basic explanations
- Always confirm what branch you committed to
- If something fails, explain exactly why and give the fix
- Never ask "would you like me to..." for things clearly part of the task — just do them
- When done: short summary of what changed, where it lives, next step

---

## REFERENCE FILES (deep detail only, not required reading)

- `CLAUDE_CONTEXT.md` - Phase-by-phase detail, API patterns
- `MASTER_PROJECT_CONTEXT.md` - Extended field mappings, API syntax examples
- `3_Documentation/BUSINESS_WORKFLOW.md` - Business processes
