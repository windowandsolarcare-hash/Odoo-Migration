# MASTER PROJECT CONTEXT
**Last Updated:** 2026-03-19
**Project:** Migration to Odoo (Workiz <-> Odoo Sync)
**Business:** A Window & Solar Care (DJ Sanders)

---

## 🛑 TECHNICAL BIBLE (READ THIS FIRST)

### 1. The "Golden" Rules
1.  **NO ZAPIER UI EDITS:** Code lives in GitHub `main`. Zapier fetches it dynamically.
2.  **ELIMINATE ZAPIER:** Future dev = Odoo Server Actions or Direct Webhooks.
3.  **NO IMPORTS IN ODOO:** Server Actions block `import`. Use pre-loaded `requests`, `datetime`, `json`.
4.  **TEST VIA API:** You create/cleanup your own test data. User does NOT do it manually.
5.  **GITHUB DEPLOY:** Use `gh api` to push to `main`. No `git` commands.
6.  **CHATTER AUDIT TRAIL:** ALL field changes/creates/updates must post to chatter with timestamp (format: `[YYYY-MM-DD HH:MM:SS] message`). Provides debugging + audit trail.
7.  **PROPERTY SEARCH:** Use `["x_studio_x_studio_record_category", "=", "Property"]` — NOT `["type", "=", "other"]`.
8.  **ODOO WEBHOOK PAYLOAD:** Always check `if isinstance(payload, str): payload = json.loads(payload)` — Odoo often passes payload as dict already.

### 2. "Golden" Custom Field Mappings
*Use these EXACT technical names. They are case-sensitive.*

| Human Name | Model | Technical Name | Notes |
| :--- | :--- | :--- | :--- |
| **Workiz UUID** | Sale Order | `x_studio_x_studio_workiz_uuid` | Unique Key |
| **Workiz Link** | Sale Order | `x_studio_x_workiz_link` | |
| **Workiz Link** | Invoice | `x_studio_workiz_job_link` | Note difference from SO |
| **Workiz Tech** | Sale Order | `x_studio_x_studio_workiz_tech` | |
| **Gate Code** | Sale Order | `x_studio_x_gate_snapshot` | Snapshot at time of job |
| **Gate Code** | Contact | `x_studio_x_gate_code` | Master record |
| **Pricing** | Sale Order | `x_studio_x_studio_pricing_snapshot` | Snapshot |
| **Pricing** | Contact | `x_studio_x_pricing` | Master record |
| **Job Type** | Sale Order | `x_studio_x_studio_x_studio_job_type` | |
| **Frequency** | Contact | `x_studio_x_frequency` | e.g. "3 Months" |
| **Alternating** | Contact | `x_studio_x_alternating` | "Yes" or "No" |
| **Service Area** | Contact | `x_studio_x_studio_service_area` | |
| **Workiz ID** | Contact | `ref` | Stores "1234" (ClientId) |
| **Location ID** | Contact | `x_studio_x_studio_location_id` | Workiz serialId / ClientId (numeric) |
| **Record Category** | Contact | `x_studio_x_studio_record_category` | "Property" for property records |
| **Last Property Visit** | Contact | `x_studio_x_studio_last_property_visit` | Date of last visit to this property |
| **Last Visit All** | Contact | `x_studio_last_visit_all_properties` | Last visit across all properties |
| **Active/Lead** | Contact | `x_studio_activelead` | "Do Not Contact" (exact case) |
| **SMS Override** | Sale Order | `x_studio_manual_sms_override` | Reactivation SMS text (plain text, `\n\n` for paragraphs) |
| **CRM Activity Log** | Contact | `x_crm_activity_log_ids` | Activity log entries |
| **Prices Per Service** | Contact | `x_studio_prices_per_service` | Pricing menu per service type |
| **Last Reactivation** | Contact | `x_studio_last_reactivation_sent` | 90-day cooldown timestamp |
| **Graveyard UUID** | Opportunity | `x_workiz_graveyard_uuid` | Workiz UUID of graveyard job |
| **Graveyard Link** | Opportunity | `x_workiz_graveyard_link` | URL to graveyard job in Workiz |
| **Historical UUID** | Opportunity | `x_historical_workiz_uuid` | UUID from historical migration |
| **Historical Link** | Opportunity | `x_studio_x_historical_workiz_link` | URL to historical job |
| **Odoo Contact ID** | Opportunity | `x_odoo_contact_id` | Linked res.partner ID |

**Selection values:** `x_studio_activelead` = `"Do Not Contact"` (exact case)

### 3. "Golden" API Syntax

#### **A. Odoo Server Action (NO IMPORTS)**
```python
# CORRECT - Use pre-loaded libraries
payload = {
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "service": "object",
        "method": "execute_kw",
        "args": [env.cr.dbname, env.uid, "YOUR_API_KEY", "res.partner", "search_read", [[["name", "=", "Test"]]], {"fields": ["id"]}]
    }
}
response = requests.post("https://window-solar-care.odoo.com/jsonrpc", json=payload)
result = response.json().get("result")
```

