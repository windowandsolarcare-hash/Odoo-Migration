# Phase 3, 4, 5 Reference Summary
**Created:** February 9, 2026  
**Purpose:** Quick reference guide for understanding what each phase does and all Workiz fields used

---

## Rule: Order/schedule times are Pacific; Odoo stores UTC

**All user-facing and business times (order date, job/schedule date, task planned time) are in Pacific (America/Los_Angeles).** Odoo’s **`date_order`** and similar datetime fields are stored in **UTC** and displayed in the user’s timezone. When writing to Odoo (e.g. setting `date_order`), **always convert Pacific → UTC** using the project’s `convert_pacific_to_utc()` in **`functions/utils/convert_pacific_to_utc.py`**. That function is **daylight-saving aware** (uses `zoneinfo` / America/Los_Angeles): summer times use PDT (UTC-7), winter times use PST (UTC-8), and transition dates are correct. When a user says “9:30am” or “12/9/2025 9:30”, treat that as **9:30 AM Pacific** and send the UTC equivalent to Odoo. Do not send the raw time as if it were UTC (that would show as 1:30 AM Pacific).

---

## Rule: Do not assume or guess field names

**Do not assume or guess Workiz or Odoo field names.** Look them up in:
- This document (Phase_3_4_5_Reference_Summary.md)
- `3_Documentation/Workiz_API_Test_Results.md` (LineItems structure and job fields)
- Holy Grail CSV / user-provided data when applicable  

If a field name is not documented here or in those sources, **ask the user**. Guessing or assuming field names risks breaking the code and creating larger problems.

---

## Zapier trigger strategy (how we wire Odoo and Workiz)

- **Odoo:** The standard Odoo triggers in Zapier (e.g. “Updated Record”, “New Record”) are unreliable or limited, so we **do not rely on them**. For Odoo-originated events we use **Webhooks by Zapier – Catch a Hook**: the Zap’s trigger is “Catch a Hook,” and something (e.g. another process or manual POST) sends the payload to that webhook URL when the Odoo event happens. So for “invoice paid” or other Odoo events, the Zap is triggered by a **webhook catch**, not by Zapier polling Odoo.
- **Workiz:** When Workiz **offers a native trigger** for what we need (e.g. **Job status changed**), we **use that trigger**. When Workiz doesn’t offer a suitable trigger for an event, we use **webhooks** (Workiz or another source POSTs to a Zapier Catch a Hook).

So: **Odoo side = webhook catch; Workiz side = use their trigger when available, otherwise webhook catch.**

---

## Property as brain (SO customer = Property)

**The customer on the Sales Order and Invoice is the Property (service address), not the Contact.** The Contact (person) is linked to the Property via **Property.parent_id = Contact** (from import and create_property). We do not change or clear parent_id.

- **SO:** `partner_id` = Property, `partner_shipping_id` = Property. Contact is **not** the SO partner; get Contact when needed via **Property.parent_id** (e.g. for Phase 5 activity, task phone).
- **Migration:** For existing SOs created when customer was Contact, run **`migrate_so_customer_to_property.py`** (with `--dry-run` first, then without) so `partner_id` = current `partner_shipping_id` (Property). Run on a **backup/restore** first.
- **Phase 5/6:** When Phase 6 triggers Phase 5, it reads SO `partner_id` (Property), then **contact_id** = that Property’s **parent_id** (Contact) for the follow-up activity.
- **Migration script** (`migrate_so_customer_to_property.py`): (1) Sets SO `partner_id` = Property; (2) Sets Invoice `partner_id` = SO’s `partner_id` so invoices match. Run on test first (script uses config_test).
- **Phone on SO/Invoice and “United States”:** Phone lives on Contact (Property.parent_id), not Property. To show Contact phone on the SO/Invoice form and use that space instead of repeating “United States,” use **Odoo Studio** (or a custom view): add a field that shows the Contact’s phone (e.g. from `partner_id.parent_id.phone` when `partner_id` is a Property) and make it a clickable link (tel:). Cannot be done from the migration script.

---

## File Summaries

