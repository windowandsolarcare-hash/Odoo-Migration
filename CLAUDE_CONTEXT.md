# CLAUDE_CONTEXT.md
**Last Updated:** 2026-03-16  
**Purpose:** Complete project context for new AI chat sessions  
**Business:** A Window & Solar Care (DJ Sanders, Owner)

---

## 📘 PROJECT OVERVIEW

**Goal:** Bi-directional real-time sync between Workiz (field service software) and Odoo (business operations platform).

**Strategic Direction:** **ELIMINATE ZAPIER.** Future development should prioritize direct integrations (Odoo Server Actions, Webhooks, Python) over Zapier middleware to reduce cost, latency, and complexity.

**Business Need:** Eliminate manual data entry, ensure data consistency, automate customer follow-ups, and optimize scheduling based on geography.

**Hierarchy:** Contact → Property → Sales Order (job) - maintained across both systems.

**External ID Pattern:** `workiz_[id]` (Mirror V31.11 logic) - every record links back to Workiz source.

**Tech Stack:**
- **Workiz:** Source of truth for field operations (jobs, customers, scheduling)
- **Odoo:** Business operations (CRM, invoicing, projects, inventory)
- **Zapier:** Automation layer (webhooks + Python code steps)
- **GitHub:** Version control (windowandsolarcare-hash/Odoo-Migration)
- **MCP Tools:** filesystem, github, zapier (for AI-assisted development)

---

## 🎯 ALL PHASES STATUS

| Phase | Purpose | Trigger | Status | Notes |
|-------|---------|---------|--------|-------|
| **1** | Historical Migration | One-time | ✅ Complete | 6 years of Workiz data migrated to Odoo |
| **2** | Dormant Reactivation | Manual (Odoo Server Action) | ✅ Deployed | 2-stage workflow (PREVIEW + LAUNCH), STOP protected |
| **2B** | STOP Compliance | Workiz Webhook (Status Change) | ✅ Deployed | Auto-blacklist contacts via Zapier |
| **3** | New Job Creation | Workiz Webhook (New Job) | ✅ Deployed | Creates SO in Odoo (Paths A/B/C) |
| **4** | Job Status Updates | Zapier Polling (Job Updated) | ✅ Deployed | Updates SO, creates tasks, syncs line items |
| **5** | Auto Job Scheduling | Phase 6 Trigger | ✅ Deployed | Creates next maintenance job in Workiz |
| **6** | Payment Sync | Odoo Webhook (New Payment) | ✅ Deployed | Adds payment to Workiz, marks Done, triggers Phase 5 |

---

## 📋 PHASE DETAILS

### Phase 1: Historical Data Migration
**Status:** ✅ Complete (prior work)
- Migrated 6 years of Workiz history to Odoo
- Reference file: `Workiz_6Year_Done_History_Master.csv`
- Established `workiz_[id]` pattern for all external IDs

### Phase 2: Dormant Customer Reactivation
**Status:** ✅ Deployed (2-Stage Workflow: PREVIEW + LAUNCH)
- **Production Files:**
  - `1_Production_Code/ODOO_REACTIVATION_PREVIEW.py` (PREVIEW Server Action)
  - `1_Production_Code/ODOO_REACTIVATION_COMPLETE_NO_IMPORTS.py` (LAUNCH Server Action)
- **Architecture (2026-03-16 Update):**
  - **PREVIEW:** Composes SMS → Writes to `x_studio_manual_sms_override` field → Posts to chatter
  - **LAUNCH:** Reads from field → Sends SMS via Workiz API
  - User can modify text in field between PREVIEW and LAUNCH
- **Features:**
  - Smart pricing: 5% annual compound inflation, rounds to $5, $85 minimum (solar flat)
  - City-aware Calendly links (pre-fills customer data)
  - Creates CRM opportunity with expected revenue
  - **Direct Workiz API calls:** Creates graveyard job, updates status to trigger SMS
  - Links graveyard job back to Opportunity (`x_workiz_graveyard_uuid`, `x_workiz_graveyard_link`)
  - Logs activity to Contact (`x_crm_activity_log_ids`)
  - **Updates property pricing:** Writes `x_studio_prices_per_service` after sending
  - **STOP Compliance:** Checks `phone_blacklisted` and `x_studio_activelead` before sending
- **Cooldown:** 90 days (tracks `x_studio_last_reactivation_sent`)
- **SMS Text:** "It's been a while and we'd like to schedule an appointment again!" (updated 2026-03-16)

**Recent Rewrite (2026-03-08):**
- **OLD:** Odoo → Webhook → Zapier → GitHub exec → Workiz API
- **NEW:** Odoo Server Action → Workiz API directly (NO ZAPIER)
- **Why:** Odoo blocks `import` statements ("forbidden opcodes"), couldn't exec() from GitHub
- **Solution:** All Workiz API code embedded directly in Server Action (no external dependencies)
- **Key Fixes:**
  - Date format: Use ISO `YYYY-MM-DD` for Odoo date fields (was causing validation errors)
  - Workiz API: Include API token in URL path: `https://api.workiz.com/api/v1/{API_TOKEN}/`
  - Job fetch: Use GET request with UUID in URL, not POST with JSON payload
  - Job create: Use `json=` parameter (not `data=`), returns list `[{UUID: ...}]`
  - Status update: SubStatus = "API SMS Test Trigger" to trigger Workiz SMS automation
  - Graveyard jobs: Omit `JobDateTime` field entirely to make jobs unscheduled
- **Debug Logging:** Comprehensive logging shows full request/response for troubleshooting
- **Copy/Paste Deployment:** Code must be copied from GitHub into Odoo Server Action UI (no API access to update Server Actions)

**2-Stage Workflow (2026-03-16):**

**Problem:** Outdated addresses/pricing in auto-composed messages needed manual review before sending

**Solution:** Split into PREVIEW (compose + write to field) and LAUNCH (read field + send) steps

**PREVIEW Server Action:**
- **Model:** `sale.order` (reactivation opportunity)
- **What it does:**
  1. Composes complete SMS with pricing, Calendly link, phone, opt-out
  2. Checks STOP compliance (`phone_blacklisted`, `x_studio_activelead`)
  3. Writes full SMS to `x_studio_manual_sms_override` field (plain text with `\n\n` for line breaks)
  4. Posts same text to chatter for quick viewing
- **User workflow after PREVIEW:**
  - Check chatter preview
  - Go to "SMS Text Modified" tab on sale.order
  - See auto-composed text in `x_studio_manual_sms_override` field
  - Edit if needed (or leave as-is)
  - Click LAUNCH
