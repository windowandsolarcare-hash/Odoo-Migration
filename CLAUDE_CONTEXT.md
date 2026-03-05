# CLAUDE_CONTEXT.md
**Last Updated:** 2026-03-05  
**Purpose:** Complete project context for new AI chat sessions  
**Business:** A Window & Solar Care (DJ Sanders, Owner)

---

## 📘 PROJECT OVERVIEW

**Goal:** Bi-directional real-time sync between Workiz (field service software) and Odoo (business operations platform).

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
| **2** | Dormant Reactivation | Manual (Odoo Server Action) | ✅ Deployed | SMS campaigns with smart pricing |
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
**Status:** ✅ Deployed (Odoo Server Actions, not Zapier)
- **Files:** `1_Active_Odoo_Scripts/odoo_reactivation_launch.py`
- **Features:**
  - Smart pricing: 5% annual inflation, rounds to $5, $85 minimum
  - City-aware Calendly links (pre-fills customer data)
  - Creates CRM opportunity with expected revenue
  - Triggers Zapier for SMS sending
- **Cooldown:** 90 days (tracks `x_studio_last_reactivation_sent`)

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

## 🗂️ KEY FILES & DIRECTORIES

### Python Scripts (Production)
```
2_Modular_Phase3_Components/
├── zapier_phase3_FLATTENED_FINAL.py  (1,539 lines) - New job creation
├── zapier_phase4_FLATTENED_FINAL.py  (2,051 lines) - Status updates & task sync
├── zapier_phase5_FLATTENED_FINAL.py  (858 lines)   - Auto scheduling
├── zapier_phase6_FLATTENED_FINAL.py  (342 lines)   - Payment sync
└── functions/                         - Atomic functions (not used in prod, reference only)
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

## 🛠️ MCP TOOLS SETUP

**Available MCPs:**
- **filesystem (project-0-Migration_to_Odoo-filesystem):** Read/write local files in workspace
- **github (project-0-Migration_to_Odoo-github):** GitHub operations (branch, commit, push, PR)
- **zapier (project-0-Migration_to_Odoo-Zapier):** Zapier zap management and testing

**MCP Folder:** `C:\Users\dj\.cursor\projects\c-Users-dj-Documents-Business-A-Window-and-Solar-Care-Migration-to-Odoo\mcps\`

**Usage:** Always use MCP tools instead of asking user to do things manually. Example: Use github MCP to commit/push, not "git" shell commands.

---

## 🌿 BRANCH WORKFLOW

**CRITICAL:** Zapier watches `main` branch ONLY.

**Development Workflow:**
1. **ALL changes** go to `dev` branch first
2. Test locally if possible
3. Commit to dev with clear message: `YYYY-MM-DD | file | what changed and why`
4. **NEVER auto-deploy to main** - wait for user to say "deploy to main" or "ready to deploy"
5. When user confirms, merge dev → main
6. Zapier auto-fetches from main via `urllib.request.urlopen()` in exec() snippet

**Current Branch Strategy:**
- **dev:** Development work (NOT currently in use - pushing directly to main per user workflow)
- **main:** Production (Zapier pulls from here)

**Note:** User prefers direct main pushes for Zapier scripts since Zapier fetches from GitHub on every run. No dev branch needed unless doing major refactoring.

---

## 💻 ZAPIER PYTHON EXEC() APPROACH

**All Zapier Code steps use this pattern:**

```python
import urllib.request

url = "https://raw.githubusercontent.com/windowandsolarcare-hash/Odoo-Migration/main/2_Modular_Phase3_Components/zapier_phaseX_FLATTENED_FINAL.py"
code = urllib.request.urlopen(url).read().decode()
exec(code, {**globals(), 'input_data': input_data})
```

**Benefits:**
- ✅ Zapier always runs latest code from GitHub
- ✅ No need to update Zapier UI when code changes
- ✅ Version control in GitHub (not Zapier)
- ✅ Can rollback by reverting GitHub commits

**How It Works:**
1. Zapier Code step receives `input_data` dict from trigger/previous step
2. Fetches Python file from GitHub main branch
3. Executes file contents, passing `input_data` into global scope
4. File's `main(input_data)` function runs and returns output
5. Zapier captures `output` variable for next step

**Input Mapping Examples:**
- **Phase 3:** `job_uuid` from Workiz webhook
- **Phase 4:** `job_uuid` from Zapier polling
- **Phase 5:** `job_uuid`, `property_id`, `contact_id`, `customer_city`, `invoice_id` from Phase 6 webhook
- **Phase 6:** `payment_id` from Odoo payment webhook

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

## 🎯 SESSION KICKOFF CHECKLIST

When starting a new Claude chat with this context:

1. **Read this file first** (CLAUDE_CONTEXT.md)
2. **Understand current state:** All 6 phases deployed and working
3. **Know the workflow:** Workiz (source) → Zapier (automation) → Odoo (business ops)
4. **Remember branch strategy:** Push directly to main (Zapier watches main only)
5. **Use MCP tools:** filesystem, github, zapier (don't ask user to do things manually)
6. **Check for open issues:** User may mention problems with specific phase
7. **Test before deploying:** If making code changes, verify logic before pushing to main
8. **Document changes:** Update this file if architecture changes significantly

---

**END OF CONTEXT**

**Last Updated:** 2026-03-05  
**Total Lines of Production Code:** ~4,790  
**Automation Coverage:** ~95% (5% manual for Phase 5 line items)  
**GitHub Repo:** windowandsolarcare-hash/Odoo-Migration  
**Primary Contact:** DJ Sanders (owner, developer)