#### **B. Workiz API (Job Create)**
```python
url = f"https://api.workiz.com/api/v1/{API_TOKEN}/job/create/"
data = {
    "auth_secret": AUTH_SECRET,
    "ClientId": "1234",
    "JobDateTime": "2026-03-20 08:00:00", # Pacific Time - OMIT for unscheduled
    "JobType": "Window Cleaning",
    "ServiceArea": "desert", # Required for routing
    "next_job_line_items": "..." # Custom field for line items
}
# Returns list [{UUID: '...', ...}] or HTTP 204
requests.post(url, json=data)
```

**Workiz field validation defaults (use these to avoid API errors):**
- `JobSource` = `"Referral"` (NOT "Reactivation")
- `type_of_service` = `"On Request"` (NOT empty string)
- `frequency` = `"Unknown"` (NOT empty string)
- `confirmation_method` = `"Cell Phone"` (NOT empty string)
- All string fields: must be `str()` — reject `None` or numbers

#### **CRITICAL: Workiz Status vs SubStatus Structure**
**THIS IS FUNDAMENTAL - ALL AGENTS MUST KNOW THIS:**

Workiz has only **5 main Status values:**
1. `Submitted`
2. `Pending`
3. `In Progress`
4. `Canceled`
5. `Done`

**ALL other statuses are stored in `SubStatus` field with Status = "Pending"**

Examples:
- "Next Appointment - Text" → Status="Pending", SubStatus="Next Appointment - Text"
- "Send Confirmation - Text" → Status="Pending", SubStatus="Send Confirmation - Text"
- "Scheduled" → Status="Pending", SubStatus="Scheduled"
- "Lead" → Status="Pending", SubStatus="Lead"
- "STOP - Do not Call or Text" → Status="Pending", SubStatus="STOP - Do not Call or Text"

**RULE:** When checking job status conditions, ALWAYS check BOTH `Status` AND `SubStatus` fields!

```python
# WRONG - only checks Status
if job['Status'] == 'Next Appointment - Text':
    # This will NEVER match!

# CORRECT - checks SubStatus
if job['SubStatus'] == 'Next Appointment - Text':
    # This works!
```

#### **C. Chatter Logging (Audit Trail)**
```python
# NOTE: datetime is pre-loaded in Odoo safe_eval - no import needed in Server Actions
# In Zapier Python steps, import normally

# Post to Sale Order chatter
def post_chatter_message(so_id, message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message_with_timestamp = f"[{timestamp}] {message}"
    payload = {
        "jsonrpc": "2.0", "method": "call",
        "params": {
            "service": "object", "method": "execute_kw",
            "args": [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, "sale.order", "message_post", [so_id], {"body": message_with_timestamp}]
        }
    }
    requests.post(ODOO_URL, json=payload, timeout=10)

# Post to Opportunity chatter
def post_opportunity_chatter(opp_id, message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message_with_timestamp = f"[{timestamp}] {message}"
    payload = {
        "jsonrpc": "2.0", "method": "call",
        "params": {
            "service": "object", "method": "execute_kw",
            "args": [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, "crm.lead", "message_post", [opp_id], {"body": message_with_timestamp}]
        }
    }
    requests.post(ODOO_URL, json=payload, timeout=10)

# RULE: Always post to chatter when changing fields for audit trail
```

#### **D. Odoo Webhook Code Rules**
Webhooks run in Odoo's safe_eval — stricter than Server Actions:
```python
# MUST check payload type - Odoo sometimes passes dict, sometimes string
if isinstance(payload, str):
    payload = json.loads(payload)

# NEVER use triple-quote docstrings - creates __doc__ (forbidden name)
# Use # comments only

# NEVER use env.user.message_post() - res.users has no message_post
# Remove all logging that uses this

# Write activity log entries via:
contact.write({"x_crm_activity_log_ids": [[0, 0, activity_vals]]})

# Write marketing blacklist via:
contact.write({'is_blacklisted': True})
```

---

## 🚫 APPROACHES THAT FAILED

| Approach | Error | Fix |
| :--- | :--- | :--- |
| `import urllib.request` in Odoo | forbidden opcode IMPORT_NAME | Odoo blocks ALL imports |
| `exec(code)` from GitHub in Odoo | forbidden opcode | Odoo safe_eval blocks exec |
| Triple-quote docstring in Odoo | Access to forbidden name __doc__ | Use # comments only |
| `env.user.message_post()` in webhook | res.users has no message_post | Remove all logging |
| `json.loads(payload)` when payload is dict | TypeError: must be str | `if isinstance(payload, str): payload = json.loads(payload)` |
| `["type", "=", "other"]` for properties | Wrong results | Use `["x_studio_x_studio_record_category", "=", "Property"]` |
| `JobSource = "Reactivation"` | Workiz validation error | Use `"Referral"` |
| `type_of_service = ""` | Workiz validation error | Use `"On Request"` |
| `frequency = ""` | Workiz validation error | Use `"Unknown"` |
| `confirmation_method = ""` | Workiz validation error | Use `"Cell Phone"` |