- **GitHub URL:** `https://raw.githubusercontent.com/windowandsolarcare-hash/Odoo-Migration/main/1_Production_Code/ODOO_REACTIVATION_PREVIEW.py`

**LAUNCH Server Action:**
- **Model:** `sale.order` (reactivation opportunity)
- **What it does:**
  1. Reads SMS from `x_studio_manual_sms_override` field
  2. If field empty, posts error (must run PREVIEW first)
  3. Checks STOP compliance (`phone_blacklisted`, `x_studio_activelead`)
  4. Sends SMS via Workiz API (creates job, updates status)
  5. Updates `x_studio_last_reactivation_sent` on contact (for 90-day cooldown)
  6. Updates `x_studio_prices_per_service` on property (for historical record)
  7. Posts success message to opportunity chatter
- **GitHub URL:** `https://raw.githubusercontent.com/windowandsolarcare-hash/Odoo-Migration/main/1_Production_Code/ODOO_REACTIVATION_COMPLETE_NO_IMPORTS.py`

**Field Format Discovery:**
- ✅ Plain text with `\n\n` (double newlines) between paragraphs = perfect formatting
- ✅ Field content survives copy/paste and manual edits
- ✅ All 15+ line breaks preserved in 500-character SMS
- ❌ HTML formatting (`<br/>`, `<p>`) not needed and complicates copy/paste
- ❌ Single `\n` doesn't always render as line break in Odoo UI

### Phase 3: New Job Creation (Master Router)
**Status:** ✅ Deployed to Zapier
- **Trigger:** Workiz "New Job Created" webhook
- **File:** `2_Modular_Phase3_Components/zapier_phase3_FLATTENED_FINAL.py` (1,539 lines)
- **Zapier Setup:**
  ```python
  import urllib.request
  url = "https://raw.githubusercontent.com/windowandsolarcare-hash/Odoo-Migration/main/2_Modular_Phase3_Components/zapier_phase3_FLATTENED_FINAL.py"
  code = urllib.request.urlopen(url).read().decode()
  exec(code, {**globals(), 'input_data': input_data})
  ```
- **Paths:**
  - **Path A:** Contact + Property exist → Create SO only
  - **Path B:** Contact exists, Property missing → Create Property + SO
  - **Path C:** Both missing → Create Contact + Property + SO
- **Key Features:**
  - Search by ClientId (not name/address)
  - Merge Contact tags + Workiz tags
  - Convert Pacific → UTC for date_order
  - Map 20+ custom fields
  - Create line items from Workiz products
  - Only confirms SO (creates task) when status = "Scheduled" or similar
- **Important:** SO stays as quotation (draft) until status changes to scheduled