### 1. `zapier_phase3_FLATTENED_FINAL.py` - Initial Sales Order Creation

**Purpose:** Creates new Sales Orders from Workiz jobs when a new job is created.

**What It Does:**
- Routes via Paths A/B/C based on Contact and Property existence
- Creates Contact (if missing) using Workiz ClientId
- Creates Property (if missing) with service details
- Creates Sales Order with complete Workiz job data
- Confirms Sales Order (Quotation → Sales Order) using `action_confirm`
- Updates `date_order` after confirmation (Odoo overwrites during confirm)
- Updates Property fields (gate code, pricing, notes, service details)

**When to Reference:** Creating new Sales Orders from Workiz jobs.

**Key Functions:**
- `main()` - Master router (Paths A/B/C)
- `create_sales_order()` - Creates SO with all Workiz fields
- `confirm_sales_order()` - Confirms SO (Quotation → Sales Order)
- `update_sales_order_date()` - Fixes date_order after confirmation

---

### 2. `zapier_phase4_FLATTENED_FINAL.py` - Sales Order Updates

**Purpose:** Updates existing Sales Orders when Workiz job status changes.

**What It Does:**
- Searches for existing SO by Workiz UUID
- **If found:** Updates SO fields with latest Workiz data, **including order line items** (replaces SO lines with current Workiz job LineItems)
- **If not found:** Calls Phase 3 to create it
- **Skips when status = "Submitted"** so the new job Phase 5 creates doesn't trigger Phase 4; Phase 3 runs from the "New Job" trigger instead, then Phase 4 runs when you change status (e.g. to send text).
- **When status = "Done":** Does **not** write payment fields to Odoo (payment originates in Odoo via Phase 6A); still updates status and property Last Visit Date. **Phase 4 does not trigger Phase 5** when Done (only Phase 6 does after marking job Done), to avoid duplicate next jobs.
- Updates Property "Last Visit Date" when job is Done
- Posts status updates to SO chatter (no payment-status line when Done)

**When to Reference:** Updating existing Sales Orders, payment tracking, status changes.

**Key Functions:**
- `main()` - Main router (handles status updates)
- `update_existing_sales_order()` - Updates SO with Workiz data
- `update_property_from_job()` - Updates Property fields
- `phase3_create_so()` - Calls Phase 3 if SO missing

**⚠️ Payment and Done (Phase 6A alignment):**
- Payment now originates in Odoo; Phase 6A syncs to Workiz (add payment + mark job Done).
- When Workiz job status becomes "Done", the "Job Status Changed" webhook can still fire and run Phase 4.
- **Phase 4 was updated:** For status = "Done", Phase 4 does **not** write payment fields (`x_studio_is_paid`, `x_studio_tip_amount`) or payment-related chatter to Odoo, so Odoo’s payment data is never overwritten by Workiz. Phase 4 still updates all other SO fields and property Last Visit Date; it does not call Phase 5 when Done (only Phase 6 does), to avoid duplicate next jobs.

---

### 3. `zapier_phase5_FLATTENED_FINAL.py` - Auto-Scheduler

**Purpose:** Creates next scheduled job after a job is marked "Done".

**What It Does:**
- **MAINTENANCE:** Creates next scheduled job in Workiz (POST job/create) with **ServiceArea** (desert / Hemet from city) and line items reference. **Does not assign tech**; you add line items, assign, set time, and set status in Workiz. On HTTP 200 the API returns UUID, ClientId, link per docs; we use that. On 204 we fall back to job/all only for logging. Does not set status.
- **ON DEMAND:** Creates follow-up reminder (mail.activity) and a calendar.event so it appears in Calendar view
- City-aware scheduling (route-based, matching Calendly); **time is fixed 10:00 AM** (you can adjust when setting the slot manually)
- Handles alternating service logic (uses line items from 2 jobs back)

**When to Reference:** Auto-scheduling next jobs, NOT directly related to SO creation/updates.

**Key Functions:**
- `main()` - Routes based on service type (Maintenance vs On Demand)
- `schedule_next_maintenance_job()` - Creates next job in Workiz
- `create_ondemand_followup()` - Creates Odoo activity

