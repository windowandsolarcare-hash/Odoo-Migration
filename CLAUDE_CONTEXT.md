# CLAUDE_CONTEXT.md
**Last Updated:** 2026-03-19  
**Purpose:** Complete project context for new AI chat sessions (Claude Code)  
**Business:** A Window & Solar Care (DJ Sanders, Owner)

---

## CRITICAL: READ THIS FIRST

**Read this file AND `MASTER_PROJECT_CONTEXT.md` at the start of every session.** This file covers phase status, field names, API endpoints, and known fixes. MASTER_PROJECT_CONTEXT.md is the Technical Bible.

---

## PROJECT OVERVIEW

**Goal:** Bi-directional real-time sync between Workiz (field service) and Odoo (business operations).

**Strategic Direction:** ELIMINATE ZAPIER. Prioritize direct Odoo integrations over Zapier middleware.

**Tech Stack:**
- **Workiz:** Source of truth for jobs, customers, scheduling
- **Odoo:** CRM, invoicing, reactivation campaigns
- **Zapier:** Automation layer (webhooks + Python code steps) - Phases 3, 4, 5, 6
- **GitHub:** windowandsolarcare-hash/Odoo-Migration (main branch only)

**CRITICAL: We use `gh` (GitHub CLI), NOT `git` commands! Push directly to main!**

---

## ALL PHASES STATUS

| Phase | Purpose | Trigger | Status | File |
|-------|---------|---------|--------|------|
| **1** | Historical Migration | One-time | Complete | N/A |
| **2** | Dormant Reactivation | Odoo Server Action | Deployed | ODOO_REACTIVATION_*.py |
| **2B** | STOP Compliance | Workiz Webhook | Two Implementations | See STOP section |
| **3** | New Job Creation | Workiz Webhook | Deployed | zapier_phase3_FLATTENED_FINAL.py |
| **4** | Job Status Updates | Zapier Polling | Deployed | zapier_phase4_FLATTENED_FINAL.py |
| **5** | Auto Job Scheduling | Phase 6 Trigger | Deployed | zapier_phase5_FLATTENED_FINAL.py |
| **6** | Payment Sync | Odoo Webhook | Deployed | zapier_phase6_FLATTENED_FINAL.py |

---

## PHASE 1: Historical Migration
- 6 years of Workiz data migrated to Odoo
- Reference: `Workiz_6Year_Done_History_Master.csv`
- External ID pattern: `workiz_[id]`

---

## PHASE 2: Reactivation Engine

**Status:** Deployed (2-stage: PREVIEW + LAUNCH)

**Files:**
- `1_Production_Code/ODOO_REACTIVATION_PREVIEW.py` - Composes SMS, writes to field
- `1_Production_Code/ODOO_REACTIVATION_COMPLETE_NO_IMPORTS.py` - Sends SMS, creates graveyard job

**Workflow:**
1. User selects Sale Order(s) → Runs PREVIEW
2. PREVIEW writes SMS to `x_studio_manual_sms_override` on sale.order
3. User can edit in "SMS Text Modified" tab
4. User clicks LAUNCH → Reads field, sends via Workiz API
5. LAUNCH creates graveyard job, updates status to trigger SMS
6. Links Opportunity to graveyard: `x_workiz_graveyard_uuid`, `x_workiz_graveyard_link`

**Key Fields:**
- `x_studio_manual_sms_override` (sale.order) - SMS text, plain text with `\n\n` for paragraphs
- `x_studio_last_reactivation_sent` (res.partner) - Cooldown (90 days)
- `x_studio_prices_per_service` (res.partner property) - Pricing menu
- `x_odoo_contact_id`, `x_historical_workiz_uuid`, `x_studio_x_historical_workiz_link` (crm.lead)
- `x_workiz_graveyard_uuid`, `x_workiz_graveyard_link` (crm.lead)