### Phase 4: Job Status Updates & Task Sync
**Status:** ✅ Deployed to Zapier (uses Zapier Polling, not webhook)
- **Trigger:** Zapier "Updated Job in Workiz" (polling every 1-5 minutes)
- **File:** `2_Modular_Phase3_Components/zapier_phase4_FLATTENED_FINAL.py` (2,051 lines)
- **Key Features:**
  - Skips when status="Submitted" (new job from Phase 5, Phase 3 handles it)
  - Searches for SO by `x_studio_x_studio_workiz_uuid`
  - If SO missing, calls Phase 3 logic to create it
  - Updates all fields: status, tech, dates, notes, gate code, pricing
  - **Confirms SO (creates tasks)** when status becomes "Scheduled"
  - **Smart line item sync on confirmed SOs:**
    - Updates prices on existing items
    - Adds new items (command: `(0, 0, vals)`)
    - Sets qty=0 for removed items (can't delete on confirmed SOs)
    - Safety flag: `ENABLE_LINE_ITEM_REMOVAL_ON_CONFIRMED_SO = True`
    - Critical fix: Uses `limit=100` when fetching existing lines
  - Updates Property fields (gate code, pricing, frequency, alternating, service type)
  - Updates Property last visit date when Done
  - Posts status updates to SO chatter
  - Does NOT write payment fields (payment originates in Odoo via Phase 6)
- **Task Sync:** Every Phase 4 run updates existing task(s) with current Workiz data:
  - Task name = "Customer Name - City"
  - Assignee/tech
  - Planned date, start/end (UTC from Workiz Pacific)
  - Phone from Contact
  - Tags
  - Never creates duplicate tasks; changing date in Workiz moves the task
- **Workiz Webhook Limitation:** Workiz webhooks only fire ONCE per job (when created), NOT on updates. That's why Phase 4 uses Zapier polling.

### Phase 5: Auto Job Scheduling
**Status:** ✅ Deployed to Zapier
- **Trigger:** Webhooks by Zapier (called by Phase 6)
- **File:** `2_Modular_Phase3_Components/zapier_phase5_FLATTENED_FINAL.py` (858 lines)
- **Inputs:** `job_uuid`, `property_id`, `contact_id`, `customer_city`, `invoice_id`
- **Paths:**
  - **5A: Maintenance** → Creates next job in Workiz
  - **5B: On Demand** → Creates Odoo activity reminder (no Workiz job)
- **Path 5A Features:**
  - Calculates next date based on `frequency` field (3 Months, 4 Months, etc.)
  - **City-aware scheduling** (matches Calendly setup):
    - Palm Springs → Friday
    - Rancho Mirage → Thursday
    - Palm Desert → Thursday
    - Indian Wells → Wednesday
    - Indio/La Quinta → Wednesday
    - Hemet → Tuesday
  - **Alternating service logic:**
    - Toggles job type: "Outside Windows and Screens" ↔ "Windows Inside & Outside Plus Screens"
    - Searches history for most recent job matching NEXT job type, pulls those line items
    - Fixed 2026-03-05: Match by job type (not just "2 jobs back")
  - Stores line items reference in `next_job_line_items` custom field
  - Preserves JobNotes from previous job
  - Creates job in Workiz (HTTP 200/204 handled)
  - **Writes Workiz link to invoice field:** `x_studio_workiz_job_link` (added 2026-03-05)
  - Posts notification to invoice chatter
- **Path 5B Features:**
  - Calculates follow-up date (6 months default, adjusted to Sunday)
  - Creates `mail.activity` in Odoo (NOT a Workiz job)
  - Solves "Sunday Nightmare" (no fake jobs cluttering Workiz)
- **API Limitation:** Workiz API doesn't support LineItems on job creation
  - Workaround: Store as text in custom field, user adds manually (30 sec)

### Phase 6: Payment Sync (Odoo → Workiz)
**Status:** ✅ Deployed to Zapier
- **Trigger:** Odoo "New Payment" webhook (account.payment model)
- **File:** `2_Modular_Phase3_Components/zapier_phase6_FLATTENED_FINAL.py` (342 lines)
- **Inputs:** `payment_id` (Zapier maps from webhook)
- **Workflow:**
  1. Look up payment by ID
  2. Get reconciled invoice
  3. Get SO from invoice origin
  4. Get Workiz UUID from SO
  5. Add payment to Workiz (amount, date, type, **check number** from `memo` field)
  6. If invoice fully paid (balance=0), mark Workiz job "Done"
  7. Trigger Phase 5 (pass `invoice_id` for Workiz link field)
- **Key Features:**
  - Split payment support: Only marks Done when balance=0
  - **Check number sync:** Odoo `memo` field → Workiz `reference` (fixed 2026-03-05)
  - Payment type mapping: Cash, Credit, Check, Zelle
  - Passes `invoice_id` to Phase 5 for Workiz link population
- **Hybrid Architecture:** Phase 3 uses webhook, Phase 4 uses polling, Phase 5 is triggered by Phase 6, Phase 6 uses webhook

---

## 🔄 PHASE 2 REACTIVATION ARCHITECTURE (March 2026 Rewrite)

### Why We Eliminated Zapier for Reactivation

**Original Design (Failed):**
```
Odoo Server Action → Webhook → Zapier → exec(GitHub code) → Workiz API
```

**Problems:**
1. Odoo blocks `import urllib.request` ("forbidden opcode" error)
2. Couldn't fetch GitHub code from within Odoo
3. Zapier added latency and complexity
4. GitHub CDN caching caused stale code issues
5. No direct API access to update Odoo Server Actions

**Final Design (Working):**
```
Odoo Server Action (single file, all-inline) → Workiz API directly
```

### Odoo Server Action Limitations

**What's Blocked:**
- ❌ ALL `import` statements (IMPORT_NAME, IMPORT_FROM opcodes)
- ❌ Dunder names like `__name__`, `__file__`
- ❌ Direct API calls to update Server Actions (Access Denied)

**What's Available:**
- ✅ `requests` library (pre-loaded, no import needed)
- ✅ `datetime` module (pre-loaded)
- ✅ `json` module (pre-loaded)
- ✅ Odoo `env` context (access to all models)
- ✅ `records` variable (selected records in UI)

### Workiz API Specifics for Reactivation

**Endpoint Format:**
```python
WORKIZ_API_TOKEN = "api_1hu6lroiy5zxomcpptuwsg8heju97iwg"
WORKIZ_BASE_URL = f"https://api.workiz.com/api/v1/{WORKIZ_API_TOKEN}"
```

**Job Fetch (GET):**
```python
url = f"{WORKIZ_BASE_URL}/job/get/{uuid}/?auth_secret={WORKIZ_AUTH_SECRET}"
response = requests.get(url, timeout=10)
result = response.json()
historical_job = result.get('data', [])[0]
```

**Job Create (POST):**
```python
# Omit JobDateTime for unscheduled jobs
job_data = {
    "auth_secret": WORKIZ_AUTH_SECRET,
    "ClientId": "1234",  # NOT "CL-1234"
    # ... other fields ...
    # JobDateTime omitted = unscheduled
}
response = requests.post(f"{WORKIZ_BASE_URL}/job/create/", json=job_data, timeout=10)
result = response.json()  # Returns list: [{UUID: 'ABC123', ...}]
graveyard_uuid = result[0].get('UUID')
```

**Status Update (POST):**
```python
status_payload = {
    "auth_secret": WORKIZ_AUTH_SECRET,
    "UUID": graveyard_uuid,
    "Status": "Pending",
    "SubStatus": "API SMS Test Trigger"  # Exact string triggers SMS
}
response = requests.post(f"{WORKIZ_BASE_URL}/job/update/", json=status_payload, timeout=10)
```

### Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `forbidden opcode(s) IMPORT_NAME` | Used `import` statement | Remove all imports, use pre-loaded modules |
| `forbidden name '__name__'` | Used dunder in debug | Remove `type(x).__name__`, use `str(type(x))` |
| `HTTP 404` on job/get | Missing API token in URL | Include token in path: `api/v1/{TOKEN}/` |
| `'list' object has no attribute 'get'` | Wrong response parsing | Check `isinstance(result, list)` first |
| `time data '03/08/2026' does not match '%Y-%m-%d'` | US date format in ISO field | Use `current_date_iso = '2026-03-08'` for Odoo fields |
| Job created but status not updated | Timing issue or wrong SubStatus | Wait 3 seconds after create, verify exact SubStatus string |
| `TypeError: string indices must be integers` (Odoo API) | Wrong payload format for `create`/`write` | Use lists: `create([[{...}]])`, `write([[id], {...}])` |
| `ValueError: Wrong value for res.partner.x_studio_activelead: 'do_not_contact'` | Selection field value mismatch | Use exact string: `"Do Not Contact"` (case-sensitive) |
| `Invalid field 'x_studio_x_draft_sms_message' on 'sale.order'` | Field exists on wrong model | Check field location (opportunity vs sale.order) |
| Zapier "Output Missing" error | No `return` or `output` variable | Return `output` dict or set `exec_globals['output']` |
| Missing line breaks in Odoo chatter/fields | Single `\n` not rendering | Use double newlines `\n\n` between paragraphs |

### Deployment Process

**Cannot Use:**
- ❌ GitHub exec() (Odoo blocks imports)
- ❌ MCP/API to update Server Actions (Access Denied)
- ❌ Zapier (unnecessary complexity, eliminated)

**Must Use:**
1. Edit `ODOO_REACTIVATION_COMPLETE_NO_IMPORTS.py` locally
2. Push to GitHub main (for version control)
3. **Manually copy/paste** into Odoo Server Action UI
4. Test with real customer (debug logs in chatter)

**GitHub Link:**
```
https://github.com/windowandsolarcare-hash/Odoo-Migration/blob/main/1_Active_Odoo_Scripts/ODOO_REACTIVATION_COMPLETE_NO_IMPORTS.py
```

### Professional Standards Discussion

**Question:** Is GitHub exec() approach professional?

**Answer for Odoo Cloud:**
- ✅ Standard: Code directly in Server Action UI
- ✅ Best Practice: Export XML backups, store in Git
- ❌ Not Standard: GitHub exec() (convenience hack, security risk)
- ❌ Blocked: Cannot use anyway (forbidden opcodes)

**For Odoo Self-Hosted:**
- ✅ Professional: Custom Odoo modules in `/addons` directory
- ✅ CI/CD: Git → deployment pipeline → server
- ❌ Not Standard: GitHub exec() runtime fetches

**Our Approach (Hybrid):**
- Development: Edit locally, push to GitHub (version control)
- Deployment: Manual copy/paste to Odoo UI (required for Cloud)
- Production: All code inline, no external dependencies

---

## 🗂️ KEY FILES & DIRECTORIES

### Python Scripts (Production)
```
1_Production_Code/
├── ODOO_REACTIVATION_PREVIEW.py              - PREVIEW Server Action (2-stage workflow)
├── ODOO_REACTIVATION_COMPLETE_NO_IMPORTS.py  - LAUNCH Server Action (2-stage workflow)
└── ODOO_REACTIVATION_MODIFY_WIZARD.py        - DEPRECATED (wizard approach abandoned)

2_Modular_Phase3_Components/
├── zapier_phase3_FLATTENED_FINAL.py  (1,539 lines) - New job creation (Zapier)
├── zapier_phase4_FLATTENED_FINAL.py  (2,051 lines) - Status updates & task sync (Zapier)
├── zapier_phase5_FLATTENED_FINAL.py  (858 lines)   - Auto scheduling (Zapier)
├── zapier_phase6_FLATTENED_FINAL.py  (342 lines)   - Payment sync (Zapier)
├── zapier_stop_handler.py            (NEW)         - STOP compliance handler (Zapier)
├── zapier_reactivation_sms_FINAL.py  (DEPRECATED)  - Old Zapier reactivation (no longer used)
├── odoo_workiz_reactivation_direct.py (DEPRECATED) - Failed GitHub exec approach
└── functions/                         - Atomic functions (not used in prod, reference only)

2_Testing_Tools/
├── test_create_workiz_job.py         - Create test job in Workiz
├── test_cleanup_workiz_job.py        - Mark test job as cancelled
├── test_cleanup_odoo_data.py         - Delete SO/Invoice/Payment in Odoo
├── dump_contact.py                   - Fetch contact details for debugging
└── read_sms_field.py                 - Read SMS override field content
```

### Documentation
```
3_Documentation/
├── PROJECT_COMPLETE_SUMMARY.md      - Overall project status
├── COMPLETE_PHASE_OVERVIEW.md       - All phases detail
├── Zapier_Architecture_Complete.md  - How Zaps work together
├── AI Handoffs/                     - Deployment guides for each phase
└── Workiz_API_Test_Results.md      - API testing notes
```

### Configuration
```
.cursorrules                          - Cursor IDE rules (MCP, branch workflow, etc.)
CLAUDE_CONTEXT.md                     - This file
```

### Reference Data
```
5_Reference_Data/
├── Workiz_6Year_Done_History_Master.csv - Historical migration source
├── Custom Field names.csv               - Odoo custom fields list
└── Fields (ir.model.fields).csv         - Odoo field metadata
```

---

## 🔧 DEVELOPMENT WORKFLOW

**CRITICAL: We use `gh` (GitHub CLI), NOT `git` commands!**
**Golden Rule: Code lives in GitHub, NOT in Zapier UI!**

### Making Code Changes:

1. **Edit locally:** Open file in Cursor (e.g., `zapier_phase5_FLATTENED_FINAL.py`)
2. **Make changes:** Add features, fix bugs, update logic
3. **Test if possible:** Create test script (e.g., `test_phase5_alternating.py`)
4. **Push to GitHub main using `gh api`:**
   ```powershell
   $repo = "windowandsolarcare-hash/Odoo-Migration"
   $filePath = "2_Modular_Phase3_Components/zapier_phase5_FLATTENED_FINAL.py"
   $date = Get-Date -Format "yyyy-MM-dd"
   
   # Get current SHA (for existing files)
   $sha = gh api "repos/$repo/contents/$filePath" --jq '.sha' 2>&1
   if ($LASTEXITCODE -eq 0) { $sha = $sha.Trim() }
   
   # Convert file to base64
   $localFile = "C:\Users\dj\Documents\Business\A Window and Solar Care\Migration to Odoo\$filePath"
   $content = Get-Content $localFile -Raw -Encoding UTF8
   $bytes = [System.Text.Encoding]::UTF8.GetBytes($content)
   $base64 = [System.Convert]::ToBase64String($bytes)
   
   # Create payload (include SHA for existing files)
   if ($LASTEXITCODE -eq 0) {
       $payload = @{message = "$date | phase5 | Fix description"; content = $base64; sha = $sha; branch = "main"} | ConvertTo-Json -Depth 10
   } else {
       $payload = @{message = "$date | phase5 | Fix description"; content = $base64; branch = "main"} | ConvertTo-Json -Depth 10
   }
   
   # Push to GitHub
   $payload | gh api "repos/$repo/contents/$filePath" --method PUT --input -
   ```
5. **Zapier auto-updates:** Next trigger fetches new code from main
6. **No Zapier UI changes needed** (unless input field mappings change)

**Why `gh` and not `git`?**
- ✅ Works without local git repository initialization
- ✅ Uses GitHub REST API directly
- ✅ No need for git install, git config, or SSH keys
- ✅ Simple PowerShell scripts for each push
- ✅ Same workflow used for ALL file pushes (phases, docs, planning, etc.)

### When to Update Zapier UI:

**Only update Zapier when:**
- Adding new input fields (e.g., adding `invoice_id` to Phase 5 inputs)
- Changing trigger type (webhook → polling)
- Changing webhook URL

**NEVER update Zapier for:**
- Code logic changes
- Bug fixes
- New features in Python code
- Variable names or function signatures

### Testing Strategy:

**CRITICAL: YOU create and cleanup ALL test data via API**

**Testing Workflow:**
1. Make code changes locally
2. Push to GitHub main (using `gh api` workflow)
3. **Create test data via API (don't ask user):**
   - Workiz jobs: `python test_create_workiz_job.py` → Returns UUID
   - Odoo data: Use Odoo JSON-RPC API calls
4. Trigger/monitor Zapier:
   - Webhook triggers automatically
   - Or manually trigger in Zapier dashboard
5. Verify results:
   - Check Zapier task history logs
   - Verify SO/Invoice/Payment in Odoo
   - Verify job status in Workiz
6. **Cleanup test data via API:**
   - Workiz: `python test_cleanup_workiz_job.py <UUID>`
   - Odoo: `python test_cleanup_odoo_data.py --so 123 --invoice 456`
7. Report to user: "✅ Working" or "❌ Issue: [details]"

**Why API-Based Test Data:**
- ✅ Tests FULL integration (Workiz webhook → Zapier → Odoo)
- ✅ Mimics real workflow (proper triggers, API calls, etc.)
- ❌ Don't create data directly in Odoo (skips webhook/Zapier steps)

**User's Role:**
- Approve or reject test results ONLY
- **Never** manually creates test data
- **Never** manually deletes test data

**Available Test Scripts:**
- `test_create_workiz_job.py` - Create test job in Workiz
- `test_cleanup_workiz_job.py` - Mark job as cancelled
- `test_cleanup_odoo_data.py` - Delete SO/Invoice/Payment
- `TEST_FRAMEWORK.md` - Complete testing guide

---

## 🛠️ MCP TOOLS SETUP

**Available MCPs:**
- **filesystem (project-0-Migration_to_Odoo-filesystem):** Read/write local files in workspace
- **github (project-0-Migration_to_Odoo-github):** GitHub operations (branch, commit, push, PR)
- **zapier (project-0-Migration_to_Odoo-Zapier):** Zapier zap management and testing

**MCP Folder:** `C:\Users\dj\.cursor\projects\c-Users-dj-Documents-Business-A-Window-and-Solar-Care-Migration-to-Odoo\mcps\`

**Usage:** Always use MCP tools instead of asking user to do things manually. Example: Use github MCP to commit/push, not "git" shell commands.

---

## 🌿 BRANCH WORKFLOW

**CRITICAL: Zapier watches `main` branch ONLY.**
**CRITICAL: We use `gh` (GitHub CLI), NOT `git` commands!**

**Current Workflow (Direct to Main):**
1. **Edit files locally** (e.g., `zapier_phase5_FLATTENED_FINAL.py`)
2. **Push directly to main** using `gh api` PowerShell scripts (see above)
3. **Zapier auto-fetches** latest code on next run
4. **No dev branch, no git repo** (we use GitHub REST API via `gh`)

**Why Direct to Main?**
- Zapier fetches from GitHub on **every single run** (via `urllib.request.urlopen()`)
- Changes are immediate but safe (only affect next trigger, not mid-run)
- Easy rollback: Revert GitHub commit → Zapier uses old version
- No merge/deploy step needed (Zapier IS the deployment)
- No git installation or repository initialization required

**Why `gh` CLI Instead of `git`?**
- ✅ **git not installed** on this system (and doesn't need to be)
- ✅ **gh CLI** (GitHub CLI) is installed and works via REST API
- ✅ No need for local git repo, git config, or SSH keys
- ✅ Direct file push via `gh api repos/.../contents/path --method PUT`
- ✅ Same workflow for everything: phases, docs, planning folders, etc.

**Rollback Process (using `gh api`):**
```powershell
# Get previous commits
gh api repos/windowandsolarcare-hash/Odoo-Migration/commits --jq '.[:10] | .[] | {sha: .sha[:7], message: .commit.message}'

# Fetch old file version
gh api repos/windowandsolarcare-hash/Odoo-Migration/contents/path/to/file.py?ref=COMMIT_SHA --jq '.content' | base64 -d > file.py

# Push back to main using normal workflow (see above)
```

**Commit Message Format:**
```
YYYY-MM-DD | filename | what changed and why
```

Example: `2026-03-05 | zapier_phase5 | Fix alternating line items - match by job type`

**Deployed Files (as of 2026-03-05):**
- ✅ zapier_phase3_FLATTENED_FINAL.py
- ✅ zapier_phase4_FLATTENED_FINAL.py
- ✅ zapier_phase5_FLATTENED_FINAL.py
- ✅ zapier_phase6_FLATTENED_FINAL.py
- ✅ CLAUDE_CONTEXT.md
- ✅ .cursorrules
- ✅ planning/BUSINESS_WORKFLOW.md
- ✅ planning/Gap_Analysis_Complete_Workflow.md

---

## 💻 ZAPIER PYTHON EXEC() APPROACH

**CRITICAL: We do NOT paste code into Zapier anymore!**

All Zapier Code steps now use this **3-line snippet** that fetches code from GitHub:

```python
import urllib.request
url = "https://raw.githubusercontent.com/windowandsolarcare-hash/Odoo-Migration/main/2_Modular_Phase3_Components/zapier_phaseX_FLATTENED_FINAL.py"
code = urllib.request.urlopen(url).read().decode()
exec(code, {**globals(), 'input_data': input_data})
```

**This means:**
- ✅ **Code lives in GitHub, NOT in Zapier UI**
- ✅ **To modify code:** Edit file locally → Push to GitHub main → Zapier auto-fetches latest on next run
- ✅ **NO manual Zapier updates needed** when code changes
- ✅ **Version control:** Full git history, can rollback anytime
- ✅ **Deployment:** Push to main = instant production (Zapier fetches on next trigger)

**Each Zapier "Code by Zapier" step contains ONLY those 4 lines above.** The actual business logic is in the GitHub files.

**Benefits:**
- ✅ Zapier always runs latest code from GitHub main branch
- ✅ No copy-paste between GitHub and Zapier UI
- ✅ No Zapier code editor limitations (token limits, syntax highlighting)
- ✅ Easy rollback: Revert GitHub commit → Zapier uses old version
- ✅ No deployment sync issues (one source of truth)

**How It Works:**
1. Zapier trigger fires (webhook or polling)
2. Zapier Code step receives `input_data` dict from trigger/previous step
3. Code step runs the 4-line snippet
4. Snippet fetches Python file from GitHub main branch (fresh every time)
5. `exec()` runs the file contents in Zapier's environment
6. File's `main(input_data)` function processes the data
7. Returns `output` dict for next Zapier step

**Input Mapping Examples (in Zapier UI):**
- **Phase 3:** `job_uuid` from Workiz webhook
- **Phase 4:** `job_uuid` from Zapier polling
- **Phase 5:** `job_uuid`, `property_id`, `contact_id`, `customer_city`, `invoice_id` from Phase 6 webhook
- **Phase 6:** `payment_id` from Odoo payment webhook

**When Modifying Code:**
1. Edit file locally (e.g., `zapier_phase5_FLATTENED_FINAL.py`)
2. Test logic if possible (create test script)
3. Push to GitHub main: `gh api repos/.../contents/path --method PUT`
4. Next Zapier run fetches new code automatically
5. **NO changes needed in Zapier UI** (unless input field mappings change)

---

## ✅ WHAT'S COMPLETED

### Fully Deployed & Working:
- ✅ Phase 1: Historical migration (6 years of data)
- ✅ Phase 2: Reactivation engine (Odoo Server Actions)
- ✅ Phase 3: New job creation (Workiz → Odoo SO)
- ✅ Phase 4: Status updates + task sync (polling-based)
- ✅ Phase 5: Auto scheduling (alternating services, city routing, Workiz link field)
- ✅ Phase 6: Payment sync (Odoo → Workiz, check number, triggers Phase 5)

### Recent Fixes (2026-03-05):
- ✅ Phase 4: Smart line item sync on confirmed SOs (update prices, add items, set qty=0)
- ✅ Phase 4: Fixed `limit=1` bug (now fetches all line items with `limit=100`)
- ✅ Phase 5: Alternating job type toggle (Outside ↔ Inside&Out)
- ✅ Phase 5: Line items match by NEXT job type (not just "2 jobs back")
- ✅ Phase 5: Writes Workiz link to invoice `x_studio_workiz_job_link` field
- ✅ Phase 6: Check number sync (Odoo `memo` → Workiz `reference`)
- ✅ Phase 6: Passes `invoice_id` to Phase 5

### Major Rewrite (2026-03-08): Phase 2 Reactivation
- ✅ **Eliminated Zapier dependency:** Direct Odoo → Workiz API calls
- ✅ **Fixed forbidden opcodes:** Removed all `import` statements, use pre-loaded modules
- ✅ **Fixed date format errors:** Use ISO format for Odoo date fields
- ✅ **Fixed Workiz API endpoints:**
  - Include API token in URL path
  - Use GET for job/get (not POST)
  - Parse list response from job/create
  - Omit JobDateTime for unscheduled jobs
  - Use exact SubStatus string: "API SMS Test Trigger"
- ✅ **Added comprehensive debug logging:** Full request/response visibility
- ✅ **Simplified architecture:** One self-contained file, no external dependencies
- 🚧 **In Testing:** Status update to trigger SMS (comprehensive debug logging active)

---

## 🚧 KNOWN ISSUES & GOTCHAS

### Workiz API Limitations:
1. **No LineItems on job/create:** Must store in custom field, user adds manually
2. **No UUID returned on HTTP 204:** Can't immediately link new job to SO
3. **Webhooks only fire once:** Job creation fires webhook, updates do NOT (that's why Phase 4 uses polling)

### Odoo Confirmed SO Restrictions:
1. **Can't delete line items:** Use `(1, line_id, {'product_uom_qty': 0})` instead
2. **Can't add line items via normal write:** Use command format `(0, 0, vals)`
3. **Safety flag in Phase 4:** `ENABLE_LINE_ITEM_REMOVAL_ON_CONFIRMED_SO = True` (can disable if needed)

### Zapier Quirks:
1. **Input mapping required:** Phase 5 needs explicit input mappings in Zapier UI (job_uuid, property_id, contact_id, customer_city, invoice_id)
2. **Catch Hook doesn't auto-map:** Must manually map webhook body fields to Code step inputs
3. **Logs not real-time:** "Logs are not supported for this app" - use print() statements and check task history

### Field Name Sensitivity:
1. **Custom field names are case-sensitive and version-specific**
2. **Use Studio field names** (e.g., `x_studio_workiz_job_link`, not `workiz_job_link`)
3. **payment.memo not payment.ref** for check numbers in Odoo 19

### Alternating Service:
1. **Requires matching job type:** Searches history for most recent job with NEXT job type
2. **Falls back to current job:** If no matching history, uses current job line items
3. **Job type names must match exactly:** "Outside Windows and Screens" (lowercase "and")

### Odoo Server Actions:
1. **No API access:** Cannot update Server Actions via Odoo API (Access Denied for ir.actions.server model)
2. **Must copy/paste:** All code updates require manual copy/paste into Odoo UI
3. **Forbidden opcodes:** ALL `import` statements blocked (IMPORT_NAME, IMPORT_FROM)
4. **Forbidden names:** Dunder names like `__name__`, `__file__` blocked
5. **Available modules:** `requests`, `datetime`, `json`, `env`, `records` pre-loaded (no import needed)
6. **GitHub for version control:** Edit locally, push to GitHub, then copy/paste to Odoo
7. **Break statement required:** Server Actions loop over `records`, must `break` after first

### Odoo Custom Fields (Key Learnings 2026-03-16):

**Text Formatting in Fields:**
- ✅ Plain text with `\n\n` (double newlines) between paragraphs preserves formatting perfectly
- ✅ `x_studio_manual_sms_override` field on `sale.order` retains all line breaks when written via API
- ✅ User can copy/paste from field, edit, and formatting survives round-trip
- ❌ HTML formatting (e.g., `<br/>`, `<p>`, `pre-wrap`) NOT needed for plain text fields
- ❌ Single `\n` may not render as line break in Odoo UI (use `\n\n` for paragraphs)

**Selection Field Values:**
- ✅ `x_studio_activelead` must be EXACT string: `"Do Not Contact"` (case and spacing matter)
- ❌ Don't use snake_case: `"do_not_contact"` will cause ValueError
- ❌ Don't use lowercase: `"do not contact"` will cause ValueError

**Field Locations:**
- ✅ `x_studio_manual_sms_override` lives on `sale.order` (NOT `crm.lead`)
- ✅ User edits via "SMS Text Modified" tab on sale.order form view
- ✅ Field is visible even if empty (user can paste directly into it)

### Phase 2 Reactivation (Status - 2026-03-16):
1. **Opportunity creation:** ✅ Working (creates CRM opportunity with expected revenue)
2. **Historical job fetch:** ✅ Working (fetches from Workiz using correct API format)
3. **Graveyard job creation:** ✅ Working (creates unscheduled job in Workiz)
4. **Status update to trigger SMS:** ✅ Working (SubStatus = "API SMS Test Trigger")
5. **PREVIEW stage:** ✅ Working (composes SMS, writes to field, posts to chatter)
6. **LAUNCH stage:** ✅ Working (reads from field, sends via Workiz, updates property pricing)
7. **STOP protection:** ✅ Working (checks `phone_blacklisted` and `x_studio_activelead` before sending)
8. **Comprehensive logging:** All API requests/responses logged to Odoo chatter for troubleshooting

---

## 💡 SUGGESTED NEXT STEPS

### Immediate Priorities:
1. **Monitor Phase 5 alternating logic:** Test with multiple alternating customers to verify line items match job type
2. **Verify invoice Workiz link field:** Test that clicking link opens correct job
3. **Test Phase 6 → Phase 5 flow end-to-end:** Record payment → verify job created → check invoice field populated

### Short-Term Improvements:
1. **Add error handling:** Retry logic for API failures
2. **Add logging:** Structured logging to Zapier + external service (Sentry, CloudWatch)
3. **Performance monitoring:** Track Zapier task usage, API call duration
4. **User training:** Document 30-second manual workflow for Phase 5 line items

### Long-Term Enhancements:
- **Phase 7: Invoice Automation:** Sync invoices Odoo ↔ Workiz (currently payment only)
- **Phase 8: Analytics Dashboard:** Job completion metrics, revenue tracking, customer retention
- **Phase 9: Customer Portal:** Self-service booking, job history, invoice access
- **Phase 10: Advanced Routing:** Consider proximity to other jobs, Google Maps integration

### Maintenance Tasks:
- **Weekly:** Check Zapier logs for errors (first month)
- **Monthly:** Verify data accuracy spot checks, review error rates
- **Quarterly:** Update city routing if service areas change
- **As needed:** Add new custom fields to Phase 3/4 mappings when Odoo/Workiz updated

---

## 🔑 CREDENTIALS & ENDPOINTS

**Odoo:**
- URL: `https://window-solar-care.odoo.com/jsonrpc`
- Database: `window-solar-care`
- User ID: `2`
- API Key: `7e92006fd5c71e4fab97261d834f2e6004b61dc6`

**Workiz:**
- API Token: `api_1hu6lroiy5zxomcpptuwsg8heju97iwg`
- Auth Secret: `sec_334084295850678330105471548`
- Base URL: `https://api.workiz.com/api/v1/{API_TOKEN}/`

**Zapier Webhook URLs:**
- Phase 3 Webhook (for Phase 4 to call): `https://hooks.zapier.com/hooks/catch/9761276/ueyjr41/`
- Phase 5 Webhook (for Phase 6 to call): `https://hooks.zapier.com/hooks/catch/9761276/ue4o0az/`
- STOP Handler Webhook (Workiz STOP status): `https://hooks.zapier.com/hooks/catch/9761276/upyvrkx/`

**GitHub:**
- Repo: `windowandsolarcare-hash/Odoo-Migration`
- Branch: `main` (production, watched by Zapier)

---

## 🎓 BUSINESS CONTEXT

**Owner:** DJ Sanders  
**Business:** A Window & Solar Care  
**Services:** Window cleaning (inside & outside), solar panel cleaning  
**Service Area:** Coachella Valley, California (Palm Springs, Palm Desert, Indian Wells, La Quinta, Indio, Hemet)  
**Customer Base:** ~1,200 active customers, mix of maintenance contracts and on-demand

**Service Types:**
- **Maintenance:** Recurring contracts (3, 4, or 6 months frequency)
- **Alternating:** Inside & Outside alternates with Outside Only each visit
- **On Demand:** One-time service, follow up after 6 months
- **On Request:** Customer calls when needed, follow up after 6 months

**Pricing:**
- Base: $85-$145 depending on service
- Inflation: 5% annually (automated in Phase 2)
- Tips: Common ($10-$20)
- Payment: Cash, Check, Credit Card, Zelle

**Workflow:**
1. Customer books (phone, Calendly, or auto-scheduled)
2. Job created in Workiz → Phase 3 creates SO in Odoo
3. Job scheduled → Phase 4 confirms SO, creates task
4. Job completed → Tech marks Done in Workiz → Phase 4 updates SO
5. Customer pays → Phase 6 adds payment to Workiz, marks Done
6. Phase 6 triggers Phase 5 → Next job auto-created (Maintenance) OR reminder created (On Demand)

---

## 📝 COMMON DEBUGGING COMMANDS

**Check recent GitHub commits:**
```bash
gh api repos/windowandsolarcare-hash/Odoo-Migration/commits --jq '.[:5] | .[] | {sha: .sha[:7], message: .commit.message, date: .commit.author.date}'
```

**Fetch specific file from GitHub:**
```bash
gh api repos/windowandsolarcare-hash/Odoo-Migration/contents/2_Modular_Phase3_Components/zapier_phase5_FLATTENED_FINAL.py --jq '.download_url' | curl -s -L
```

**Rollback a file to previous commit:**
```bash
# Get file content from specific commit SHA
gh api repos/windowandsolarcare-hash/Odoo-Migration/contents/path/to/file.py?ref=COMMIT_SHA

# Then push back to main using normal github MCP commit
```

**Test Odoo API call:**
```python
import requests
payload = {"jsonrpc": "2.0", "method": "call", "params": {"service": "object", "method": "execute_kw", "args": [DB, USER_ID, API_KEY, "sale.order", "search_read", [[["x_studio_x_studio_workiz_uuid", "=", "UUID"]]], {"fields": ["name"], "limit": 1}]}}
r = requests.post(ODOO_URL, json=payload)
print(r.json())
```

**Test Workiz API call:**
```python
import requests
url = f"https://api.workiz.com/api/v1/{API_TOKEN}/job/get/{UUID}/?auth_secret={AUTH_SECRET}"
r = requests.get(url)
print(r.json())
```

---

## 🚨 STOP COMPLIANCE (SMS Opt-Out Handling)

**Status:** ✅ Fully Automated (Workiz → Zapier → Odoo)

### Architecture (Deployed 2026-03-16)

**Trigger:** Workiz webhook fires when job sub-status changes to "STOP - Do not Call or Text"

**Workflow:**
```
Workiz Webhook → Zapier Catch Hook → Execute GitHub code → Odoo API
```

**What Happens:**
1. Customer sends STOP reply to SMS
2. User changes job sub-status in Workiz to "STOP - Do not Call or Text"
3. Workiz webhook fires to Zapier: `https://hooks.zapier.com/hooks/catch/9761276/upyvrkx/`
4. Zapier parses payload (nested `clientInfo.serialId` and `primaryPhone`)
5. Executes `2_Modular_Phase3_Components/zapier_stop_handler.py` from GitHub
6. Script performs:
   - Formats phone to E.164 (e.g., `9514898621` → `+19514898621`)
   - Creates record in `phone.blacklist` model (auto-updates `phone_blacklisted` on contact)
   - Searches for contact by `x_studio_client_id` (Workiz `serialId`)
   - Updates contact: `x_studio_activelead` = `"Do Not Contact"`
   - Posts detailed timestamped message to contact's chatter with HTML formatting
7. Contact is now protected from ALL SMS (reactivation, marketing, etc.)

### Zapier Setup (Stop Handler)

**Zapier Step 1:** Webhooks by Zapier (Catch Hook)
- Webhook URL: `https://hooks.zapier.com/hooks/catch/9761276/upyvrkx/`
- Trigger: Workiz "Job Status Changed" → Sub-status = "STOP - Do not Call or Text"

**Zapier Step 2:** Code by Zapier (Run Python)
```python
import urllib.request

url = "https://raw.githubusercontent.com/windowandsolarcare-hash/Odoo-Migration/main/2_Modular_Phase3_Components/zapier_stop_handler.py"
code = urllib.request.urlopen(url).read().decode()

# Execute and capture output
exec_globals = {**globals(), 'input_data': input_data}
exec(code, exec_globals)

# Return the output from executed code
return exec_globals.get('output', {'status': 'error', 'message': 'No output generated'})
```

**Input Mappings (in Zapier UI):**
- `client_id`: `data__clientInfo__serialId` (nested path)
- `phone`: `data__clientInfo__primaryPhone`

### File: zapier_stop_handler.py

**Location:** `2_Modular_Phase3_Components/zapier_stop_handler.py`

**Key Functions:**
- `format_e164(phone)`: Converts US phone to E.164 format
- `add_to_blacklist(phone)`: Creates `phone.blacklist` record
- `update_contact_status(client_id, phone)`: Finds contact, updates `x_studio_activelead`, posts to chatter
- `post_to_chatter(contact_id, message)`: Posts HTML-formatted message with timestamp to contact

**Odoo API Gotchas:**
- `create()` requires: `[model, "create", [[{"field": "value"}]]]` (list of dicts)
- `write()` requires: `[model, "write", [[record_id], {"field": "value"}]]` (record IDs as list)
- `x_studio_activelead` must be EXACT string: `"Do Not Contact"` (case-sensitive)
- `phone.blacklist.number` must be E.164 format (e.g., `+19514898621`)

**Chatter Message Format:**
```html
<p><strong>🛑 STOP REQUEST RECEIVED</strong></p>
<ul>
<li><strong>Time:</strong> 2026-03-16 07:30:45 UTC</li>
<li><strong>Phone Blacklisted:</strong> +19514898621</li>
<li><strong>Status Changed:</strong> Active/Lead → Do Not Contact</li>
<li><strong>Source:</strong> Workiz webhook (via Zapier)</li>
</ul>
<p><em>This contact will no longer receive SMS messages (reactivation, marketing, etc.)</em></p>
```

### Reactivation Protection (Built-In)

**Both PREVIEW and LAUNCH scripts check STOP compliance:**

```python
# From ODOO_REACTIVATION_COMPLETE_NO_IMPORTS.py (lines 49-67)
if contact_vals.get('phone_blacklisted'):
    now_utc = datetime.now(timezone.utc)
    timestamp = now_utc.strftime("%Y-%m-%d %H:%M:%S UTC")
    source_order.message_post(body=f"⛔ **SKIP: Contact Blacklisted**\n\n{full_name} ({phone_sanitized})\n\nPhone is blacklisted (STOP request received)\nTime: {timestamp}\n\n*This contact will not receive SMS*")
    break

if contact_vals.get('x_studio_activelead') == "Do Not Contact":
    now_utc = datetime.now(timezone.utc)
    timestamp = now_utc.strftime("%Y-%m-%d %H:%M:%S UTC")
    source_order.message_post(body=f"⛔ **SKIP: Do Not Contact**\n\n{full_name} ({phone_sanitized})\n\nActive/Lead status: Do Not Contact\nTime: {timestamp}\n\n*This contact will not receive SMS*")
    break
```

**When contact is blacklisted:**
- ✅ PREVIEW/LAUNCH stop immediately
- ✅ No SMS composed or sent
- ✅ Timestamped message posted to opportunity chatter
- ✅ User sees exactly why contact was skipped

### Key Technical Learnings (2026-03-16)

**Odoo's `phone.blacklist` Model:**
- ✅ Standard Odoo model (no custom fields needed)
- ✅ Automatically updates `phone_blacklisted` field on `res.partner`
- ✅ Requires E.164 format phone numbers
- ✅ Creating record in `phone.blacklist` instantly blacklists the contact

**Field Format Discovery:**
- ❌ Initially tried `x_studio_stop_request_received` custom field (unnecessary)
- ❌ Initially tried `is_blacklisted` field (read-only, can't write to it)
- ✅ Final solution: Use `phone.blacklist` model + `x_studio_activelead` custom field

**Text Formatting in Odoo:**
- ✅ Plain text with double newlines (`\n\n`) between paragraphs renders correctly
- ✅ Field `x_studio_manual_sms_override` preserves all line breaks perfectly
- ❌ HTML formatting in chatter preview was not preferred (too complex to copy/paste)
- ✅ Final solution: Plain text format matches "old launch" code (working since 2025)

---

## 🎯 SESSION KICKOFF CHECKLIST

When starting a new Claude chat with this context:

1. **Read this file first** (CLAUDE_CONTEXT.md)
2. **Understand current state:** All 6 phases deployed and working
3. **Know the workflow:** Workiz (source) → Zapier (automation) → Odoo (business ops)
4. **Remember branch strategy:** Push directly to main (Zapier watches main only)
5. **Use `gh api` for GitHub:** PowerShell scripts, NOT git commands
6. **Testing workflow:** YOU create/cleanup test data via API (user never does this manually)
7. **Test scripts available:** `test_create_workiz_job.py`, `test_cleanup_workiz_job.py`, `test_cleanup_odoo_data.py`
8. **Document changes:** Update this file if architecture changes significantly

**CRITICAL TESTING RULE:**
When making code changes that need testing:
- ✅ YOU create test data via API (Workiz/Odoo)
- ✅ YOU cleanup test data via API
- ❌ User NEVER manually creates/deletes test data
- See `TEST_FRAMEWORK.md` for complete guide

---

**END OF CONTEXT**

**Last Updated:** 2026-03-16  
**Total Lines of Production Code:** ~5,400 (includes 2-stage reactivation + STOP handler)  
**Automation Coverage:** ~98% (manual only for Phase 5 line items + STOP status change in Workiz)  
**GitHub Repo:** windowandsolarcare-hash/Odoo-Migration  
**Primary Contact:** DJ Sanders (owner, developer)  

**Recent Major Changes:**
- **2026-03-16:** Phase 2 Reactivation - 2-stage workflow (PREVIEW writes to field, LAUNCH sends from field)
- **2026-03-16:** STOP Compliance - Fully automated via Zapier (Workiz webhook → phone.blacklist)
- **2026-03-16:** SMS text updated: "we'd like to schedule an appointment again!" (not "stop by")
- **2026-03-15:** Reactivation STOP checks - Respects `phone_blacklisted` and `x_studio_activelead`
- **2026-03-08:** Phase 2 Rewrite - Eliminated Zapier middleware, direct Odoo→Workiz API
- **2026-03-05:** Phase 5 alternating logic fix, Phase 6 check number sync, invoice Workiz link field