---

## Complete Workiz Fields Used for Sales Orders

### Fields Used in Initial SO Creation (Phase 3):

| Workiz Field | Odoo Destination | Notes |
|-------------|------------------|-------|
| `ClientId` | Contact `ref` field | Used for search/creation |
| `FirstName` | Contact `x_studio_x_studio_first_name` | |
| `LastName` | Contact `x_studio_x_studio_last_name` | |
| `Phone` | Contact `phone` | |
| `Email` | Contact `email` | |
| `Address` | Property `street` | |
| `City` | Property `city` | |
| `PostalCode` | Property `zip` | |
| `LocationId` | Property `x_studio_x_studio_location_id` | |
| `UUID` | SO `x_studio_x_studio_workiz_uuid` | **Key field for linking** |
| `SerialId` | SO `name` | Formatted as 6-digit (e.g., "000123") |
| `JobDateTime` | SO `date_order` | Converted Pacific → UTC (DST-aware so 10:00 shows as 10:00, not 11:00) |
| `SubStatus` / `Status` | SO `x_studio_x_studio_workiz_status` | SubStatus preferred, falls back to Status |
| `JobSource` | SO `x_studio_x_studio_lead_source` | |
| `JobType` | SO `x_studio_x_studio_x_studio_job_type` | |
| `Team` | SO `x_studio_x_studio_workiz_tech` | Formatted as comma-separated names |
| `Tags` / `JobTags` | SO `tag_ids` | Via crm.tag lookup |
| `GateCode` / `gate_code` | SO `x_studio_x_gate_snapshot` + Property `x_studio_x_gate_code` | |
| `Pricing` / `pricing` | SO `x_studio_x_studio_pricing_snapshot` + Property `x_studio_x_pricing` | |
| `JobNotes` / `Notes` | SO `x_studio_x_studio_notes_snapshot1` + Property `comment` | Combined with Comments |
| `Comments` / `Comment` | SO `x_studio_x_studio_notes_snapshot1` + Property `comment` | Combined with JobNotes |
| `LineItems` | SO `order_line` | **Product match by Workiz product code:** Odoo product field `x_studio_x_studio_workiz_product_number` = Workiz line item `ModelNum` or `Id` (from GET job/get; see Workiz_API_Test_Results.md). Fallback: product name, then "Service". |
| `frequency` | Property `x_studio_x_frequency` + **SO** `x_studio_x_studio_frequency_so` | 3/6/12 months, Unknown; _so = SO copy for invoicing |
| `alternating` | Property `x_studio_x_alternating` | Converted: 1/0 → Yes/No |
| `type_of_service` | Property `x_studio_x_type_of_service` + **SO** `x_studio_x_studio_type_of_service_so` | Maintenance, On Request, Unknown; _so = SO copy for invoicing |

**Line items → Odoo product matching (Phase 3 & 4):**  
We do **not** match by product name. Odoo products have a custom field **`x_studio_x_studio_workiz_product_number`** that stores the Workiz product code. Workiz API (GET job/get) and the **Holy Grail CSV** both use the same field name **`LineItems`** and the same structure: a list of dicts, each with **`Id`** (e.g. 32052), plus `Name`, `Quantity`, `Price`, `Description`, `ModelNum`, etc. We iterate over **every** item in that list and add one SO order line per item (multiple line items → multiple SO lines). Product lookup uses `ModelNum` or `Id` → `x_studio_x_studio_workiz_product_number`; fallback: product name, then "Service". When LineItems is a string (e.g. from CSV), we parse it with `ast.literal_eval`. See `3_Documentation/Workiz_API_Test_Results.md` for the full structure.

**Default project for SOs (products that create tasks):** When an SO has order lines, Odoo may require a project on the quotation for products that create tasks. Set **`DEFAULT_PROJECT_ID`** in the Phase 3 and Phase 4 scripts to your Odoo project ID (integer). Find the ID in Odoo: Project app → open the project → URL contains `id=...`, or enable Developer Mode and use View Metadata. **Using the ID (not the project name) means renaming the project in Odoo will not break the integration.** The SO field used is **`project_id`** (standard Odoo). If your instance uses a different field name, update `ODOO_SO_PROJECT_FIELD` in the scripts.