**CRM Activity Log Format (restored 2026-03-18):**
```python
activity_data = {
    "x_name": f"{campaign_name} | {current_date_display} | Job #{source_order.name} | {primary_service_str}",
    "x_description": message_body,  # Actual SMS sent
    "x_related_order_id": int(source_order.id),
    "x_contact_id": int(contact.id),
    "x_campaign_id": campaign_id
}
```

**Price Engine:**
- Add-ons (base_price < $70): No inflation, no $85 minimum
- Solar: Flat price
- Regular: 5% annual inflation + $85 minimum

**STOP Compliance:**
- Skips if `phone_blacklisted` OR `x_studio_activelead` == "Do Not Contact"

**Workiz API:**
- Token in URL: `https://api.workiz.com/api/v1/{API_TOKEN}/`
- Job create: Omit `JobDateTime` for unscheduled
- Status update: `SubStatus = "API SMS Test Trigger"` triggers SMS
- Wait 3 seconds after create before status update

**Deployment:** Copy/paste from GitHub into Odoo Server Action UI. No API access to update.

---

## PHASE 3: New Job Creation

**Trigger:** Workiz "New Job Created" webhook
**File:** `1_Production_Code/zapier_phase3_FLATTENED_FINAL.py`

**Zapier Code Step:**
```python
import urllib.request
url = "https://raw.githubusercontent.com/windowandsolarcare-hash/Odoo-Migration/main/1_Production_Code/zapier_phase3_FLATTENED_FINAL.py"
code = urllib.request.urlopen(url).read().decode()
exec_globals = {**globals(), 'input_data': input_data}
exec(code, exec_globals)
return exec_globals.get('output', {'status': 'error', 'message': 'No output generated'})
```

**Paths:** A (SO only), B (Property + SO), C (Contact + Property + SO)
**Filter:** Skip "Reactivation Lead" job type (graveyard jobs)

---

## PHASE 4: Job Status Updates

**Trigger:** Zapier "Updated Job in Workiz" (polling every 1-5 min)
**File:** `1_Production_Code/zapier_phase4_FLATTENED_FINAL.py`

**Zapier Webhook (4B):** Workiz "Job Status Changed" → Same URL as Phase 4 polling

**Key Fixes (2026-03-18):**
- Property search: `["x_studio_x_studio_record_category", "=", "Property"]` NOT `["type", "=", "other"]`
- Race condition: Only update `x_studio_x_studio_last_property_visit` if new date is newer or current is empty

**Unfinished:** Auto-close Reactivation Opportunities when graveyard job goes to Scheduled (find_opportunity_by_graveyard_uuid, mark_opportunity_won)

---

## PHASE 5: Auto Job Scheduling

**Trigger:** Phase 6 webhook
**File:** `1_Production_Code/zapier_phase5_FLATTENED_FINAL.py`

**Key Fixes (2026-03-18):**
- `calculate_next_service_date(base_date)` - Use completed job date, NOT datetime.now()
- `last_date_cleaned` populated on new maintenance jobs from JobDateTime

**Paths:** 5A Maintenance (create Workiz job), 5B On Demand (create Odoo activity)

---

## PHASE 6: Payment Sync

**Trigger:** Odoo "New Payment" webhook
**File:** `1_Production_Code/zapier_phase6_FLATTENED_FINAL.py`

**Flow:** Payment → Invoice → SO → Workiz UUID → Add payment → Mark Done → Trigger Phase 5

---

## STOP COMPLIANCE (TWO IMPLEMENTATIONS)

### Implementation A: Zapier (zapier_stop_handler.py)
**Trigger:** Workiz webhook → Zapier → `2_Modular_Phase3_Components/zapier_stop_handler.py`
**URL:** `https://hooks.zapier.com/hooks/catch/9761276/upyvrkx/`
**Uses:** `phone.blacklist` model, `x_studio_activelead` = "Do Not Contact", `ref` field for client lookup

### Implementation B: Odoo Webhook (odoo_webhook_stop_handler.py)
**Trigger:** Workiz sends DIRECTLY to Odoo
**URL:** `https://window-solar-care.odoo.com/web/hook/f64d0bc1-54fd-45a1-b645-0dcae6ae1728`
**File:** `1_Production_Code/odoo_webhook_stop_handler.py`

