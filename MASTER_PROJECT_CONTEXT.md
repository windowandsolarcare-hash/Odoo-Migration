# MASTER PROJECT CONTEXT
**Last Updated:** 2026-03-15
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
    "JobDateTime": "2026-03-20 08:00:00", # Pacific Time
    "JobType": "Window Cleaning",
    "ServiceArea": "desert", # Required for routing
    "next_job_line_items": "..." # Custom field for line items
}
# Returns 204 (No Content) or 200 (with data)
requests.post(url, json=data)
```

---

## 📂 PROJECT STRUCTURE (REORGANIZED)

### `1_Production_Code/` (The Active Core)
*These 6 scripts run the entire business. Touch with care.*
*   `zapier_phase3_FLATTENED_FINAL.py` (New Job: Workiz -> Odoo)
*   `zapier_phase4_FLATTENED_FINAL.py` (Updates: Workiz -> Odoo)
*   `zapier_phase5_FLATTENED_FINAL.py` (Scheduling: Odoo -> Workiz)
*   `zapier_phase6_FLATTENED_FINAL.py` (Payments: Odoo -> Workiz)
*   `ODOO_REACTIVATION_COMPLETE_NO_IMPORTS.py` (Reactivation Engine)
*   `odoo_webhook_stop_handler.py` (STOP Compliance - *In Progress*)

### `2_Testing_Tools/`
*Use these to verify your changes.*
*   `test_create_workiz_job.py`
*   `test_cleanup_workiz_job.py`
*   `test_cleanup_odoo_data.py`

### `3_Documentation/`
*   `AI_Agent_Master_Manual_OPTIMIZED.docx`
*   `BUSINESS_WORKFLOW.md`

### `z_ARCHIVE_DEPRECATED/`
*   Old scripts, "Part 1/2/3" files, and previous experiments.

---

## 🔄 CURRENT SYSTEM STATUS

| Phase | Function | Status | Trigger |
| :--- | :--- | :--- | :--- |
| **1** | History Migration | ✅ Done | N/A |
| **2** | Reactivation | ✅ Active | Odoo Server Action (Manual) |
| **3** | New Job Sync | ✅ Active | Workiz Webhook -> Zapier |
| **4** | Job Updates | ✅ Active | Zapier Polling (5 min) |
| **5** | Auto-Schedule | ✅ Active | Triggered by Phase 6 |
| **6** | Payment Sync | ✅ Active | Odoo Webhook -> Zapier |

---

## 🚀 STRATEGIC GOALS
1.  **Eliminate Zapier:** Move logic to Odoo Server Actions or direct Python scripts.
2.  **STOP Compliance:** Automate "STOP" replies to update Odoo `is_blacklisted`.
3.  **Stability:** Reduce "moving parts" by consolidating code.

---

## 🔑 CREDENTIALS (SHORT)
*   **Odoo:** User ID `2`, DB `window-solar-care`
*   **Workiz:** API Token starts `api_1hu...`
*   **GitHub:** `windowandsolarcare-hash/Odoo-Migration` (Branch: `main`)