**Products defaulting to Field Service (project 2):** You can set **all products** to use Field Service as their default project so tasks created from SO lines go to that project by default. Run **`update_all_products_task_and_service.py`** (it now also sets **`project_id`** = Field Service on every product). After products are updated, you can **test** whether the Phase 3/4 code that sets **`project_id`** on the SO is still needed: create an SO with a task-creating product and confirm the task appears in Field Service. If it does without the SO being given a project, the SO `project_id` code can be removed or made optional; keeping it is harmless and acts as a fallback.

**Task sync (assignee, planned date, tags, customer, contact number):** After creating or updating an SO, we sync all tasks linked to that SO (via `sale_line_id` on `project.task`):
- **Assignee:** First tech/team member from Workiz `Team` → lookup **res.users** by name (not hardcoded). Set **`ODOO_TASK_ASSIGNEE_FIELD`** (default **`user_ids`**; use **`user_id`** if your app has a single-assignee field).
- **Planned date:** Order/scheduled date (JobDateTime) → **`ODOO_TASK_PLANNED_DATE_FIELD`** (default **`date_deadline`**). Start with time → **`ODOO_TASK_START_DATETIME_FIELD`** (default **`date_planning`**). End with time: set **`WORKIZ_JOB_END_DATETIME_FIELD`** to the Workiz field name for job end (e.g. `JobEndDateTime`) and **`ODOO_TASK_END_DATETIME_FIELD`** to the task’s end-datetime field name.
- **Tags:** From the SO’s **`tag_ids`** → task **`ODOO_TASK_TAG_IDS_FIELD`** (default **`tag_ids`**).
- **Customer:** SO’s **`partner_id`** → task **`ODOO_TASK_PARTNER_FIELD`** (default **`partner_id`**).
- **Contact number:** Taken from the **Contact** record only (SO **partner_id**), not from the Property. We read the Contact’s **phone** and set task **`ODOO_TASK_PHONE_FIELD`** (default **`phone`**). Set to **False** to skip.
- **Service address:** Taken from the **Property** record (SO **partner_shipping_id**). We set task **`ODOO_TASK_PROPERTY_PARTNER_FIELD`** (default **`partner_shipping_id`**) so the task’s address stays the property address. If your task uses a different field for the property/site address, set that constant; set to **False** to skip.
Record categories: Contact = customer, phone lives here; Property = service address. We use Contact for customer + phone and Property for address.
All of these constants are in the Phase 3 and Phase 4 scripts so you can match your Field Service app’s field names without guessing.

**To show Frequency and Type of Service on the Sales Order (for invoicing):**  
In Odoo, add two custom fields on **Sales Order** (`sale.order`) with these exact technical names (the _so suffix = SO copy; property stays source of truth). **Use Selection type** for consistent filtering and reporting:

- **`x_studio_x_studio_frequency_so`** — label **Frequency**, type **Selection** (Workiz options):
  - `3 Months`, `4 Months`, `6 Months`, `12 Months`, `Unknown`
- **`x_studio_x_studio_type_of_service_so`** — label **Type of Service**, type **Selection** (Workiz options):
  - `Maintenance`, `On Request`, `Unknown`

Create via **Settings → Technical → Database Structure → Models → sale.order → New Field**, or Odoo Studio. Sync (Phase 3 / Phase 4) only writes a value if it exists in the Selection; otherwise it logs and omits (add the value in Odoo to sync it).

**Property/Contact fields** (`x_studio_x_frequency`, `x_studio_x_type_of_service`) are currently Char. You can later add Selection fields and migrate data if you want the same benefits on the property model; the SO fields above should be created as Selection from the start.

### Additional Fields Used in SO Updates (Phase 4):