**Workiz Configuration:** Must filter on `SubStatus = "STOP - Do not Call or Text"` (NOT Status - Status stays "Pending")

**Payload Format (NEW - Workiz sends):**
```json
{
  "data": {
    "uuid": "B6GB1D",
    "clientInfo": {
      "serialId": 1040,
      "firstName": "Jean",
      "lastName": "Faenza",
      "primaryPhone": "8058131909"
    }
  }
}
```

**Odoo Webhook Code MUST:**
- NO docstrings (triple quotes) - creates __doc__ forbidden
- NO `env.user.message_post` - res.users has no message_post
- `if isinstance(payload, str): payload = json.loads(payload)` - Odoo often provides dict already
- Use `contact.write({'is_blacklisted': True})` for marketing blacklist
- Use `contact.write({"x_crm_activity_log_ids": [[0, 0, activity_vals]]})` for activity log

**Contact lookup:** `x_studio_x_studio_location_id` = clientInfo.serialId, OR phone search

---

## APPROACHES THAT FAILED

| Approach | Error | Fix |
|----------|-------|-----|
| `import urllib.request` in Odoo | forbidden opcode IMPORT_NAME | Odoo blocks ALL imports |
| `exec(code)` from GitHub in Odoo | forbidden opcode | Odoo safe_eval blocks exec |
| Triple-quote docstring in Odoo | Access to forbidden name __doc__ | Use # comments only |
| `env.user.message_post()` in webhook | res.users has no message_post | Remove all logging |
| `json.loads(payload)` when payload is dict | TypeError: must be str | `if isinstance(payload, str): payload = json.loads(payload)` |
| `["type", "=", "other"]` for properties | Wrong property type | Use `["x_studio_x_studio_record_category", "=", "Property"]` |
| JobSource = "Reactivation" | Workiz validation error | Use "Referral" |
| type_of_service = "" | Workiz validation | Use "On Request" |
| frequency = "" | Workiz validation | Use "Unknown" |
| confirmation_method = "" | Workiz validation | Use "Cell Phone" |

---

## WORKIZ API QUIRKS

- **ClientId:** Use numeric (e.g., 1040) not "CL-xxx" format
- **JobDateTime:** Omit for unscheduled jobs
- **LineItems:** Cannot add via API - store in custom field, user adds manually
- **Status vs SubStatus:** SubStatus holds "Scheduled", "STOP - Do not Call or Text", etc.
- **String fields:** All must be str() - Unit, JobSource, etc. reject None/numbers
- **Job create response:** Returns list `[{UUID: '...', ...}]` or HTTP 204

---

## ODOO CUSTOM FIELD NAMES (EXACT)

| Purpose | Model | Field Name |
|---------|-------|------------|
| Workiz UUID | sale.order | x_studio_x_studio_workiz_uuid |
| Workiz Link | sale.order | x_studio_x_workiz_link |
| Workiz Link | account.move | x_studio_workiz_job_link |
| Graveyard UUID | crm.lead | x_workiz_graveyard_uuid |
| Graveyard Link | crm.lead | x_workiz_graveyard_link |
| Historical UUID | crm.lead | x_historical_workiz_uuid |
| Historical Link | crm.lead | x_studio_x_historical_workiz_link |
| Location ID | res.partner | x_studio_x_studio_location_id |
| Record Category | res.partner | x_studio_x_studio_record_category |
| Last Property Visit | res.partner | x_studio_x_studio_last_property_visit |
| Last Visit All | res.partner | x_studio_last_visit_all_properties |
| Active/Lead | res.partner | x_studio_activelead |
| SMS Override | sale.order | x_studio_manual_sms_override |
| CRM Activity | res.partner | x_crm_activity_log_ids |
| Prices Per Service | res.partner | x_studio_prices_per_service |

**Selection values:** `x_studio_activelead` = "Do Not Contact" (exact case)