---

## 🛑 STOP COMPLIANCE (TWO IMPLEMENTATIONS)

### Implementation A: Zapier (zapier_stop_handler.py)
- **Trigger:** Workiz webhook → Zapier → `2_Modular_Phase3_Components/zapier_stop_handler.py`
- **URL:** `https://hooks.zapier.com/hooks/catch/9761276/upyvrkx/`
- **Uses:** `phone.blacklist` model, `x_studio_activelead` = "Do Not Contact", `ref` field for client lookup

### Implementation B: Odoo Webhook (odoo_webhook_stop_handler.py)
- **Trigger:** Workiz sends DIRECTLY to Odoo
- **URL:** `https://window-solar-care.odoo.com/web/hook/f64d0bc1-54fd-45a1-b645-0dcae6ae1728`
- **File:** `1_Production_Code/odoo_webhook_stop_handler.py`

**Workiz config:** Filter on `SubStatus = "STOP - Do not Call or Text"` (NOT Status — Status stays "Pending")

**Payload format Workiz sends:**
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

**Contact lookup:** `x_studio_x_studio_location_id` = `clientInfo.serialId`, OR fall back to phone search.

---

## 📂 PROJECT STRUCTURE

### `1_Production_Code/` (The Active Core)
*These scripts run the entire business. Touch with care.*
- `zapier_phase3_FLATTENED_FINAL.py` — New Job: Workiz → Odoo
- `zapier_phase4_FLATTENED_FINAL.py` — Updates: Workiz → Odoo
- `zapier_phase5_FLATTENED_FINAL.py` — Scheduling: Odoo → Workiz
- `zapier_phase6_FLATTENED_FINAL.py` — Payments: Odoo → Workiz
- `ODOO_REACTIVATION_PREVIEW.py` — Reactivation: composes SMS, writes to field
- `ODOO_REACTIVATION_COMPLETE_NO_IMPORTS.py` — Reactivation: sends SMS, creates graveyard job
- `odoo_webhook_stop_handler.py` — STOP Compliance (Odoo direct webhook)
- `zapier_calendly_booking_FLATTENED_FINAL.py` — Calendly booking sync

### `2_Modular_Phase3_Components/`
- `zapier_stop_handler.py` — STOP Compliance (Zapier implementation)

### `2_Testing_Tools/`
*Use these to verify your changes.*
- `test_create_workiz_job.py`
- `test_cleanup_workiz_job.py`
- `test_cleanup_odoo_data.py`
- `TEST_FRAMEWORK.md`

### `3_Documentation/`
- `AI_Agent_Master_Manual_OPTIMIZED.docx`
- `BUSINESS_WORKFLOW.md`

### `z_ARCHIVE_DEPRECATED/`
Old scripts, "Part 1/2/3" files, and previous experiments.

---

## 🔄 CURRENT SYSTEM STATUS

| Phase | Function | Status | Trigger |
| :--- | :--- | :--- | :--- |
| **1** | History Migration | ✅ Done | N/A |
| **2** | Reactivation | ✅ Active | Odoo Server Action (Manual) |
| **2B** | STOP Compliance | ✅ Two implementations | Workiz Webhook |
| **3** | New Job Sync | ✅ Active | Workiz Webhook → Zapier |
| **4** | Job Updates | ✅ Active | Zapier Polling (5 min) |
| **5** | Auto-Schedule | ✅ Active | Triggered by Phase 6 |
| **6** | Payment Sync | ✅ Active | Odoo Webhook → Zapier |

### Unfinished / Roadmap
1. **Auto-close Reactivation Opportunities** — When graveyard job goes to Scheduled, mark Opportunity Won, create SO
2. **Missing Location IDs** — Some contacts missing `x_studio_x_studio_location_id` (breaks STOP lookup by ClientId)

---

## 🚀 STRATEGIC GOALS
1.  **Eliminate Zapier:** Move logic to Odoo Server Actions or direct Python scripts.
2.  **STOP Compliance:** Automate "STOP" replies to update Odoo `is_blacklisted`.
3.  **Stability:** Reduce "moving parts" by consolidating code.

---

## 🔑 CREDENTIALS (SHORT)
- **Odoo:** User ID `2`, DB `window-solar-care`, URL `window-solar-care.odoo.com`
- **Workiz:** API Token `api_1hu6lroiy5zxomcpptuwsg8heju97iwg`, Auth `sec_334084295850678330105471548`
- **GitHub:** `windowandsolarcare-hash/Odoo-Migration` (Branch: `main`)