| Workiz Field | Odoo Destination | Notes |
|-------------|------------------|-------|
| `Status` | Determines if payment fields should be added | Only when Status = "Done" |
| `JobAmountDue` | SO `x_studio_is_paid` | Boolean: True if JobAmountDue = 0 |
| `LineItems` (tip extraction) | SO `x_studio_tip_amount` | Extracts tip from LineItems |
| `JobDateTime` | Property `x_studio_x_studio_last_property_visit` | Date only (when Status = "Done") |
| `LastStatusUpdate` | SO Chatter message | Timestamp in chatter |

### Payment Fields (Phase 4 - Current Implementation):

**When Status = "Done":**
- `JobAmountDue` → `x_studio_is_paid` (True if amount due = 0)
- `LineItems` (tip) → `x_studio_tip_amount` (extracted from line items)

**⚠️ Phase 6 Change:**
- These fields will be populated from Odoo payment records instead of Workiz
- Phase 6 will sync payment TO Workiz after recording in Odoo

---

## Before creating invoice: Keep SO (and line items) in sync with Workiz

Workiz is the source of truth for what was done at the job (e.g. line items like "Shower glass doors"). Phase 4 updates SO **status/notes/date** when Workiz status changes and **order line items** (matched by Workiz product code; see "Line items → Odoo product matching" above). So if someone adds a line in Workiz after the SO was created, Odoo won’t have it until you refresh.

**Recommendation:** Automate with a schedule so that by the time you create an invoice, the SO already has the latest Workiz data (including line items).

- **Scheduled (e.g. every 4 hours)** – Run:  
  `python refresh_so_from_workiz.py --scheduled`  
  from folder `2_Modular_Phase3_Components`. This finds all confirmed SOs that have a Workiz UUID and are **not yet fully invoiced**, fetches the latest job from Workiz, and updates the SO (status, notes, date, **and line items**). Use Task Scheduler / cron. Optional: `--limit 50`, `--delay 2.5`, `--dry-run` to test.

- **Single SO before invoicing** – If you want to refresh one order right before creating the invoice:  
  `python refresh_so_from_workiz.py <so_id>`  
  (e.g. `python refresh_so_from_workiz.py 15832`). Then create the invoice from that SO.

A future Odoo button (“Refresh from Workiz”) could call the same logic for the current SO; for now the script covers both scheduled and one-off refresh.

---

## Standard workflow: Accept payment (e.g. SO 003982, $125, check 3465)

1. **In Odoo – Sales Order**  
   Open the SO (e.g. 003982). Confirm it has the correct Workiz UUID and amount.

2. **Create and confirm invoice**  
   Create the invoice from the SO, then confirm/post it (terminology: **post** the invoice).

3. **Register the payment** – Click the **Pay** button **at the top** of the invoice (not "Collect Payment" in the gear). In the pop-up wizard: **Journal** (e.g. BNK1), **Payment method**, **Amount**, **Date**, **Memo/Reference** (e.g. check **3465**). Then **Create Payment** / **Validate**. Invoice shows **Paid**, **$0.00**.

4. **Sync to Workiz (Phase 6)**  
   When the automation triggers on **Payment** (recommended): each payment you enter (e.g. first roommate’s check, second roommate’s check) is sent to Zapier; the Zap adds **that payment’s amount** to Workiz and marks the job **Done only when the invoice balance is zero**. So split payments are supported: first payment → Workiz gets partial; second payment → Workiz gets second partial; when the invoice is fully paid, job is marked Done.  
   Odoo does **not** call Workiz by itself. Options:
   - **Automation (recommended):** Run the webhook server and have Odoo (or Zapier) call it when an invoice is paid. See **Phase6_Automation_When_Invoice_Paid.md** in this folder: run `python phase6_webhook_server.py` in `2_Modular_Phase3_Components`, expose the URL (e.g. ngrok), then set up Odoo Automation to POST the invoice id to that URL when `payment_state` = paid. No manual step.
   - **Manual (one invoice):** `python phase6_payment_sync_to_workiz.py <invoice_id>` from folder `2_Modular_Phase3_Components`.
   - **Scheduled fallback:** `python phase6_auto_sync_paid_invoices.py` (every 5–10 min) to catch any paid invoices that weren’t triggered by the webhook.