---

## ZAPIER EXEC() PATTERN

```python
import urllib.request
url = "https://raw.githubusercontent.com/windowandsolarcare-hash/Odoo-Migration/main/1_Production_Code/zapier_phaseX_FLATTENED_FINAL.py"
code = urllib.request.urlopen(url).read().decode()
exec_globals = {**globals(), 'input_data': input_data}
exec(code, exec_globals)
return exec_globals.get('output', {'status': 'error', 'message': 'No output generated'})
```

**Critical:** Code lives in GitHub. Zapier fetches on EVERY run. Push to main = instant deploy.

---

## GITHUB DEPLOYMENT

**Use `gh api` NOT git. Claude Code runs bash, so use the bash version below (NOT PowerShell).**

```bash
repo="windowandsolarcare-hash/Odoo-Migration"
filePath="1_Production_Code/example.py"
sha=$(gh api "repos/$repo/contents/$filePath" --jq '.sha' 2>/dev/null)

/c/Python314/python -c "
import json, base64
with open(r'C:/Users/dj/Documents/Business/A Window and Solar Care/Migration to Odoo/$filePath', 'rb') as f:
    content = base64.b64encode(f.read()).decode()
payload = {
    'message': 'YYYY-MM-DD | filename | description',
    'content': content,
    'sha': '$sha',
    'branch': 'main'
}
print(json.dumps(payload))
" | gh api "repos/$repo/contents/$filePath" --method PUT --input -
```

**Notes:**
- Python executable: `/c/Python314/python`
- Commit message format: `YYYY-MM-DD | filename | description`
- Always push to `main` — Zapier watches main only

---

## CONTACT LINK ON SALE ORDER

**Solution:** Odoo Studio Related Field
- Path: `partner_shipping_id.parent_id`
- Creates clickable link to Contact (with smart buttons)
- No code changes, no backfill

---

## FILE STRUCTURE

```
1_Production_Code/
├── ODOO_REACTIVATION_PREVIEW.py
├── ODOO_REACTIVATION_COMPLETE_NO_IMPORTS.py
├── odoo_webhook_stop_handler.py
├── zapier_phase3_FLATTENED_FINAL.py
├── zapier_phase4_FLATTENED_FINAL.py
├── zapier_phase5_FLATTENED_FINAL.py
├── zapier_phase6_FLATTENED_FINAL.py
└── zapier_calendly_booking_FLATTENED_FINAL.py

2_Modular_Phase3_Components/
└── zapier_stop_handler.py  (Zapier STOP - uses ref, phone.blacklist)

2_Testing_Tools/
├── test_create_workiz_job.py
├── test_cleanup_workiz_job.py
├── test_cleanup_odoo_data.py
└── check_*.py (diagnostic scripts)
```

---

## ROADMAP / UNFINISHED

1. ~~**Auto-close Reactivation Opportunities**~~ - **DONE** (Phase 4, lines 2289-2354). Detects when graveyard job JobType changes from "Reactivation Lead" + job is scheduled → marks Opportunity Won automatically.
2. **Odoo STOP webhook** - Ensure Workiz configured to send to Odoo URL; verify blacklisting works
3. **Missing Location IDs** - Some contacts missing x_studio_x_studio_location_id (breaks STOP lookup by ClientId)
4. **Orphaned future jobs** - Decision: Leave alone (no auto-delete)

---

## CREDENTIALS

**Odoo:** window-solar-care.odoo.com, DB: window-solar-care, API Key in `.cursorrules` (legacy — kept for reference)
**Workiz:** API Token api_1hu6lroiy5zxomcpptuwsg8heju97iwg, Auth sec_334084295850678330105471548  
**GitHub:** windowandsolarcare-hash/Odoo-Migration, main branch

---

## TESTING RULE

**YOU create and cleanup ALL test data via API.** User never manually creates/deletes. Use test_create_workiz_job.py, test_cleanup_workiz_job.py, test_cleanup_odoo_data.py.

---

**END OF CONTEXT**