5. **Workiz → Phase 4**  
   When the job is marked Done, Workiz “Job Status Changed” triggers Phase 4: Odoo SO and property are updated (no payment fields written from Workiz; payment is from Odoo).

6. **Phase 5 (after Done)**  
   Phase 4 triggers Phase 5 based on **Type of Service**:
   - **Maintenance** → Create next job in Workiz (per frequency).
   - **On Demand** → Create Odoo activity only (follow-up in 6 months, Sunday).
   - **Unknown** or **On Request** → Create Odoo activity only, **follow-up in 1 year (Sunday)**. **No new job is created in Workiz.**

For SO 003982 (Unknown / Unknown): when you post the invoice and sync payment, the job will be marked Done; Phase 5 will create a **single Odoo activity** due in 1 year (on a Sunday) to call the customer, and will **not** create a new Workiz job.

---

## Sales Order Cancellation via API

### Single Cancellation:

```python
def cancel_sales_order(so_id):
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB,
                ODOO_USER_ID,
                ODOO_API_KEY,
                "sale.order",
                "action_cancel",  # ← This is the method
                [[so_id]]  # ← List of IDs to cancel
            ]
        }
    }
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    return response.json().get("result") is not False
```

### Bulk Cancellation:

Yes, you can cancel multiple Sales Orders at once by passing multiple IDs:

```python
def cancel_sales_orders_bulk(so_ids):
    """Cancel multiple Sales Orders in one API call"""
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB,
                ODOO_USER_ID,
                ODOO_API_KEY,
                "sale.order",
                "action_cancel",
                [so_ids]  # ← Pass list of IDs: [123, 456, 789]
            ]
        }
    }
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    return response.json().get("result") is not False
```

### Workflow for Deletion:

1. **Cancel SO:** `action_cancel` (unlocks it, changes state from "sale" to "cancel")
2. **Delete SO:** `unlink` (removes it from database)

**Note:** You cannot delete a Sales Order that is in "sale" state. It must be cancelled first.

---

## Phase 4 Payment Flow - Current vs Phase 6

### Current Flow (Phase 4):
```
Payment accepted in Workiz
    ↓
Job marked "Done" in Workiz
    ↓
Phase 4 triggered (status change webhook)
    ↓
Phase 4 reads JobAmountDue from Workiz
    ↓
Updates Odoo SO: x_studio_is_paid, x_studio_tip_amount
    ↓
Triggers Phase 5 (if Maintenance/On Demand)
```

### New Flow (Phase 6):
```
Payment received at door (check/cash/credit)
    ↓
Payment recorded in Odoo (invoice payment)
    ↓
Phase 6 triggered (manual script or scheduled run of phase6_auto_sync_paid_invoices.py)
    ↓
Phase 6 syncs payment to Workiz via POST /job/addPayment/{UUID}/
    ↓
If balance = 0: Mark job "Done" in Workiz (or trigger Phase 4)
    ↓
Phase 4/5 continues with "Done" status logic
```

### Conflict Resolution:

**Question:** Should Phase 4's payment reading logic be:
1. **Disabled** when Phase 6 is active?
2. **Modified** to only read if payment wasn't synced from Odoo?
3. **Left active** as fallback (if payment entered directly in Workiz)?

**Recommendation:** Leave Phase 4 active as fallback, but add logic to check if payment was already synced from Odoo to avoid duplicate updates.

---

## Quick Reference: Which File to Use?

| Task | File | Function |
|------|------|----------|
| Create new SO from Workiz job | `zapier_phase3_FLATTENED_FINAL.py` | `main()` |
| Update existing SO (status change) | `zapier_phase4_FLATTENED_FINAL.py` | `main()` |
| Auto-schedule next job | `zapier_phase5_FLATTENED_FINAL.py` | `main()` |
| Cancel Sales Order | Utility script (not yet created) | `action_cancel` |
| Delete Sales Order | Utility script | `unlink` (after cancel) |

---

**Last Updated:** February 9, 2026  
**Next Review:** After Phase 6 implementation

