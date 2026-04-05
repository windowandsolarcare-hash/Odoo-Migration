"""
ZAPIER PHASE 4 FLATTENED SCRIPT - FINAL
=======================================
Workiz Job Status Update -> Odoo Integration

Author: DJ Sanders

Triggered by: Workiz job status change (any status).
If your Zap uses "Job Updated" (every field change), Phase 4 will run often (e.g. adding line items, assigning time). To reduce runs, use "Job Status Changed" only if Workiz offers it.

Features:
- Skips when status is "Submitted" (new job from Phase 5; Phase 3 creates SO via New Job trigger; Phase 4 runs when you change status later, e.g. to send text)
- Updates existing Sales Order if found (including order line items from Workiz)
- Idempotent create: if SO already exists for this job UUID, returns it (no duplicate SOs)
- Re-check before create: if another run just created the SO, we update instead of creating again
- Creates new SO via Phase 3 logic only when missing (Paths A/B/C)
- When creating a missing SO: only confirms SO (creates task) when Status or SubStatus is one of: "Next appointment", "Send confirmation text", "Scheduled". All other statuses/substatuses → SO created as draft (no task).
- When updating an existing draft SO (quotation): if status becomes one of those three, we confirm the SO (so Odoo creates tasks), then sync task fields (assignee/tech, planned date, start/end in UTC from Workiz Pacific, phone from Contact).
- Every time Phase 4 runs for an existing SO (any status/date/team change): we update the existing task(s) with current Workiz data (task name = "Customer Name - City", assignee, planned date, start/end, phone, tags). We never create a duplicate task; changing the date in Workiz moves the task to the new date.
- When status = "Done": does NOT write payment fields to Odoo (payment originates in Odoo via Phase 6A)
- Updates Property "Last Visit Date" when done
- NEW (2026-03-06): Analyzes SO products and updates Property service tracking fields:
  - x_studio_has_window_service (Checkbox, cumulative: set to True if windows detected, never set to False)
  - x_studio_has_solar_service (Checkbox, cumulative: set to True if solar detected, never set to False)
  - x_studio_most_recent_service_type (Selection: 'windows', 'solar', 'both', 'other', blank - updated each job)
- NEW (2026-03-06): Aggregates Property data to Contact level when job completes:
  - Contact x_studio_last_visit_all_properties = MAX last visit date across all properties
  - Contact x_studio_has_window_service = True if ANY property has window service
  - Contact x_studio_has_solar_service = True if ANY property has solar service
  - Contact x_studio_most_recent_service_type = from property with most recent visit
- Posts status updates to SO chatter (no payment-status line when Done)

Generated: 2026-02-07
Updated: 2026-03-06 (Added service tracking + Contact/Property aggregation)
"""

import requests
import json
import sys
import os
from datetime import datetime, timedelta
import ast

# ==============================================================================
# CONFIGURATION & CREDENTIALS
# ==============================================================================

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

WORKIZ_API_TOKEN = "api_1hu6lroiy5zxomcpptuwsg8heju97iwg"
WORKIZ_AUTH_SECRET = "sec_334084295850678330105471548"
WORKIZ_BASE_URL = f"https://api.workiz.com/api/v1/{WORKIZ_API_TOKEN}"

# Phase 3 Webhook URL (for Phase 4 to call when SO doesn't exist)
PHASE3_WEBHOOK_URL = "https://hooks.zapier.com/hooks/catch/9761276/ueyjr41/"

# Phase 5 Webhook URL (set this after deploying Phase 5 Zap)
PHASE5_WEBHOOK_URL = "https://hooks.zapier.com/hooks/catch/9761276/ue4o0az/"  # TODO: Replace with actual webhook URL

# Odoo product field that stores Workiz product code (cross-reference for line item matching)
ODOO_PRODUCT_WORKIZ_CODE_FIELD = "x_studio_x_studio_workiz_product_number"

# Default project ID for SOs when products create tasks (Odoo requires project on quotation).
# Set to your Odoo project ID (integer). Find it: Project app → open project → URL has id=... or enable Developer Mode → View Metadata.
# Renaming the project in Odoo does not change its ID, so this won't break.
DEFAULT_PROJECT_ID = 2
# Odoo field on sale.order for project (standard: project_id -> project.project)
ODOO_SO_PROJECT_FIELD = "project_id"
# Task fields (standard Odoo names; change if your Field Service uses different technical names)
ODOO_TASK_PLANNED_DATE_FIELD = "date_deadline"   # planned/end date (Date)
ODOO_TASK_ASSIGNEE_FIELD = "user_ids"           # assignee(s); standard can be user_ids (many2many) or user_id (many2one)
ODOO_TASK_TAG_IDS_FIELD = "tag_ids"             # tags from SO
ODOO_TASK_PARTNER_FIELD = "partner_id"          # customer/contact (record category Contact — phone lives here)
ODOO_TASK_PHONE_FIELD = "partner_phone"         # Contact Number on task: we fill from Odoo Contact (Property.parent_id). Studio label "Contact Number", technical name partner_phone.
ODOO_TASK_PROPERTY_PARTNER_FIELD = False  # Odoo 19 FSM project.task has no 'partner_shipping_id'; set to field name if you add it (e.g. Studio)
# Optional: planned start/end with time (Datetime). Set to False if not used.
ODOO_TASK_START_DATETIME_FIELD = "planned_date_begin"  # Odoo 19 FSM: planned start datetime (UTC)
ODOO_TASK_END_DATETIME_FIELD = "date_end"             # Odoo 19 FSM: planned end datetime (UTC); set False to skip
# Workiz: job start = JobDateTime. End: if your Workiz job has end date/time, set the key here (e.g. "JobEndDateTime").
WORKIZ_JOB_END_DATETIME_FIELD = "JobEndDateTime" # Workiz returns this field with job end time

# Line item matching for confirmed SOs: Set to False to disable "set qty=0 for removed items" behavior
ENABLE_LINE_ITEM_REMOVAL_ON_CONFIRMED_SO = True  # True = set qty=0 for items not in Workiz; False = only update/add


# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

def extract_job_from_input(input_data):
    """
    Extract job UUID and job data from Zapier input.
    Supports both webhook format (flattened by Zapier) and polling format.
    Returns: (job_uuid, workiz_job_dict or None)
    """
    try:
        # Check for Zapier's FLATTENED Workiz webhook format (keys like 'Data Uuid', 'Data Status', etc.)
        # Zapier flattens nested JSON: {'data': {'uuid': 'X'}} becomes {'Data Uuid': 'X'}
        if 'Data Uuid' in input_data or 'data__uuid' in input_data:
            print("[*] Detected Workiz webhook format (real-time, Zapier-flattened)")
            
            # Extract using Zapier's flattened keys
            job_uuid = input_data.get('Data Uuid') or input_data.get('data__uuid', '')
            
            # Extract clientId and strip CL- prefix
            client_id_raw = input_data.get('Data Client Info Client Id', '')
            client_id = str(client_id_raw).replace('CL-', '') if client_id_raw else ''
            
            # Build job data dict matching our existing code expectations (using Zapier's flattened keys)
            workiz_job = {
                'UUID': job_uuid,
                'SerialId': input_data.get('Data Serial Id', ''),
                'Status': input_data.get('Data Status', ''),
                'SubStatus': input_data.get('Data Sub Status Name', ''),  # Zapier flattens subStatus.name
                'JobDateTime': input_data.get('Data Date', ''),
                'JobType': input_data.get('Data Job Type Name', ''),  # Zapier flattens jobType.name
                'JobSource': input_data.get('Data Ad Group Name', ''),  # Zapier flattens adGroup.name
                'ClientId': client_id,
                'FirstName': input_data.get('Data Client Info First Name', ''),
                'LastName': input_data.get('Data Client Info Last Name', ''),
                'Phone': input_data.get('Data Client Info Primary Phone', ''),
                'Email': input_data.get('Data Client Info Email', ''),
                'Address': input_data.get('Data Client Info Address Details Address', ''),
                'City': input_data.get('Data Client Info Address Details City', ''),
                'PostalCode': input_data.get('Data Client Info Address Details Zip Code', ''),
                'LocationId': input_data.get('Data Client Info Address Details Location Key', ''),
                'Team': [],  # Will extract from flattened team keys below
                'LineItems': [],  # Will extract from flattened line item keys below
                'Tags': [],  # Will extract from flattened tag keys below
                'JobNotes': input_data.get('Data Description', ''),  # Webhook has 'description' field
                'Comments': '',
                'gate_code': '',
                'pricing': '',
                'frequency': '',
                'alternating': '',
                'type_of_service': '',
            }
            
            # Extract Team (Zapier flattens as 'Data Team 1 Name', 'Data Team 2 Name', etc.)
            team_list = []
            for key in input_data.keys():
                if key.startswith('Data Team') and key.endswith('Name'):
                    team_name = input_data.get(key, '')
                    if team_name:
                        team_list.append({'Name': team_name})
            workiz_job['Team'] = team_list
            
            # Extract Tags (Zapier flattens as 'Data Tags 1 Name', etc.)
            tags_list = []
            for key in input_data.keys():
                if key.startswith('Data Tags') and 'Name' in key:
                    tag_name = input_data.get(key, '')
                    if tag_name:
                        tags_list.append(tag_name)
            workiz_job['Tags'] = tags_list
            
            # Extract Custom Fields (Zapier flattens as 'Data Custom Fields 1 Field Name', 'Data Custom Fields 1 Value', etc.)
            for key in input_data.keys():
                if key.startswith('Data Custom Fields') and key.endswith('Field Name'):
                    field_name = (input_data.get(key, '') or '').lower().strip()
                    # Get corresponding value key (replace 'Field Name' with 'Value')
                    value_key = key.replace('Field Name', 'Value')
                    value = input_data.get(value_key, '')
                    
                    if 'gate' in field_name:
                        workiz_job['gate_code'] = value
                    elif 'pricing' in field_name or 'price' in field_name:
                        workiz_job['pricing'] = value
                    elif 'frequency' in field_name or 'freq' in field_name:
                        workiz_job['frequency'] = value
                    elif 'alternating' in field_name:
                        workiz_job['alternating'] = value
                    elif 'type' in field_name and 'service' in field_name:
                        workiz_job['type_of_service'] = value
            
            print(f"[*] Webhook parsed successfully: UUID={job_uuid}, ClientId={client_id}")
            return (job_uuid, workiz_job)
        
        # Fallback to Zapier polling format (flat structure)
        job_uuid = input_data.get('job_uuid') or input_data.get('UUID')
        
        if job_uuid:
            print("[*] Detected Zapier polling format (may be delayed)")
            return (job_uuid, None)
        
        return (None, None)
        
    except Exception as e:
        print(f"[ERROR] extract_job_from_input failed: {e}")
        import traceback
        traceback.print_exc()
        # Try fallback to simple job_uuid extraction
        job_uuid = input_data.get('job_uuid') or input_data.get('UUID')
        if job_uuid:
            return (job_uuid, None)
        return (None, None)


def _odoo_search_read(model, domain, fields, limit=1):
    """Helper: search_read and return result list."""
    payload = {
        "jsonrpc": "2.0", "method": "call",
        "params": {
            "service": "object", "method": "execute_kw",
            "args": [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, model, "search_read", [domain], {"fields": fields, "limit": limit}]
        }
    }
    try:
        r = requests.post(ODOO_URL, json=payload, timeout=10)
        return r.json().get("result", [])
    except Exception:
        return []


def _odoo_write(model, record_ids, values):
    """Helper: write to Odoo records and return success boolean."""
    payload = {
        "jsonrpc": "2.0", "method": "call",
        "params": {
            "service": "object", "method": "execute_kw",
            "args": [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, model, "write", [record_ids, values]]
        }
    }
    try:
        r = requests.post(ODOO_URL, json=payload, timeout=10)
        return r.json().get("result", False)
    except Exception:
        return False


def _odoo_find_user_id_by_name(tech_name):
    """Return Odoo res.users id for a name (e.g. 'Dan Saunders'). Not hardcoded — lookup by name."""
    if not tech_name or not str(tech_name).strip():
        return None
    name = str(tech_name).strip()
    # Try exact name then ilike
    for domain in [[["name", "=", name]], [["name", "ilike", name]]]:
        users = _odoo_search_read("res.users", domain, ["id"], limit=1)
        if users:
            return users[0]["id"]
    return None


def _parse_workiz_tag_names(raw_tags):
    """Normalize Workiz tags payload to a clean list of tag names."""
    if not raw_tags:
        return []
    if isinstance(raw_tags, str):
        try:
            parsed = ast.literal_eval(raw_tags)
            raw_tags = parsed
        except Exception:
            raw_tags = [t.strip() for t in raw_tags.split(",") if t.strip()]
    if not isinstance(raw_tags, list):
        return []
    names = []
    for t in raw_tags:
        if isinstance(t, dict):
            name = t.get("Name") or t.get("name") or t.get("Tag") or t.get("tag")
        else:
            name = str(t) if t is not None else ""
        name = (name or "").strip()
        if name:
            names.append(name)
    # preserve order while removing duplicates
    return list(dict.fromkeys(names))


def _resolve_task_tag_ids_from_workiz(workiz_job):
    """
    Map Workiz tag names to Odoo task tags (project.tags) IDs.
    Fallback to crm.tag lookup only when project.tags doesn't contain the name.
    """
    tag_names = _parse_workiz_tag_names(workiz_job.get("Tags") or workiz_job.get("JobTags"))
    if not tag_names:
        return []
    ids = []
    for tag_name in tag_names:
        found = _odoo_search_read("project.tags", [["name", "=", tag_name]], ["id"], limit=1)
        if not found:
            found = _odoo_search_read("project.tags", [["name", "ilike", tag_name]], ["id"], limit=1)
        if not found:
            # Backward compatibility fallback if this DB still uses crm.tag IDs in task.tag_ids.
            found = _odoo_search_read("crm.tag", [["name", "=", tag_name]], ["id"], limit=1)
            if not found:
                found = _odoo_search_read("crm.tag", [["name", "ilike", tag_name]], ["id"], limit=1)
        if found:
            tag_id = found[0].get("id")
            if isinstance(tag_id, int):
                ids.append(tag_id)
        else:
            print(f"[!] Workiz task tag not found in project.tags/crm.tag: '{tag_name}'")
    return sorted(set(ids))


def sync_tasks_from_so_and_job(so_id, workiz_job, job_datetime_utc):
    """
    Sync all tasks linked to this SO. job_datetime_utc must be UTC (Workiz JobDateTime converted via convert_pacific_to_utc for DST).
    Sets: task name = "Customer Name - City" (from Contact + Property city), assignee (tech/team from Workiz),
    planned date = date_order/JobDateTime, start datetime (date_planning), end datetime (if configured; Pacific→UTC),
    tags from SO, customer (Property), service address (Property), contact phone (from Contact = Property.parent_id).
    """
    # Return dict so caller can put it in output (Zapier Data out); prints often not visible in Code step logs.
    def _ret(tasks_found=0, tasks_updated=False, error=None):
        return {"task_sync_tasks_found": tasks_found, "task_sync_updated": tasks_updated, "task_sync_error": error}
    print(f"[*] Syncing tasks for SO id={so_id} (JobDateTime in payload: {bool(job_datetime_utc)}, Team: {bool(workiz_job.get('Team') or workiz_job.get('team'))})")
    # Resolve SO line ids and task ids
    lines = _odoo_search_read("sale.order.line", [["order_id", "=", so_id]], ["id"], limit=500)
    line_ids = [x["id"] for x in lines]
    if not line_ids:
        print("[!] No order lines found for SO; cannot sync tasks.")
        return _ret(error="No order lines for SO")
    payload_tasks = {
        "jsonrpc": "2.0", "method": "call",
        "params": {
            "service": "object", "method": "execute_kw",
            "args": [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, "project.task", "search", [[["sale_line_id", "in", line_ids]]]]
        }
    }
    try:
        r = requests.post(ODOO_URL, json=payload_tasks, timeout=10)
        task_ids = r.json().get("result", [])
    except Exception as e:
        print(f"[!] Task search failed: {e}")
        return _ret(error=f"Task search failed: {e}")
    if not task_ids:
        print("[!] No tasks found linked to this SO's order lines (sale_line_id in line_ids). Checking for backfill...")
        # Backfill: if SO is confirmed (state=sale) and in a scheduling status, create tasks directly via API.
        # Avoids cancel/draft/confirm cycle which risks breaking SOs with invoices/payments.
        so_check = _odoo_search_read("sale.order", [["id", "=", so_id]], ["state", "partner_id", "partner_shipping_id"], limit=1)
        wiz_status = workiz_job.get("Status", "")
        wiz_substatus = workiz_job.get("SubStatus", "")
        if so_check and so_check[0].get("state") == "sale" and is_task_trigger_status(wiz_status, wiz_substatus):
            print(f"[*] Backfill triggered: confirmed SO, substatus={wiz_substatus or wiz_status}, {len(line_ids)} order line(s)")
            backfilled = 0
            for ol_id in line_ids:
                create_vals = {"project_id": DEFAULT_PROJECT_ID, "sale_line_id": ol_id}
                # Task name: "{ContactName} - {City}" — same format Phase 3 uses
                so_partner = so_check[0].get("partner_id")
                pid = so_partner[0] if isinstance(so_partner, (list, tuple)) else so_partner
                if pid:
                    prop = _odoo_search_read("res.partner", [["id", "=", pid]], ["name", "parent_id", "city"], limit=1)
                    if prop:
                        city = (prop[0].get("city") or "").strip()
                        contact_id = prop[0].get("parent_id")
                        contact_id = contact_id[0] if isinstance(contact_id, (list, tuple)) else contact_id
                        customer_name = (prop[0].get("name") or "").strip()
                        if contact_id:
                            contact = _odoo_search_read("res.partner", [["id", "=", contact_id]], ["name"], limit=1)
                            if contact:
                                customer_name = (contact[0].get("name") or customer_name).strip()
                        task_name = (f"{customer_name} - {city}".strip(" - ").strip() if city else customer_name) or "New Task"
                        create_vals["name"] = task_name
                    # Description: copy order line name (product + description text) — mirrors what action_confirm() does
                    ol_line = _odoo_search_read("sale.order.line", [["id", "=", ol_id]], ["name"], limit=1)
                    if ol_line:
                        ol_name = (ol_line[0].get("name") or "").strip()
                        # Description is the part after the first line (product name is line 1)
                        desc_parts = ol_name.split("\n", 1)
                        if len(desc_parts) > 1 and desc_parts[1].strip():
                            create_vals["description"] = desc_parts[1]
                    if ODOO_TASK_PARTNER_FIELD:
                        create_vals[ODOO_TASK_PARTNER_FIELD] = pid
                # Assignee from Workiz team; fall back to project manager (ODOO_USER_ID) so task is never unassigned
                team_raw = workiz_job.get("Team") or workiz_job.get("team") or []
                if isinstance(team_raw, list) and team_raw and ODOO_TASK_ASSIGNEE_FIELD:
                    for m in team_raw:
                        fname = (m.get("Name") or m.get("name") or "") if isinstance(m, dict) else ""
                        if fname:
                            uid = _odoo_find_user_id_by_name(str(fname).strip())
                            if uid:
                                if ODOO_TASK_ASSIGNEE_FIELD == "user_ids":
                                    create_vals["user_ids"] = [(6, 0, [uid])]
                                else:
                                    create_vals[ODOO_TASK_ASSIGNEE_FIELD] = uid
                            break
                if ODOO_TASK_ASSIGNEE_FIELD and "user_ids" not in create_vals and ODOO_TASK_ASSIGNEE_FIELD not in create_vals:
                    create_vals["user_ids"] = [(6, 0, [ODOO_USER_ID])]
                # Planned dates from job datetime
                if job_datetime_utc:
                    if ODOO_TASK_START_DATETIME_FIELD:
                        create_vals[ODOO_TASK_START_DATETIME_FIELD] = job_datetime_utc
                    # End: use Workiz JobEndDateTime if available, else start+1h
                    end_str = None
                    if WORKIZ_JOB_END_DATETIME_FIELD and workiz_job.get(WORKIZ_JOB_END_DATETIME_FIELD):
                        raw_end = str(workiz_job.get(WORKIZ_JOB_END_DATETIME_FIELD)).strip()
                        if raw_end:
                            try:
                                end_str = convert_pacific_to_utc(raw_end)
                            except Exception:
                                end_str = raw_end
                    if not end_str:
                        try:
                            dt_end = datetime.strptime(job_datetime_utc[:19], "%Y-%m-%d %H:%M:%S") + timedelta(hours=1)
                            end_str = dt_end.strftime("%Y-%m-%d %H:%M:%S")
                        except Exception:
                            pass
                    if end_str:
                        if ODOO_TASK_END_DATETIME_FIELD:
                            create_vals[ODOO_TASK_END_DATETIME_FIELD] = end_str
                        if ODOO_TASK_PLANNED_DATE_FIELD:
                            create_vals[ODOO_TASK_PLANNED_DATE_FIELD] = end_str
                    # allocated_hours: compute from start/end so duration clock shows correctly
                    try:
                        if end_str:
                            dt_s = datetime.strptime(job_datetime_utc[:19], "%Y-%m-%d %H:%M:%S")
                            dt_e = datetime.strptime(end_str[:19], "%Y-%m-%d %H:%M:%S")
                            create_vals["allocated_hours"] = max(round((dt_e - dt_s).total_seconds() / 3600, 2), 0.25)
                        else:
                            create_vals["allocated_hours"] = 1.0
                    except Exception:
                        create_vals["allocated_hours"] = 1.0
                # Create the task
                create_payload = {
                    "jsonrpc": "2.0", "method": "call",
                    "params": {
                        "service": "object", "method": "execute_kw",
                        "args": [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, "project.task", "create", [create_vals]]
                    }
                }
                try:
                    cr = requests.post(ODOO_URL, json=create_payload, timeout=10)
                    new_id = cr.json().get("result")
                    if new_id:
                        print(f"[OK] Backfilled task id={new_id} for order_line {ol_id} (name: {create_vals.get('name')})")
                        backfilled += 1
                    else:
                        print(f"[!] Backfill task create for line {ol_id} returned no id: {cr.json()}")
                except Exception as e:
                    print(f"[!] Backfill task create failed for line {ol_id}: {e}")
            if backfilled > 0:
                print(f"[OK] Backfilled {backfilled} task(s) for confirmed SO with no existing tasks")
                return _ret(tasks_found=backfilled, tasks_updated=True)
            return _ret(tasks_found=0, error="Backfill attempted but 0 tasks created")
        else:
            so_st = so_check[0].get("state") if so_check else "unknown"
            print(f"[!] No backfill: state={so_st}, substatus={wiz_substatus or wiz_status} (need state=sale + scheduling status)")
        return _ret(tasks_found=0, error="No tasks with sale_line_id in this SO's lines")
    n_tasks = len(task_ids)

    task_vals = {}

    # Assignee = tech/team (first team member name → lookup res.users; not hardcoded)
    team_raw = workiz_job.get("Team") or workiz_job.get("team") or []
    if isinstance(team_raw, list) and team_raw:
        first_name = None
        for m in team_raw:
            if isinstance(m, dict):
                first_name = m.get("Name") or m.get("name")
                if first_name:
                    break
        if first_name and ODOO_TASK_ASSIGNEE_FIELD:
            user_id = _odoo_find_user_id_by_name(str(first_name).strip())
            if user_id is not None:
                # user_ids is (6, 0, [id1, id2]) for many2many; user_id is integer for many2one
                if ODOO_TASK_ASSIGNEE_FIELD == "user_ids":
                    task_vals["user_ids"] = [(6, 0, [user_id])]
                else:
                    task_vals[ODOO_TASK_ASSIGNEE_FIELD] = user_id

    # Planned start/end: Odoo FSM requires planned_date_begin < date_end. Do NOT set date_deadline (date only) when we set planned_date_begin — it becomes midnight and fails "start before end".
    order_date_str = (job_datetime_utc or "").strip()
    if order_date_str:
        date_part = order_date_str.split()[0] if " " in order_date_str else order_date_str
        if ODOO_TASK_START_DATETIME_FIELD:
            task_vals[ODOO_TASK_START_DATETIME_FIELD] = order_date_str
        # Only set date_deadline when we're NOT setting planned_date_begin (otherwise midnight deadline fails constraint)
        if ODOO_TASK_PLANNED_DATE_FIELD and not ODOO_TASK_START_DATETIME_FIELD:
            task_vals[ODOO_TASK_PLANNED_DATE_FIELD] = date_part
        elif ODOO_TASK_PLANNED_DATE_FIELD and not task_vals.get(ODOO_TASK_START_DATETIME_FIELD):
            task_vals[ODOO_TASK_PLANNED_DATE_FIELD] = date_part
    # End datetime: from Workiz if set, else start + 1h so constraint "start before end" passes
    if WORKIZ_JOB_END_DATETIME_FIELD and workiz_job.get(WORKIZ_JOB_END_DATETIME_FIELD) and ODOO_TASK_END_DATETIME_FIELD:
        end_str = workiz_job.get(WORKIZ_JOB_END_DATETIME_FIELD)
        if end_str:
            end_str = str(end_str).strip()
            if " " in end_str and len(end_str) >= 19:
                try:
                    task_vals[ODOO_TASK_END_DATETIME_FIELD] = convert_pacific_to_utc(end_str)
                except Exception:
                    task_vals[ODOO_TASK_END_DATETIME_FIELD] = end_str
            else:
                task_vals[ODOO_TASK_END_DATETIME_FIELD] = end_str + " 17:00:00"
    elif ODOO_TASK_END_DATETIME_FIELD and order_date_str and task_vals.get(ODOO_TASK_START_DATETIME_FIELD):
        try:
            dt = datetime.strptime(order_date_str, "%Y-%m-%d %H:%M:%S")
            end_dt = dt + timedelta(hours=1)
            task_vals[ODOO_TASK_END_DATETIME_FIELD] = end_dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            pass
    # If we set start but no end yet (e.g. no Workiz end field), set end = start+1h so the write doesn't leave old end < new start
    if task_vals.get(ODOO_TASK_START_DATETIME_FIELD) and not task_vals.get(ODOO_TASK_END_DATETIME_FIELD) and ODOO_TASK_END_DATETIME_FIELD:
        try:
            dt = datetime.strptime(str(task_vals[ODOO_TASK_START_DATETIME_FIELD])[:19], "%Y-%m-%d %H:%M:%S")
            task_vals[ODOO_TASK_END_DATETIME_FIELD] = (dt + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            pass
    # Enforce planned_date_begin < date_end (Odoo constraint). If end <= start (e.g. bad Workiz end or timezone), set end = start + 1h
    start_val = task_vals.get(ODOO_TASK_START_DATETIME_FIELD)
    end_val = task_vals.get(ODOO_TASK_END_DATETIME_FIELD)
    if start_val and end_val and ODOO_TASK_END_DATETIME_FIELD:
        try:
            start_dt = datetime.strptime(str(start_val)[:19], "%Y-%m-%d %H:%M:%S")
            end_dt = datetime.strptime(str(end_val)[:19], "%Y-%m-%d %H:%M:%S")
            if end_dt <= start_dt:
                end_dt = start_dt + timedelta(hours=1)
                task_vals[ODOO_TASK_END_DATETIME_FIELD] = end_dt.strftime("%Y-%m-%d %H:%M:%S")
                end_val = task_vals[ODOO_TASK_END_DATETIME_FIELD]
        except Exception:
            pass
    # Keep deadline coherent with end datetime. In this DB date_deadline is datetime, so write full end datetime.
    if task_vals.get(ODOO_TASK_END_DATETIME_FIELD) and ODOO_TASK_PLANNED_DATE_FIELD:
        end_val = task_vals[ODOO_TASK_END_DATETIME_FIELD]
        if end_val:
            task_vals[ODOO_TASK_PLANNED_DATE_FIELD] = str(end_val)
    # allocated_hours (allocated time): compute from start/end so the clock icon fills in correctly
    start_val = task_vals.get(ODOO_TASK_START_DATETIME_FIELD)
    end_val = task_vals.get(ODOO_TASK_END_DATETIME_FIELD)
    if start_val and end_val:
        try:
            dt_s = datetime.strptime(str(start_val)[:19], "%Y-%m-%d %H:%M:%S")
            dt_e = datetime.strptime(str(end_val)[:19], "%Y-%m-%d %H:%M:%S")
            task_vals["allocated_hours"] = max(round((dt_e - dt_s).total_seconds() / 3600, 2), 0.25)
        except Exception:
            task_vals["allocated_hours"] = 1.0
    elif start_val:
        task_vals["allocated_hours"] = 1.0

    # SO: partner_id = Property (customer); partner_shipping_id = Property. Contact = Property.parent_id.
    so_list = _odoo_search_read("sale.order", [["id", "=", so_id]], ["partner_id", "partner_shipping_id", "tag_ids"], limit=1)
    if so_list:
        so = so_list[0]
        partner_id = so.get("partner_id")
        if partner_id is not None and ODOO_TASK_PARTNER_FIELD:
            pid = partner_id[0] if isinstance(partner_id, (list, tuple)) else partner_id
            if pid:
                task_vals[ODOO_TASK_PARTNER_FIELD] = pid
        if ODOO_TASK_PROPERTY_PARTNER_FIELD:
            shipping = so.get("partner_shipping_id")
            if shipping is not None:
                sid = shipping[0] if isinstance(shipping, (list, tuple)) else shipping
                if sid:
                    task_vals[ODOO_TASK_PROPERTY_PARTNER_FIELD] = sid
        # Task tags should come from Workiz job tags (UUID payload), not stale SO tags.
        # If no Workiz tags resolve, fallback to SO tags for compatibility.
        if ODOO_TASK_TAG_IDS_FIELD:
            task_tag_ids = _resolve_task_tag_ids_from_workiz(workiz_job)
            if task_tag_ids:
                task_vals[ODOO_TASK_TAG_IDS_FIELD] = [(6, 0, task_tag_ids)]
                print(f"[*] Task tags from Workiz UUID payload: {task_tag_ids}")
            else:
                tag_ids = so.get("tag_ids") or []
                ids = [t for t in tag_ids if isinstance(t, int)] or [t[0] for t in tag_ids if isinstance(t, (list, tuple)) and t]
                if ids:
                    task_vals[ODOO_TASK_TAG_IDS_FIELD] = [(6, 0, ids)]
                    print(f"[*] Task tags fallback from SO: {ids}")

    pid = task_vals.get(ODOO_TASK_PARTNER_FIELD)
    if (pid is None or not pid) and so_list and so_list[0].get("partner_id"):
        p = so_list[0].get("partner_id")
        pid = p[0] if isinstance(p, (list, tuple)) else p
    # Task name = "Customer Name - City" (customer = Contact; city from Property). SO partner is Property.
    if pid:
        prop = _odoo_search_read("res.partner", [["id", "=", pid]], ["name", "parent_id", "city"], limit=1)
        if prop:
            prop = prop[0]
            city = (prop.get("city") or "").strip()
            contact_id = prop.get("parent_id")
            if contact_id is not None:
                contact_id = contact_id[0] if isinstance(contact_id, (list, tuple)) else contact_id
            customer_name = (prop.get("name") or "").strip()
            if contact_id:
                contact = _odoo_search_read("res.partner", [["id", "=", contact_id]], ["name"], limit=1)
                if contact:
                    customer_name = (contact[0].get("name") or customer_name).strip()
            if customer_name or city:
                task_name = f"{customer_name} - {city}".strip(" - ").strip() if city else customer_name
                if task_name:
                    task_vals["name"] = task_name
    # Phone: SO partner is Property; phone lives on Contact. Get Contact via Property.parent_id.
    if pid and ODOO_TASK_PHONE_FIELD:
        partners = _odoo_search_read("res.partner", [["id", "=", pid]], ["phone", "parent_id"], limit=1)
        if partners:
            phone = (partners[0].get("phone") or "").strip()
            if not phone and partners[0].get("parent_id"):
                contact_id_phone = partners[0]["parent_id"][0] if isinstance(partners[0]["parent_id"], (list, tuple)) else partners[0]["parent_id"]
                contact_partners = _odoo_search_read("res.partner", [["id", "=", contact_id_phone]], ["phone"], limit=1)
                if contact_partners:
                    phone = (contact_partners[0].get("phone") or "").strip()
            if phone:
                task_vals[ODOO_TASK_PHONE_FIELD] = phone

    if not task_vals:
        print("[!] No task_vals to write (missing JobDateTime/Team/partner?); task sync skipped.")
        return _ret(tasks_found=n_tasks, error="No fields to write (JobDateTime/Team/partner missing?)")
    print(f"[*] Writing to {len(task_ids)} task(s): {list(task_vals.keys())}")
    payload_write = {
        "jsonrpc": "2.0", "method": "call",
        "params": {
            "service": "object", "method": "execute_kw",
            "args": [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, "project.task", "write", [task_ids, task_vals]]
        }
    }
    try:
        wr = requests.post(ODOO_URL, json=payload_write, timeout=10)
        resp = wr.json()
        if resp.get("error"):
            err = str(resp.get("error", ""))
            print(f"[ERROR] Task write failed: {err}")
            return _ret(tasks_found=n_tasks, error=f"Odoo write failed: {err}")
        print(f"[OK] Synced {len(task_ids)} task(s): assignee, planned date, tags, customer, contact number")
        return _ret(tasks_found=n_tasks, tasks_updated=True)
    except Exception as e:
        print(f"[ERROR] Task write exception: {e}")
        return _ret(tasks_found=n_tasks, error=f"Task write exception: {e}")


def confirm_sales_order(so_id, date_order_utc=None):
    """Confirm a draft SO (quotation → sales order); Odoo then creates tasks for lines with 'Create on Order = Task'.
    If date_order_utc provided, writes it back after confirm (Odoo resets date_order to now() during action_confirm)."""
    payload = {
        "jsonrpc": "2.0", "method": "call",
        "params": {
            "service": "object", "method": "execute_kw",
            "args": [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, "sale.order", "action_confirm", [[so_id]]]
        }
    }
    try:
        requests.post(ODOO_URL, json=payload, timeout=10)
        print("[OK] Confirmed draft SO → sales order (tasks created)")
        if date_order_utc:
            # Odoo's action_confirm() internally resets date_order to datetime.now().
            # This only surfaces when Phase 4 confirms an *existing* draft SO (e.g. user
            # changes status to Pending Scheduled on a job whose SO was never confirmed).
            # When creating a new SO, the date in the creation payload wins because confirm
            # happens in the same request. On the update path it doesn't — so we write it back.
            # Fixed 2026-04-01 after SO 004253 showed current date instead of Workiz JobDateTime.
            write_payload = {
                "jsonrpc": "2.0", "method": "call",
                "params": {
                    "service": "object", "method": "execute_kw",
                    "args": [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, "sale.order", "write", [[so_id], {"date_order": date_order_utc}]]
                }
            }
            requests.post(ODOO_URL, json=write_payload, timeout=10)
            print(f"[*] Restored date_order after confirm: {date_order_utc}")
        return True
    except Exception:
        return False


def sync_task_planned_date_to_order_date(so_id, order_date_str):
    """
    Legacy: set only planned date on tasks. Prefer sync_tasks_from_so_and_job for full sync.
    """
    if not order_date_str or not str(order_date_str).strip():
        return
    order_date_str = str(order_date_str).strip()
    date_part = order_date_str.split()[0] if " " in order_date_str else order_date_str
    lines = _odoo_search_read("sale.order.line", [["order_id", "=", so_id]], ["id"], limit=500)
    line_ids = [x["id"] for x in lines]
    if not line_ids:
        return
    payload_tasks = {
        "jsonrpc": "2.0", "method": "call",
        "params": {
            "service": "object", "method": "execute_kw",
            "args": [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, "project.task", "search", [[["sale_line_id", "in", line_ids]]]]
        }
    }
    try:
        r = requests.post(ODOO_URL, json=payload_tasks, timeout=10)
        task_ids = r.json().get("result", [])
    except Exception:
        return
    if not task_ids or not ODOO_TASK_PLANNED_DATE_FIELD:
        return
    payload_write = {
        "jsonrpc": "2.0", "method": "call",
        "params": {
            "service": "object", "method": "execute_kw",
            "args": [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, "project.task", "write", [task_ids, {ODOO_TASK_PLANNED_DATE_FIELD: date_part}]]
        }
    }
    try:
        requests.post(ODOO_URL, json=payload_write, timeout=10)
    except Exception:
        pass


def format_serial_id(serial_id):
    """Format Workiz SerialId as 6-digit string with leading zeros."""
    try:
        return str(int(serial_id)).zfill(6)
    except:
        return str(serial_id)

def convert_pacific_to_utc(pacific_datetime_str):
    """
    Convert Pacific time string to UTC.
    Args:
        pacific_datetime_str (str): Pacific time (e.g., "2026-03-12 08:30:00")
    Returns:
        str: UTC time formatted as "YYYY-MM-DD HH:MM:SS"
    """
    # DST-aware: 10:00 Pacific must become correct UTC so Odoo shows 10:00 (not 11:00)
    dt_naive = datetime.strptime(pacific_datetime_str, '%Y-%m-%d %H:%M:%S')
    try:
        from zoneinfo import ZoneInfo
        pacific = ZoneInfo('America/Los_Angeles')
        dt_pacific = dt_naive.replace(tzinfo=pacific)
        dt_utc = dt_pacific.astimezone(ZoneInfo('UTC'))
        return dt_utc.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        # Fallback: PST=+8, PDT=+7 by month
        offset_hours = 8 if dt_naive.month in (11, 12, 1, 2) or (dt_naive.month == 3 and dt_naive.day < 10) else 7
        dt_utc = dt_naive + timedelta(hours=offset_hours)
        return dt_utc.strftime('%Y-%m-%d %H:%M:%S')



def is_task_trigger_status(status_value, substatus_value):
    """Return True only for explicit scheduling states/substates that should create/sync tasks."""
    allowed_values = {
        "next appointment - text",
        "send confirmation - text",
        "scheduled",
    }

    def _norm(v):
        return " ".join((v or "").strip().lower().split())

    status_text = _norm(status_value)
    substatus_text = _norm(substatus_value)
    return status_text in allowed_values or substatus_text in allowed_values



def _normalize_address_for_match(address):
    """Normalize street text for robust property matching (Ct vs Court, punctuation, spacing)."""
    if not address:
        return ""
    text = str(address).strip().lower()
    replacements = {
        ".": " ",
        ",": " ",
        "#": " ",
    }
    for a, b in replacements.items():
        text = text.replace(a, b)
    tokens = [t for t in text.split() if t]
    norm_map = {
        "ct": "court",
        "rd": "road",
        "dr": "drive",
        "ln": "lane",
        "ave": "avenue",
        "blvd": "boulevard",
        "st": "street",
    }
    normalized = [norm_map.get(tok, tok) for tok in tokens]
    return " ".join(normalized)


def _rebind_so_to_matching_property_if_needed(so_id, workiz_job):
    """If UUID-matched SO is bound to wrong property, rebind partner/shipping to the contact's matching property."""
    service_address = (workiz_job.get('Address') or '').strip()
    if not service_address:
        return None

    so_rows = _odoo_search_read('sale.order', [["id", "=", so_id]], ["partner_id", "partner_shipping_id"], limit=1)
    if not so_rows:
        return None

    so = so_rows[0]
    shipping = so.get('partner_shipping_id') or so.get('partner_id')
    shipping_id = shipping[0] if isinstance(shipping, (list, tuple)) else shipping
    if not shipping_id:
        return None

    prop_rows = _odoo_search_read('res.partner', [["id", "=", shipping_id]], ["id", "street", "parent_id"], limit=1)
    if not prop_rows:
        return None

    current_prop = prop_rows[0]
    current_street = (current_prop.get('street') or '').strip()
    contact = current_prop.get('parent_id')
    contact_id = contact[0] if isinstance(contact, (list, tuple)) else contact
    if not contact_id:
        return None

    if _normalize_address_for_match(current_street) == _normalize_address_for_match(service_address):
        return None

    # Try exact first, then normalized contains-match on this contact's properties.
    exact = _odoo_search_read(
        'res.partner',
        [["street", "=", service_address], ["parent_id", "=", contact_id], ["x_studio_x_studio_record_category", "=", "Property"]],
        ["id", "street"],
        limit=1,
    )
    target = exact[0] if exact else None

    if not target:
        candidates = _odoo_search_read(
            'res.partner',
            [["parent_id", "=", contact_id], ["x_studio_x_studio_record_category", "=", "Property"]],
            ["id", "street"],
            limit=100,
        )
        target_norm = _normalize_address_for_match(service_address)
        for c in candidates:
            c_norm = _normalize_address_for_match(c.get('street') or '')
            if c_norm == target_norm:
                target = c
                break

    if not target:
        print(f"[!] SO {so_id} property mismatch detected, but no matching property found for address: {service_address}")
        return None

    target_id = target['id']
    if target_id == shipping_id:
        return None

    updates = {
        'partner_id': int(target_id),
        'partner_invoice_id': int(target_id),
        'partner_shipping_id': int(target_id),
    }
    ok = update_sales_order(so_id, updates)
    if ok:
        print(f"[OK] Rebound SO {so_id} to property {target_id} for address '{service_address}'")
        return target_id

    print(f"[!] Failed to rebind SO {so_id} to property {target_id}")
    return None

def format_team_names(team_raw):
    """Extract team member names from Workiz team data."""
    if not team_raw:
        return ""
    
    if isinstance(team_raw, list):
        names = []
        for member in team_raw:
            if isinstance(member, dict):
                name = member.get('Name') or member.get('name', '')
                if name:
                    names.append(str(name).strip())
            elif member:
                names.append(str(member).strip())
        return ", ".join(names)
    elif isinstance(team_raw, str):
        return team_raw.strip()
    return ""

def extract_tip_from_line_items(line_items):
    """Extract tip amount from Workiz job line items."""
    if not line_items or not isinstance(line_items, list):
        return 0.0
    
    for item in line_items:
        item_name = item.get('Name', '').lower()
        if 'tip' in item_name:
            return float(item.get('Price', 0))
    
    return 0.0


# ==============================================================================
# WORKIZ API FUNCTIONS
# ==============================================================================

def get_job_details(job_uuid):
    """Fetch full job details from Workiz API."""
    url = f'{WORKIZ_BASE_URL}/job/get/{job_uuid}/?auth_secret={WORKIZ_AUTH_SECRET}'
    
    try:
        response = requests.get(url, timeout=10)
        result = response.json()
        
        if result.get('flag'):
            job_data = result['data'][0]
            print("[OK] Workiz job data fetched successfully")
            return job_data
        else:
            print(f"[ERROR] Workiz API returned flag=False: {result.get('msg')}")
            return None
    except Exception as e:
        print(f"[ERROR] Failed to fetch Workiz job: {e}")
        return None


# ==============================================================================
# ODOO API FUNCTIONS - SEARCH/READ
# ==============================================================================

def search_contact_by_client_id(client_id):
    """Search for Contact by Workiz ClientId (ref field)."""
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB, ODOO_USER_ID, ODOO_API_KEY,
                "res.partner", "search_read",
                [[
                    ["x_studio_x_studio_record_category", "=", "Contact"],
                    ["ref", "=", str(client_id)]
                ]],
                {"fields": ["id", "name", "ref"], "limit": 1}
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result and len(result) > 0:
        contact = result[0]
        print(f"[OK] Contact found: {contact['name']} (ID: {contact['id']}, ClientId: {contact['ref']})")
        return {'contact_id': contact['id'], 'name': contact['name'], 'ref': contact['ref']}
    return None

def search_property_for_contact(service_address, contact_id):
    """Search for Property by address and linked Contact."""
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB, ODOO_USER_ID, ODOO_API_KEY,
                "res.partner", "search_read",
                [[
                    ["street", "=", service_address],
                    ["parent_id", "=", contact_id],
                    ["x_studio_x_studio_record_category", "=", "Property"]
                ]],
                {"fields": ["id", "name", "street"], "limit": 1}
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result and len(result) > 0:
        prop = result[0]
        print(f"[OK] Property found: {prop['street']} (ID: {prop['id']})")
        return {'property_id': prop['id'], 'name': prop['name'], 'street': prop['street']}
    return None

def search_sales_order_by_uuid(workiz_uuid):
    """Search for Sales Order by Workiz UUID."""
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB, ODOO_USER_ID, ODOO_API_KEY,
                "sale.order", "search_read",
                [[["x_studio_x_studio_workiz_uuid", "=", workiz_uuid]]],
                {
                    "fields": ["id", "name", "partner_id", "partner_shipping_id", "x_studio_x_studio_workiz_uuid", "state"],
                    "limit": 1
                }
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result", [])
    
    if result and len(result) > 0:
        return result[0]
    return None


# ==============================================================================
# ODOO API FUNCTIONS - CREATE
# ==============================================================================

def create_contact(first_name, last_name, phone, email, address, city, postal_code, client_id):
    """Create a new Contact in Odoo."""
    full_name = f"{first_name} {last_name}".strip()
    
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB, ODOO_USER_ID, ODOO_API_KEY,
                "res.partner", "create",
                [{
                    "name": full_name,
                    "ref": str(client_id),
                    "x_studio_x_studio_first_name": first_name,
                    "x_studio_x_studio_last_name": last_name,
                    "phone": phone,
                    "email": email,
                    "street": address,
                    "city": city,
                    "zip": postal_code,
                    "state_id": 13,
                    "x_studio_x_studio_record_category": "Contact"
                }]
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    contact_id = response.json().get("result")
    
    if contact_id:
        print(f"[OK] Contact created: {full_name} (ID: {contact_id})")
        return contact_id
    return None

def create_property(address, city, postal_code, contact_id, location_id, frequency, type_of_service, alternating, contact_name=None):
    """Create a new Property in Odoo. Name = 'Contact Name, Address' for SO list display when contact_name provided."""
    # Convert alternating 1/0 to Yes/No
    alternating_text = ""
    if alternating:
        alternating_text = "Yes" if str(alternating) == "1" else "No" if str(alternating) == "0" else alternating
    
    # SO Customer column shows partner name; use "Contact Name, Address" when we have contact name
    contact_name = (contact_name or "").strip()
    property_display_name = f"{contact_name}, {address}".strip(", ").strip() if contact_name else address
    
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB, ODOO_USER_ID, ODOO_API_KEY,
                "res.partner", "create",
                [{
                    "name": property_display_name,
                    "street": address,
                    "parent_id": contact_id,
                    "x_studio_x_studio_record_category": "Property",
                    "city": city,
                    "zip": postal_code,
                    "state_id": 13,
                    "x_studio_x_studio_location_id": str(location_id) if location_id else "",
                    "x_studio_x_frequency": frequency or "",
                    "x_studio_x_type_of_service": type_of_service or "",
                    "x_studio_x_alternating": alternating_text
                }]
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    property_id = response.json().get("result")
    
    if property_id:
        print(f"[OK] Property created: {address} (ID: {property_id})")
        return property_id
    return None


def find_opportunity_by_graveyard_uuid(job_uuid):
    """Search for Opportunity with this Workiz graveyard UUID."""
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
                "crm.lead",
                "search_read",
                [[["x_workiz_graveyard_uuid", "=", job_uuid]]],
                {"fields": ["id", "name", "x_workiz_graveyard_uuid"], "limit": 1}
            ]
        }
    }
    
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json()
        
        if result.get("result") and len(result["result"]) > 0:
            opp = result["result"][0]
            print(f"[OK] Opportunity found for graveyard UUID {job_uuid}: {opp['name']} (ID: {opp['id']})")
            return opp
        else:
            return None
    except Exception as e:
        print(f"[ERROR] Failed to search for Opportunity: {e}")
        return None


def mark_opportunity_won(opportunity_id):
    """Mark Odoo opportunity as Won using action_set_won."""
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
                "crm.lead",
                "action_set_won",
                [[opportunity_id]]
            ]
        }
    }
    
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json()
        
        if result.get("result") is not None:
            print(f"[OK] Opportunity {opportunity_id} marked as Won!")
            return {'success': True}
        else:
            return {'success': False, 'message': 'action_set_won failed'}
    except Exception as e:
        print(f"[ERROR] Failed to mark Opportunity Won: {e}")
        return {'success': False, 'message': str(e)}


# ==============================================================================
# ODOO API FUNCTIONS - UPDATE
# ==============================================================================

def analyze_service_type_from_so(so_id):
    """
    Analyze products in Sales Order to determine service types.
    Returns: (has_window: bool, has_solar: bool, service_type: str)
    service_type values: 'windows', 'solar', 'both', 'other'
    """
    lines = _odoo_search_read("sale.order.line", [["order_id", "=", so_id]], ["product_id", "name"], limit=500)
    
    if not lines:
        return (False, False, 'other')
    
    has_window = False
    has_solar = False
    
    for line in lines:
        product_name = ""
        if line.get('product_id'):
            product_name = line['product_id'][1] if isinstance(line['product_id'], list) else ""
        if not product_name:
            product_name = line.get('name', '')
        
        if not product_name:
            continue
        
        product_lower = product_name.lower()
        
        # Skip non-service items
        if any(x in product_lower for x in ['tip', 'discount', 'legacy', 'quote']):
            continue
        
        # Detect service type
        if 'window' in product_lower:
            has_window = True
        elif 'solar' in product_lower:
            has_solar = True
    
    # Determine service_type value
    if has_window and has_solar:
        service_type = 'both'
    elif has_window:
        service_type = 'windows'
    elif has_solar:
        service_type = 'solar'
    else:
        service_type = 'other'
    
    return (has_window, has_solar, service_type)


def update_property_fields(property_id, gate_code=None, pricing=None, last_visit_date=None, 
                          job_notes=None, comments=None, frequency=None, alternating=None, 
                          type_of_service=None, has_window=None, has_solar=None, 
                          most_recent_service_type=None):
    """Update property fields in Odoo (including service tracking fields)."""
    updates = {}
    
    if gate_code is not None:
        updates['x_studio_x_gate_code'] = str(gate_code)
    
    if pricing is not None:
        updates['x_studio_x_pricing'] = str(pricing)
    
    if last_visit_date is not None:
        # Race condition protection: only update if new date is newer than existing
        existing = _odoo_search_read("res.partner", [["id", "=", property_id]], 
                                     ["x_studio_x_studio_last_property_visit"], limit=1)
        current_date = existing[0].get('x_studio_x_studio_last_property_visit') if existing else None
        
        if not current_date or last_visit_date > current_date:
            updates['x_studio_x_studio_last_property_visit'] = last_visit_date
            print(f"[*] Property last visit: {current_date} -> {last_visit_date} (updated)")
        else:
            print(f"[*] Property last visit: {current_date} (keeping - new date {last_visit_date} is older, skipped)")

    
    if frequency is not None:
        updates['x_studio_x_frequency'] = str(frequency)
    
    if type_of_service is not None:
        updates['x_studio_x_type_of_service'] = str(type_of_service)
    
    if alternating is not None:
        alternating_text = "Yes" if str(alternating) == "1" else "No" if str(alternating) == "0" else alternating
        updates['x_studio_x_alternating'] = str(alternating_text)
    
    # NEW: Service tracking fields
    if has_window is not None:
        updates['x_studio_has_window_service'] = has_window
    
    if has_solar is not None:
        updates['x_studio_has_solar_service'] = has_solar
    
    if most_recent_service_type is not None:
        updates['x_studio_most_recent_service_type'] = most_recent_service_type
    
    if job_notes or comments:
        combined_notes = ""
        if job_notes:
            combined_notes += f"[Job Notes]\n{job_notes}\n\n"
        if comments:
            combined_notes += f"[Comments]\n{comments}"
        updates['comment'] = combined_notes.strip()
    
    if not updates:
        return True
    
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB, ODOO_USER_ID, ODOO_API_KEY,
                "res.partner", "write",
                [[property_id], updates]
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result")
    
    if result:
        print(f"[OK] Property updated successfully (including service tracking)")
        return True
    return False

def _find_product_id_by_workiz_code(workiz_code):
    """Return Odoo product id where x_studio_x_studio_workiz_product_number matches workiz_code, or None."""
    if workiz_code is None or str(workiz_code).strip() == '':
        return None
    code = str(workiz_code).strip()
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB, ODOO_USER_ID, ODOO_API_KEY,
                "product.product", "search_read",
                [[[ODOO_PRODUCT_WORKIZ_CODE_FIELD, "=", code]]],
                {"fields": ["id"], "limit": 1}
            ]
        }
    }
    resp = requests.post(ODOO_URL, json=payload, timeout=10)
    result = resp.json().get("result", [])
    return result[0]["id"] if result else None


def _find_product_id_by_name(product_name):
    """Return Odoo product id for exact name, or None."""
    if not product_name or not str(product_name).strip():
        return None
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB, ODOO_USER_ID, ODOO_API_KEY,
                "product.product", "search_read",
                [[["name", "=", str(product_name).strip()]]],
                {"fields": ["id"], "limit": 1}
            ]
        }
    }
    resp = requests.post(ODOO_URL, json=payload, timeout=10)
    result = resp.json().get("result", [])
    return result[0]["id"] if result else None


def build_order_line_commands(line_items):
    """
    Build Odoo order_line commands from Workiz LineItems.
    Match by Workiz product code (x_studio_x_studio_workiz_product_number) first; fallback to product name then 'Service'.
    Skips lines when no product can be found (Odoo requires product_id on order lines).
    """
    if not line_items or not isinstance(line_items, list):
        return []
    order_lines = []
    for item in line_items:
        item_name = item.get('Name', 'Service') or 'Service'
        item_desc = item.get('Description', '')
        item_qty = float(item.get('Quantity', 1))
        item_price = float(item.get('Price', 0))
        # Workiz product code: from GET job/get LineItems (Workiz_API_Test_Results.md): ModelNum, Id
        workiz_code = item.get('ModelNum') or item.get('Id')
        if workiz_code is not None and str(workiz_code).strip() != '':
            product_id = _find_product_id_by_workiz_code(workiz_code)
        else:
            product_id = None
        if product_id is None:
            product_id = _find_product_id_by_name(item_name)
        if product_id is None and item_name != 'Service':
            product_id = _find_product_id_by_name('Service')
        if product_id is None:
            print(f"[!] Skipping line item '{item_name}' (code={workiz_code}): no matching product in Odoo (set {ODOO_PRODUCT_WORKIZ_CODE_FIELD} or add 'Service')")
            continue
        order_line_vals = {
            'product_id': product_id,
            'name': f"{item_name}\n{item_desc}" if item_desc else item_name,
            'product_uom_qty': item_qty,
            'price_unit': item_price,
        }
        order_lines.append((0, 0, order_line_vals))
    return order_lines


def build_confirmed_so_line_commands(so_id, line_items):
    """
    Build line item update commands for CONFIRMED Sales Orders (state='sale').
    
    For confirmed SOs, Odoo doesn't allow deleting lines. Instead:
    - Update existing line prices/quantities
    - Add new lines
    - Set quantity to 0 for removed lines
    
    Returns: list of Odoo write commands [(1, line_id, vals), (0, 0, vals), ...]
    """
    print(f"[*] build_confirmed_so_line_commands called: {len(line_items) if line_items else 0} Workiz items")
    
    if not line_items or not isinstance(line_items, list):
        # No line items from Workiz - set all existing lines to qty=0
        print("[*] No line items from Workiz - will set all Odoo lines to qty=0")
        existing_lines = _odoo_search_read("sale.order.line", [["order_id", "=", so_id]], 
                                           ["id", "name", "product_uom_qty"], limit=100)
        if existing_lines:
            commands = []
            for line in existing_lines:
                if line['product_uom_qty'] > 0:
                    commands.append((1, line['id'], {'product_uom_qty': 0}))
                    print(f"[*] Setting qty to 0 (no Workiz items): line {line['id']}")
            return commands
        return []
    
    # Fetch existing SO lines with their product IDs (limit=100 to get all lines, not just first one)
    existing_lines = _odoo_search_read("sale.order.line", [["order_id", "=", so_id]], 
                                       ["id", "product_id", "name", "price_unit", "product_uom_qty"], limit=100)
    
    print(f"[*] Found {len(existing_lines) if existing_lines else 0} existing lines in Odoo SO")
    
    if not existing_lines:
        print("[*] No existing lines found on SO - will add new lines")
        existing_lines = []
    
    # Track which line IDs we've updated (to know which ones to set qty=0)
    updated_line_ids = set()
    
    # Build commands
    commands = []
    
    # Process each Workiz line item
    for item in line_items:
        item_name = item.get('Name', 'Service') or 'Service'
        item_desc = item.get('Description', '')
        item_qty = float(item.get('Quantity', 1))
        item_price = float(item.get('Price', 0))
        workiz_code = item.get('ModelNum') or item.get('Id')
        
        # Find matching Odoo product
        if workiz_code is not None and str(workiz_code).strip() != '':
            product_id = _find_product_id_by_workiz_code(workiz_code)
        else:
            product_id = None
        if product_id is None:
            product_id = _find_product_id_by_name(item_name)
        if product_id is None and item_name != 'Service':
            product_id = _find_product_id_by_name('Service')
        
        if product_id is None:
            print(f"[!] Skipping line item '{item_name}': no matching product in Odoo")
            continue
        
        # Find best matching existing line (prefer matching product_id, then first unused line with qty > 0)
        best_match = None
        for line in existing_lines:
            if line['id'] in updated_line_ids:
                continue  # Already matched to a Workiz item
            
            pid = line['product_id']
            line_product_id = pid[0] if isinstance(pid, (list, tuple)) else pid
            
            if line_product_id == product_id:
                best_match = line
                break
        
        if best_match:
            # UPDATE existing line
            line_id = best_match['id']
            updated_line_ids.add(line_id)
            
            # Only update if price or qty changed
            needs_update = False
            update_vals = {}
            
            if abs(best_match['price_unit'] - item_price) > 0.01:
                update_vals['price_unit'] = item_price
                needs_update = True
            
            if abs(best_match['product_uom_qty'] - item_qty) > 0.01:
                update_vals['product_uom_qty'] = item_qty
                needs_update = True
            
            # Update description if changed
            new_desc = f"{item_name}\n{item_desc}" if item_desc else item_name
            if best_match['name'] != new_desc:
                update_vals['name'] = new_desc
                needs_update = True
            
            if needs_update:
                commands.append((1, line_id, update_vals))
                print(f"[*] Updating line {line_id}: {item_name} - ${item_price}")
            else:
                updated_line_ids.add(line_id)  # Mark as touched even if no changes
        else:
            # ADD new line (no matching line found)
            line_vals = {
                'product_id': product_id,
                'name': f"{item_name}\n{item_desc}" if item_desc else item_name,
                'product_uom_qty': item_qty,
                'price_unit': item_price,
            }
            commands.append((0, 0, line_vals))
            print(f"[*] Adding new line: {item_name} - ${item_price}")
    
    # Set qty to 0 for Odoo lines NOT matched to any Workiz item (controlled by flag)
    if ENABLE_LINE_ITEM_REMOVAL_ON_CONFIRMED_SO:
        for line in existing_lines:
            if line['id'] not in updated_line_ids and line['product_uom_qty'] > 0:
                commands.append((1, line['id'], {'product_uom_qty': 0}))
                print(f"[*] Setting qty to 0 for unmatched line {line['id']}: {line['name']}")
    else:
        print("[*] ENABLE_LINE_ITEM_REMOVAL_ON_CONFIRMED_SO=False; skipping qty=0 for unmatched lines")
    
    print(f"[*] Built {len(commands)} line item command(s) for confirmed SO")
    return commands


def update_sales_order(so_id, updates):
    """Update Sales Order fields in Odoo. On failure, logs Odoo error and returns False."""
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB, ODOO_USER_ID, ODOO_API_KEY,
                "sale.order", "write",
                [[so_id], updates]
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    data = response.json()
    result = data.get("result")
    if result is True:
        return True
    # Log Odoo error so we can see why write failed (e.g. product required on order line)
    err = data.get("error")
    if err:
        msg = err.get("data", {}).get("message") or err.get("message") or str(err)
        print(f"[ERROR] Odoo write failed: {msg}")
    return False

def post_chatter_message(so_id, message):
    """Post a message to the Sales Order chatter."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message_with_timestamp = f"[{timestamp}] {message}"
    
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB, ODOO_USER_ID, ODOO_API_KEY,
                "sale.order", "message_post",
                [so_id],
                {"body": message_with_timestamp}
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json()
    
    return "result" in result


def post_opportunity_chatter(opp_id, message):
    """Post a message to the Opportunity (crm.lead) chatter with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message_with_timestamp = f"[{timestamp}] {message}"
    
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB, ODOO_USER_ID, ODOO_API_KEY,
                "crm.lead", "message_post",
                [opp_id],
                {"body": message_with_timestamp}
            ]
        }
    }
    
    try:
        response = requests.post(ODOO_URL, json=payload, timeout=10)
        result = response.json()
        return "result" in result
    except Exception as e:
        print(f"[ERROR] Failed to post to Opportunity chatter: {e}")
        return False


# ==============================================================================
# ODOO API FUNCTIONS - SALES ORDER
# ==============================================================================

def create_sales_order(contact_id, property_id, workiz_job_data, skip_confirm=False):
    """Create Sales Order in Odoo from Workiz job data. Idempotent: if SO already exists for this job UUID, returns it without creating duplicate.
    skip_confirm=True: create SO as draft (no action_confirm) so Odoo does not auto-create tasks — use when Phase 4 is backfilling a missing SO."""
    
    # Extract Workiz data
    workiz_uuid = workiz_job_data.get('UUID', '')
    if workiz_uuid:
        existing = search_sales_order_by_uuid(workiz_uuid)
        if existing:
            print(f"[*] SO already exists for this job (idempotent), returning existing ID {existing['id']}")
            return existing['id']
    
    workiz_link = f"https://app.workiz.com/root/job/{workiz_uuid}/1"
    workiz_substatus = workiz_job_data.get('SubStatus', '') or workiz_job_data.get('Status', '')
    job_source = workiz_job_data.get('JobSource', '')
    
    tags = workiz_job_data.get('Tags') or workiz_job_data.get('JobTags', '')
    if isinstance(tags, str):
        try:
            tags = ast.literal_eval(tags)
        except:
            tags = [t.strip() for t in tags.split(',') if t.strip()]
    
    gate_code_raw = workiz_job_data.get('gate_code', '')
    pricing_raw = workiz_job_data.get('pricing', '')
    job_notes = workiz_job_data.get('JobNotes') or workiz_job_data.get('Notes', '')
    info_to_remember = workiz_job_data.get('information_to_remember') or workiz_job_data.get('InformationToRemember', '')
    comments = workiz_job_data.get('Comments') or workiz_job_data.get('Comment', '')
    job_type = workiz_job_data.get('JobType') or workiz_job_data.get('Type', '')
    line_items_raw = workiz_job_data.get('LineItems', [])
    team_raw = workiz_job_data.get('Team') or workiz_job_data.get('team', '')
    
    # Filter placeholder text - convert to string first to handle integers
    gate_code = gate_code_raw if gate_code_raw and str(gate_code_raw).lower() not in ['gate code', 'gate', ''] else ''
    pricing = pricing_raw if pricing_raw and str(pricing_raw).lower() not in ['pricing', 'price', 'pricing note', ''] else ''
    
    # Process Team field
    team_names = format_team_names(team_raw)
    
    # Parse line items
    if isinstance(line_items_raw, str):
        try:
            line_items = ast.literal_eval(line_items_raw)
        except:
            line_items = []
    else:
        line_items = line_items_raw if line_items_raw else []
    
    # Build order lines (match by Workiz product code x_studio_x_studio_workiz_product_number, then name)
    order_lines = build_order_line_commands(line_items)
    
    # Get serial ID for order name
    serial_id = workiz_job_data.get('SerialId', '')
    order_name = format_serial_id(serial_id)
    
    # Combine job notes and comments
    notes_snapshot = ""
    if job_notes:
        notes_snapshot += f"[Job Notes]\n{job_notes}\n\n"
    if comments:
        notes_snapshot += f"[Comments]\n{comments}"
    notes_snapshot = notes_snapshot.strip()
    
    # Get contact tags
    contact_tags_payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB, ODOO_USER_ID, ODOO_API_KEY,
                "res.partner", "search_read",
                [[["id", "=", contact_id]]],
                {"fields": ["category_id"]}
            ]
        }
    }
    
    contact_response = requests.post(ODOO_URL, json=contact_tags_payload, timeout=10)
    contact_result = contact_response.json().get("result", [])
    contact_tag_ids = []
    if contact_result:
        category_id = contact_result[0].get('category_id')
        if category_id:
            if isinstance(category_id, list):
                contact_tag_ids = [tag_id for tag_id, _ in category_id] if category_id else []
            else:
                contact_tag_ids = [category_id]
    
    # Search for Workiz tags in Odoo
    workiz_tag_ids = []
    if tags and isinstance(tags, list):
        for tag_name in tags:
            tag_search_payload = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "service": "object",
                    "method": "execute_kw",
                    "args": [
                        ODOO_DB, ODOO_USER_ID, ODOO_API_KEY,
                        "crm.tag", "search_read",
                        [[["name", "=", tag_name]]],
                        {"fields": ["id"], "limit": 1}
                    ]
                }
            }
            tag_response = requests.post(ODOO_URL, json=tag_search_payload, timeout=10)
            tag_result = tag_response.json().get("result", [])
            if tag_result:
                workiz_tag_ids.append(tag_result[0]['id'])
    
    all_tag_ids = list(set(contact_tag_ids + workiz_tag_ids))
    
    # Build order data. Property as brain: customer and billing = Property. Contact linked via Property.parent_id.
    order_data = {
        "name": order_name,
        "partner_id": property_id,
        "partner_invoice_id": property_id,
        "partner_shipping_id": property_id,
        "x_studio_x_studio_workiz_uuid": workiz_uuid,
        "x_studio_x_workiz_link": workiz_link,
        "x_studio_x_studio_workiz_status": workiz_substatus,
        "x_studio_x_studio_lead_source": job_source
    }
    
    # Set date_order from JobDateTime BEFORE creating SO (so Odoo doesn't default to current time)
    job_datetime_str = workiz_job_data.get('JobDateTime', '')
    # DEBUG: Uncomment to verify date extraction
    # print(f"[DEBUG] Extracted JobDateTime from Workiz: '{job_datetime_str}'")
    if job_datetime_str:
        job_datetime_utc = convert_pacific_to_utc(job_datetime_str)
        order_data['date_order'] = job_datetime_utc
        print(f"[*] Setting SO date_order: {job_datetime_utc} (from Workiz JobDateTime: {job_datetime_str})")
    else:
        print("[WARNING] No JobDateTime found in Workiz data - Odoo will default date_order to current time")
    
    if job_type:
        order_data["x_studio_x_studio_x_studio_job_type"] = job_type
    
    if team_names:
        order_data["x_studio_x_studio_workiz_tech"] = team_names
    
    if gate_code:
        order_data["x_studio_x_gate_snapshot"] = gate_code
    
    if pricing:
        order_data["x_studio_x_studio_pricing_snapshot"] = pricing
    
    if notes_snapshot:
        order_data["x_studio_x_studio_notes_snapshot1"] = notes_snapshot
    
    if all_tag_ids:
        order_data["tag_ids"] = [(6, 0, all_tag_ids)]
    
    if order_lines:
        order_data["order_line"] = order_lines
        # Products that create tasks require a project on the quotation; set default so create succeeds
        if DEFAULT_PROJECT_ID:
            order_data[ODOO_SO_PROJECT_FIELD] = DEFAULT_PROJECT_ID

    # Create SO
    create_payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB, ODOO_USER_ID, ODOO_API_KEY,
                "sale.order", "create",
                [order_data]
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=create_payload, timeout=10)
    so_id = response.json().get("result")
    
    if not so_id:
        print("[ERROR] Failed to create sales order")
        return None
    
    print(f"[OK] Sales order created: ID {so_id}")
    
    # Confirm the SO (unless backfill: skip so Odoo does not create tasks)
    if not skip_confirm:
        confirm_payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [
                    ODOO_DB, ODOO_USER_ID, ODOO_API_KEY,
                    "sale.order", "action_confirm",
                    [[so_id]]
                ]
            }
        }
        requests.post(ODOO_URL, json=confirm_payload, timeout=10)
    else:
        print("[*] SO left as draft (no confirm → no task created).")
    
    return so_id


# ==============================================================================
# PHASE 3: PATH EXECUTION FUNCTIONS
# ==============================================================================

def execute_path_a(contact_id, property_id, workiz_job, skip_confirm=False):
    """PATH A: Both Contact and Property exist. skip_confirm=True = backfill (no confirm → no tasks)."""
    print("\n" + "="*70)
    print("EXECUTING PATH A: Existing Contact + Existing Property")
    print("="*70)
    
    so_id = create_sales_order(contact_id, property_id, workiz_job, skip_confirm=skip_confirm)
    if not so_id:
        return {'success': False, 'error': 'Failed to create sales order'}
    
    gate_code = workiz_job.get('gate_code', '')
    pricing = workiz_job.get('pricing', '')
    job_notes = workiz_job.get('JobNotes', '')
    comments = workiz_job.get('Comments', '')
    frequency = workiz_job.get('frequency', '')
    alternating = workiz_job.get('alternating', '')
    type_of_service = workiz_job.get('type_of_service_2') or workiz_job.get('type_of_service', '')
    
    update_property_fields(property_id, gate_code, pricing, None, job_notes, comments, frequency, alternating, type_of_service)
    
    print("="*70)
    print("[OK] PATH A COMPLETE")
    print("="*70)
    
    return {
        'success': True,
        'path': 'A',
        'contact_id': contact_id,
        'property_id': property_id,
        'sales_order_id': so_id
    }

def execute_path_b(contact_id, service_address, workiz_job, skip_confirm=False):
    """PATH B: Contact exists, Property doesn't. skip_confirm=True = backfill (no tasks)."""
    print("\n" + "="*70)
    print("EXECUTING PATH B: Existing Contact + New Property")
    print("="*70)
    
    city = workiz_job.get('City', '')
    postal_code = workiz_job.get('PostalCode', '')
    location_id = workiz_job.get('LocationId', '')
    frequency = workiz_job.get('frequency', '')
    type_of_service = workiz_job.get('type_of_service_2') or workiz_job.get('type_of_service', '')
    alternating = workiz_job.get('alternating', '')
    # Contact name for Property display "Contact Name, Address"
    contact_name = (workiz_job.get('FirstName', '') + ' ' + workiz_job.get('LastName', '')).strip()
    if not contact_name:
        contact_read = _odoo_search_read("res.partner", [["id", "=", contact_id]], ["name"], limit=1)
        if contact_read:
            contact_name = (contact_read[0].get("name") or "").strip()
    property_id = create_property(service_address, city, postal_code, contact_id, location_id, frequency, type_of_service, alternating, contact_name=contact_name)
    if not property_id:
        return {'success': False, 'error': 'Failed to create property'}
    
    so_id = create_sales_order(contact_id, property_id, workiz_job, skip_confirm=skip_confirm)
    if not so_id:
        return {'success': False, 'error': 'Failed to create sales order'}
    
    gate_code = workiz_job.get('gate_code', '')
    pricing = workiz_job.get('pricing', '')
    job_notes = workiz_job.get('JobNotes', '')
    comments = workiz_job.get('Comments', '')
    
    update_property_fields(property_id, gate_code, pricing, None, job_notes, comments, frequency, alternating, type_of_service)
    
    print("="*70)
    print("[OK] PATH B COMPLETE")
    print("="*70)
    
    return {
        'success': True,
        'path': 'B',
        'contact_id': contact_id,
        'property_id': property_id,
        'sales_order_id': so_id
    }

def execute_path_c(customer_name, service_address, workiz_job, client_id, skip_confirm=False):
    """PATH C: Neither Contact nor Property exist. skip_confirm=True = backfill (no tasks)."""
    print("\n" + "="*70)
    print("EXECUTING PATH C: New Contact + New Property")
    print("="*70)
    
    first_name = workiz_job.get('FirstName', '')
    last_name = workiz_job.get('LastName', '')
    phone = workiz_job.get('Phone', '')
    email = workiz_job.get('Email', '')
    city = workiz_job.get('City', '')
    postal_code = workiz_job.get('PostalCode', '')
    location_id = workiz_job.get('LocationId', '')
    frequency = workiz_job.get('frequency', '')
    type_of_service = workiz_job.get('type_of_service_2') or workiz_job.get('type_of_service', '')
    alternating = workiz_job.get('alternating', '')
    
    contact_id = create_contact(first_name, last_name, phone, email, service_address, city, postal_code, client_id)
    if not contact_id:
        return {'success': False, 'error': 'Failed to create contact'}
    
    property_id = create_property(service_address, city, postal_code, contact_id, location_id, frequency, type_of_service, alternating, contact_name=customer_name)
    if not property_id:
        return {'success': False, 'error': 'Failed to create property'}
    
    so_id = create_sales_order(contact_id, property_id, workiz_job, skip_confirm=skip_confirm)
    if not so_id:
        return {'success': False, 'error': 'Failed to create sales order'}
    
    gate_code = workiz_job.get('gate_code', '')
    pricing = workiz_job.get('pricing', '')
    job_notes = workiz_job.get('JobNotes', '')
    comments = workiz_job.get('Comments', '')
    
    update_property_fields(property_id, gate_code, pricing, None, job_notes, comments, frequency, alternating, type_of_service)
    
    print("="*70)
    print("[OK] PATH C COMPLETE")
    print("="*70)
    
    return {
        'success': True,
        'path': 'C',
        'contact_id': contact_id,
        'property_id': property_id,
        'sales_order_id': so_id
    }


# ==============================================================================
# PHASE 3: MASTER ROUTER (CREATE NEW SO)
# ==============================================================================

def phase3_create_so(input_data):
    """
    Phase 3 Router: Create new Sales Order (Paths A/B/C).
    Called by Phase 4 when SO doesn't exist.
    """
    print("\n" + "="*70)
    print("WORKIZ -> ODOO MASTER ROUTER")
    print("="*70)
    
    job_uuid = input_data.get('job_uuid')
    if not job_uuid:
        return {'success': False, 'error': 'No job_uuid provided'}
    
    print(f"\n[*] Fetching Workiz job: {job_uuid}")
    workiz_job = get_job_details(job_uuid)
    if not workiz_job:
        return {'success': False, 'error': 'Failed to fetch Workiz job'}
    
    customer_name = workiz_job.get('FirstName', '') + ' ' + workiz_job.get('LastName', '')
    customer_name = customer_name.strip()
    service_address = workiz_job.get('Address', '').strip()
    phone = workiz_job.get('Phone', '')
    email = workiz_job.get('Email', '')
    client_id = workiz_job.get('ClientId')
    
    print(f"[*] Customer: {customer_name}")
    print(f"[*] ClientId: {client_id}")
    print(f"[*] Address: {service_address}")
    
    if not client_id:
        return {'success': False, 'error': 'Missing ClientId from Workiz job'}
    
    if not service_address:
        return {'success': False, 'error': 'Missing service address'}
    
    print(f"\n[*] Searching for Contact by ClientId: {client_id}")
    contact_result = search_contact_by_client_id(client_id)
    
    skip_confirm = input_data.get('_skip_confirm', False)
    if skip_confirm:
        print("[*] Status/SubStatus is not 'Next appointment' / 'Send confirmation text' / 'Scheduled': SO will be created as draft (no task).")
    if contact_result:
        contact_id = contact_result['contact_id']
        
        print(f"\n[*] Searching for Property: {service_address}")
        property_result = search_property_for_contact(service_address, contact_id)
        
        if property_result:
            property_id = property_result['property_id']
            return execute_path_a(contact_id, property_id, workiz_job, skip_confirm=skip_confirm)
        else:
            return execute_path_b(contact_id, service_address, workiz_job, skip_confirm=skip_confirm)
    else:
        return execute_path_c(customer_name, service_address, workiz_job, client_id, skip_confirm=skip_confirm)


# ==============================================================================
# PHASE 4: UPDATE EXISTING SO
# ==============================================================================

def update_existing_sales_order(so_id, workiz_job, so_state=None):
    """Update an existing Sales Order with latest Workiz data. Skips order_line when SO is confirmed (sale/done) since Odoo locks lines.
    Property as brain: if SO has Contact as customer (partner_id != partner_shipping_id), we correct to Property on every update."""
    print(f"\n[*] Updating existing Sales Order ID: {so_id}")

    # Ensure UUID-matched SO is bound to the correct property for the incoming Workiz address.
    _rebind_so_to_matching_property_if_needed(so_id, workiz_job)
    
    # Fetch state and partner fields (for property-as-brain correction)
    _so_property_id = None
    read_payload = {
        "jsonrpc": "2.0", "method": "call",
        "params": {
            "service": "object", "method": "execute_kw",
            "args": [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, "sale.order", "read", [[so_id]], {"fields": ["state", "partner_id", "partner_shipping_id"]}]
        }
    }
    try:
        r = requests.post(ODOO_URL, json=read_payload, timeout=10)
        res = r.json().get("result", [])
        if res and isinstance(res[0], dict):
            if so_state is None:
                so_state = res[0].get("state")
            # Property as brain: if customer is Contact instead of Property, we will fix it in updates below
            pid = res[0].get("partner_id")
            sid = res[0].get("partner_shipping_id")
            pid = pid[0] if isinstance(pid, (list, tuple)) else pid
            sid = sid[0] if isinstance(sid, (list, tuple)) else sid
            _so_property_id = sid or pid
            if sid and pid != sid:
                _correct_customer_to_property = sid  # used when building updates
            else:
                _correct_customer_to_property = None
        else:
            _correct_customer_to_property = None
    except Exception:
        _correct_customer_to_property = None
    
    workiz_uuid = workiz_job.get('UUID', '')
    workiz_substatus = workiz_job.get('SubStatus', '') or workiz_job.get('Status', '')
    job_source = workiz_job.get('JobSource', '')
    job_type = workiz_job.get('JobType', '')
    gate_code = workiz_job.get('gate_code', '')
    pricing = workiz_job.get('pricing', '')
    job_notes = workiz_job.get('JobNotes', '')
    comments = workiz_job.get('Comments', '')
    job_datetime_str = workiz_job.get('JobDateTime', '') or workiz_job.get('job_datetime', '')
    if not job_datetime_str:
        job_date = workiz_job.get('JobDate', '') or workiz_job.get('job_date', '')
        job_time = workiz_job.get('JobTime', '') or workiz_job.get('job_time', '')
        if job_date and job_time:
            job_datetime_str = f"{str(job_date).strip()} {str(job_time).strip()}"
        elif job_date:
            job_datetime_str = str(job_date).strip()
    frequency = workiz_job.get('frequency', '')
    type_of_service = workiz_job.get('type_of_service_2') or workiz_job.get('type_of_service', '')
    team = workiz_job.get('Team', []) or workiz_job.get('team', [])
    tags = workiz_job.get('Tags') or workiz_job.get('JobTags', [])
    if isinstance(tags, str):
        try:
            tags = ast.literal_eval(tags)
        except Exception:
            tags = [t.strip() for t in tags.split(',') if t.strip()]
    if not isinstance(tags, list):
        tags = []
    line_items_raw = workiz_job.get('LineItems', [])
    status = workiz_job.get('Status', '')
    
    # Parse line items (API may return list or string)
    if isinstance(line_items_raw, str):
        try:
            line_items = ast.literal_eval(line_items_raw)
        except Exception:
            line_items = []
    else:
        line_items = line_items_raw if line_items_raw else []
    
    # Diagnostic: so we can see why line items might not sync (e.g. Workiz job/get returned 0 LineItems)
    print(f"[*] LineItems from Workiz: {len(line_items)} item(s)")
    if not line_items and so_state != 'done':
        print("[*] No line items in job payload; SO order lines will not be updated (check Workiz job/get response for LineItems).")
    
    team_names = format_team_names(team)
    
    job_datetime_utc = None
    if job_datetime_str:
        job_datetime_utc = convert_pacific_to_utc(job_datetime_str)
    
    notes_snapshot = ""
    if job_notes:
        notes_snapshot += f"[Job Notes]\n{job_notes}\n\n"
    if comments:
        notes_snapshot += f"[Comments]\n{comments}"
    notes_snapshot = notes_snapshot.strip()

    # Keep SO tags current (contact tags + Workiz tags) so task sync gets correct tags from SO.
    # Without this, task sync can write stale tags when only status/date changes.
    contact_tag_ids = []
    property_for_tags = _correct_customer_to_property or _so_property_id
    if property_for_tags:
        prop_read = _odoo_search_read("res.partner", [["id", "=", property_for_tags]], ["parent_id"], limit=1)
        if prop_read and prop_read[0].get("parent_id"):
            contact_id_for_tags = prop_read[0]["parent_id"]
            contact_id_for_tags = contact_id_for_tags[0] if isinstance(contact_id_for_tags, (list, tuple)) else contact_id_for_tags
            contact_read = _odoo_search_read("res.partner", [["id", "=", contact_id_for_tags]], ["category_id"], limit=1)
            if contact_read:
                category_id = contact_read[0].get("category_id") or []
                if isinstance(category_id, list):
                    if category_id and all(isinstance(x, int) for x in category_id):
                        contact_tag_ids = category_id
                    else:
                        contact_tag_ids = [x[0] for x in category_id if isinstance(x, (list, tuple)) and x]
                elif isinstance(category_id, int):
                    contact_tag_ids = [category_id]

    workiz_tag_ids = []
    for tag_name in tags:
        tag_name = str(tag_name).strip()
        if not tag_name:
            continue
        tag_search = _odoo_search_read("crm.tag", [["name", "=", tag_name]], ["id"], limit=1)
        if not tag_search:
            tag_search = _odoo_search_read("crm.tag", [["name", "ilike", tag_name]], ["id"], limit=1)
        if tag_search:
            workiz_tag_ids.append(tag_search[0]["id"])
        else:
            print(f"[!] Workiz tag not found in Odoo crm.tag: '{tag_name}'")
    all_tag_ids = sorted(set(contact_tag_ids + workiz_tag_ids))
    
    updates = {
        'x_studio_x_studio_workiz_status': workiz_substatus,
        'x_studio_x_studio_workiz_tech': team_names,
        'x_studio_x_gate_snapshot': gate_code,
        'x_studio_x_studio_pricing_snapshot': pricing,
        'x_studio_x_studio_notes_snapshot1': notes_snapshot,
    }
    if all_tag_ids:
        updates['tag_ids'] = [(6, 0, all_tag_ids)]
        print(f"[*] SO tags refreshed for sync: {all_tag_ids}")
    
    # Property as brain: correct customer to Property if SO still has Contact (e.g. from older Zap or one-off)
    if _correct_customer_to_property:
        updates['partner_id'] = _correct_customer_to_property
        updates['partner_invoice_id'] = _correct_customer_to_property
        print(f"[*] Correcting SO customer to Property (id={_correct_customer_to_property}); was Contact.")
    
    if job_datetime_utc:
        updates['date_order'] = job_datetime_utc
    
    if job_type:
        updates['x_studio_x_studio_x_studio_job_type'] = job_type
    
    if job_source:
        updates['x_studio_x_studio_lead_source'] = job_source
    
    # Only set freq/tos if value is in Odoo Selection (when field is Selection type)
    if frequency:
        freq_val = str(frequency).strip()
        try:
            from functions.odoo.get_selection_values import get_selection_values
            allowed = get_selection_values("sale.order", "x_studio_x_studio_frequency_so")
            if not allowed or freq_val in allowed:
                updates['x_studio_x_studio_frequency_so'] = freq_val
        except Exception:
            updates['x_studio_x_studio_frequency_so'] = freq_val
    if type_of_service:
        tos_val = str(type_of_service).strip()
        try:
            from functions.odoo.get_selection_values import get_selection_values
            allowed = get_selection_values("sale.order", "x_studio_x_studio_type_of_service_so")
            if not allowed or tos_val in allowed:
                updates['x_studio_x_studio_type_of_service_so'] = tos_val
        except Exception:
            updates['x_studio_x_studio_type_of_service_so'] = tos_val
    
    # Update order line items from Workiz
    if so_state in ('sale', 'done'):
        # For confirmed SOs: use smart update (can't delete lines, but can update prices and add lines)
        print(f"[*] SO state is {so_state}; using smart line update (update prices, add new, set qty=0 for removed)")
        order_line_commands = build_confirmed_so_line_commands(so_id, line_items)
        if order_line_commands:
            updates['order_line'] = order_line_commands
            print(f"[*] Processing {len(order_line_commands)} line item command(s)")
    else:
        # For draft SOs: use full replace (clear all + add new)
        print(f"[*] SO state is {so_state}; using full replace for line items")
        order_line_commands = build_order_line_commands(line_items)
        if order_line_commands:
            updates['order_line'] = [(5, 0, 0)] + order_line_commands  # (5,0,0) clear existing; then add new
            print(f"[*] Updating {len(order_line_commands)} line item(s) on SO")
            # Products that create tasks require a project on the quotation; set default project so write succeeds
            if DEFAULT_PROJECT_ID:
                updates[ODOO_SO_PROJECT_FIELD] = DEFAULT_PROJECT_ID
            else:
                print(f"[!] Set DEFAULT_PROJECT_ID in this script to your Odoo project ID if Odoo errors about project on quotation")
    
    # When status is Done, do NOT write payment fields to Odoo: payment now originates in Odoo (Phase 6A).
    # Writing Workiz payment data here would overwrite Odoo's source-of-truth and can cause conflicts.
    
    success = update_sales_order(so_id, updates)
    
    if not success:
        print("[ERROR] Failed to update Sales Order")
        return {'success': False, 'error': 'SO update failed'}
    
    print("[OK] Sales Order updated successfully")

    # Pricing check: compare Workiz total vs updated Odoo SO total and write flag
    workiz_total_raw = workiz_job.get('TotalPrice') or workiz_job.get('SubTotal') or 0
    try:
        workiz_total_check = float(workiz_total_raw)
    except Exception:
        workiz_total_check = 0
    if workiz_total_check > 0:
        so_total_result = _odoo_search_read('sale.order', [['id', '=', so_id]], ['amount_untaxed'], limit=1)
        odoo_total_check = float(so_total_result[0].get('amount_untaxed', 0)) if so_total_result else 0
        if abs(workiz_total_check - odoo_total_check) < 0.02:
            pricing_flag = '<span class="text-success"><b>OK - Workiz: ${:.2f} | Odoo: ${:.2f}</b></span>'.format(workiz_total_check, odoo_total_check)
        else:
            pricing_flag = '<span class="text-danger"><b>MISMATCH - Workiz: ${:.2f} | Odoo: ${:.2f} - Change status to Scheduled in Workiz to force Phase 4 sync</b></span>'.format(workiz_total_check, odoo_total_check)
        _odoo_write('sale.order', [so_id], {'x_studio_pricing_mismatch': pricing_flag})
        print(f"[*] Pricing check: Workiz ${workiz_total_check:.2f} vs Odoo ${odoo_total_check:.2f}")

    # Sync tasks: every status/date/team change updates the existing task(s) — we never create a second task or ignore. Overwrites assignee, planned date, start/end, customer, contact number, tags with current Workiz data (e.g. moving date in Workiz moves the task).
    order_date = job_datetime_utc or updates.get("date_order")
    task_sync_info = {"task_sync_tasks_found": 0, "task_sync_updated": False, "task_sync_error": "not_called"}
    if so_state != 'draft' or order_date or workiz_job.get("Team") or workiz_job.get("team"):
        task_sync_info = sync_tasks_from_so_and_job(so_id, workiz_job, order_date) or task_sync_info
    
    # Post to chatter
    last_status_update = workiz_job.get('LastStatusUpdate', '')
    message_parts = [f"Status updated to: {workiz_substatus}"]
    
    if last_status_update:
        message_parts[0] = f"Status updated to: {workiz_substatus} on {last_status_update}"
    
    # Do not append payment status/tip when Done; payment data originates in Odoo (Phase 6A).
    
    chatter_message = "; ".join(message_parts)
    post_chatter_message(so_id, chatter_message)
    print("[OK] Posted status update to chatter")
    
    return {'success': True, 'so_id': so_id, 'updated': True, **task_sync_info}

def update_contact_last_visit_all_properties(contact_id):
    """
    Update Contact's x_studio_last_visit_all_properties with the MAX last visit date
    across ALL properties owned by this contact.
    """
    if not contact_id:
        return
    
    print(f"[*] Updating Contact {contact_id} last visit (all properties)...")
    
    # Find all properties for this contact
    properties = _odoo_search_read(
        "res.partner",
        [["parent_id", "=", contact_id], ["x_studio_x_studio_record_category", "=", "Property"]],
        ["id", "x_studio_x_studio_last_property_visit"],
        limit=500
    )
    
    if not properties:
        print(f"[*] No properties found for Contact {contact_id}")
        return
    
    # Find the most recent visit date across all properties
    max_date = None
    for prop in properties:
        visit_date = prop.get('x_studio_x_studio_last_property_visit')
        if visit_date:
            if max_date is None or visit_date > max_date:
                max_date = visit_date
    
    if not max_date:
        print(f"[*] No visit dates found on properties")
        return
    
    # Update Contact
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB, ODOO_USER_ID, ODOO_API_KEY,
                "res.partner", "write",
                [[contact_id], {"x_studio_last_visit_all_properties": max_date}]
            ]
        }
    }
    
    response = requests.post(ODOO_URL, json=payload, timeout=10)
    result = response.json().get("result")
    
    if result:
        print(f"[OK] Contact {contact_id} last visit updated to: {max_date}")
        return True
    else:
        print(f"[ERROR] Failed to update Contact last visit")
        return False


def update_contact_service_fields(contact_id):
    """
    Aggregate service fields from ALL properties to Contact level.
    - Has Window Service: True if ANY property has window service
    - Has Solar Service: True if ANY property has solar service
    - Most Recent Service Type: From property with most recent last visit
    """
    if not contact_id:
        return
    
    print(f"[*] Updating Contact {contact_id} service fields...")
    
    # Find all properties for this contact
    properties = _odoo_search_read(
        "res.partner",
        [["parent_id", "=", contact_id], ["x_studio_x_studio_record_category", "=", "Property"]],
        ["id", "x_studio_has_window_service", "x_studio_has_solar_service", 
         "x_studio_most_recent_service_type", "x_studio_x_studio_last_property_visit"],
        limit=500
    )
    
    if not properties:
        print(f"[*] No properties found for Contact {contact_id}")
        return
    
    # Aggregate service flags (True if ANY property has it)
    contact_has_window = False
    contact_has_solar = False
    most_recent_service_type = False  # Default to blank
    most_recent_date = None
    
    for prop in properties:
        if prop.get('x_studio_has_window_service'):
            contact_has_window = True
        if prop.get('x_studio_has_solar_service'):
            contact_has_solar = True
        
        # Most recent service type: from property with latest visit
        prop_service_type = prop.get('x_studio_most_recent_service_type')
        prop_last_visit = prop.get('x_studio_x_studio_last_property_visit')
        
        if prop_service_type and prop_service_type != False and prop_last_visit:
            if most_recent_date is None or prop_last_visit > most_recent_date:
                most_recent_date = prop_last_visit
                most_recent_service_type = prop_service_type
    
    # Update Contact
    updates = {
        'x_studio_has_window_service': contact_has_window,
        'x_studio_has_solar_service': contact_has_solar,
        'x_studio_most_recent_service_type': most_recent_service_type
    }
    
    _odoo_write("res.partner", [contact_id], updates)
    print(f"[OK] Contact {contact_id} service fields updated: window={contact_has_window}, solar={contact_has_solar}, type={most_recent_service_type}")
    return True


def clear_next_job_date_on_contact(contact_id):
    """Clear x_studio_next_job_date on Contact when job is Done or Canceled."""
    if not contact_id:
        return
    try:
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
                    "res.partner",
                    "write",
                    [[contact_id], {"x_studio_next_job_date": False}]
                ]
            }
        }
        rpc_resp = requests.post(ODOO_URL, json=payload, timeout=10)
        rpc_data = rpc_resp.json()
        if rpc_data.get("result"):
            print(f"[OK] Next Job Date cleared on contact {contact_id}")
        else:
            print(f"[WARNING] Could not clear Next Job Date: {rpc_data}")
    except Exception as e:
        print(f"[WARNING] clear_next_job_date_on_contact failed: {e}")


def update_property_from_job(property_id, workiz_job, so_id=None, is_done=False):
    """Update property fields from Workiz job data (including service tracking)."""
    gate_code = workiz_job.get('gate_code', '')
    pricing = workiz_job.get('pricing', '')
    job_notes = workiz_job.get('JobNotes', '')
    comments = workiz_job.get('Comments', '')
    frequency = workiz_job.get('frequency', '')
    alternating = workiz_job.get('alternating', '')
    type_of_service = workiz_job.get('type_of_service_2') or workiz_job.get('type_of_service', '')
    
    last_visit_date = None
    has_window = None
    has_solar = None
    most_recent_service_type = None
    
    if is_done:
        job_datetime_str = workiz_job.get('JobDateTime', '')
        if job_datetime_str:
            last_visit_date = job_datetime_str.split(' ')[0]
            print(f"[*] Updating Last Property Visit to: {last_visit_date}")
        
        # NEW: Analyze service type from Sales Order products
        if so_id:
            print(f"[*] Analyzing service types from SO {so_id}...")
            has_window_flag, has_solar_flag, service_type = analyze_service_type_from_so(so_id)
            
            # Set flags: if THIS order has the service, mark as True (never set to False - all-time flags)
            if has_window_flag:
                has_window = True
                print(f"[*] Window service detected - setting x_studio_has_window_service = True")
            
            if has_solar_flag:
                has_solar = True
                print(f"[*] Solar service detected - setting x_studio_has_solar_service = True")
            
            # Always update most recent service type (this changes with each job)
            most_recent_service_type = service_type
            print(f"[*] Most recent service type: {service_type}")
    
    update_property_fields(property_id, gate_code, pricing, last_visit_date, job_notes, comments, 
                          frequency, alternating, type_of_service, has_window, has_solar, 
                          most_recent_service_type)
    print(f"[OK] Property {property_id} updated")
    
    # NEW: Update Contact's aggregated fields across ALL properties
    if is_done:
        # Get Contact ID from Property
        prop_data = _odoo_search_read("res.partner", [["id", "=", property_id]], ["parent_id"], limit=1)
        if prop_data and prop_data[0].get('parent_id'):
            contact_id = prop_data[0]['parent_id'][0] if isinstance(prop_data[0]['parent_id'], list) else prop_data[0]['parent_id']
            if contact_id:
                # Update last visit date across all properties
                if last_visit_date:
                    update_contact_last_visit_all_properties(contact_id)
                # Update service fields across all properties
                update_contact_service_fields(contact_id)


# ==============================================================================
# PHASE 4: MAIN ROUTER
# ==============================================================================

def main(input_data):
    """
    Phase 4 Main Router: Handle Workiz job status updates.
    
    Expected input_data formats:
    1. Workiz webhook (real-time): {'data': {'uuid': '...', 'status': '...', ...}}
    2. Zapier polling (legacy): {'job_uuid': 'ABC123'}
    """
    print("\n" + "="*70)
    print("PHASE 4: WORKIZ JOB STATUS UPDATE")
    print("="*70)
    
    # Extract job UUID and data from input (supports both webhook and polling formats)
    job_uuid, workiz_job = extract_job_from_input(input_data)
    
    if not job_uuid:
        return {'success': False, 'error': 'No job_uuid provided'}
    
    # If webhook didn't provide full data, fetch from Workiz API
    if not workiz_job:
        print(f"\n[*] Fetching Workiz job details: {job_uuid}")
        workiz_job = get_job_details(job_uuid)
        if not workiz_job:
            return {'success': False, 'error': 'Failed to fetch Workiz job'}
    else:
        print(f"\n[*] Using Workiz webhook data (no API call needed)")
    
    status = workiz_job.get('Status', '')
    substatus = workiz_job.get('SubStatus', '')
    print(f"[*] Job Status: {status}")
    if substatus:
        print(f"[*] Job SubStatus: {substatus}")
    
    # For Submitted status: only run if an SO already exists for this job UUID.
    # If no SO exists, skip and let Phase 3 (New Job trigger) create it — avoids race condition where
    # Phase 4 and Phase 3 both try to create an SO simultaneously for the same new job.
    # If SO already exists, go ahead and update it (e.g. Phase 3 already ran, or job was imported).
    if (status or '').strip().lower() == 'submitted':
        existing_check = search_sales_order_by_uuid(job_uuid)
        if not existing_check:
            print("[*] Skipping Phase 4 for status 'Submitted' with no existing SO (Phase 3 will create it via New Job trigger)")
            print("="*70)
            return {'success': True, 'skipped': True, 'reason': 'status_is_submitted_no_so'}
        print("[*] Status is Submitted but SO already exists — continuing Phase 4 update")
    
    # -------------------------------------------------------------------------
    # GRAVEYARD JOB AUTO-CLOSE: Detect manually scheduled reactivation jobs
    # -------------------------------------------------------------------------
    # When a graveyard job (Reactivation Lead) gets manually scheduled (you change JobType and schedule it),
    # auto-close the Opportunity (same outcome as Calendly path).
    # IMPORTANT: Check this BEFORE checking if SO exists (Opportunity should close regardless of SO status).
    
    job_type = workiz_job.get('JobType', '')
    job_status = workiz_job.get('Status', '')
    job_substatus = workiz_job.get('SubStatus', '')
    
    print(f"[*] Checking for graveyard job auto-close: JobType='{job_type}', Status='{job_status}', SubStatus='{job_substatus}'")
    
    # Detection criteria: JobType is NOT "Reactivation Lead" AND job is scheduled
    # Current 4 scheduling statuses (will be renamed to start with "Scheduled" later)
    # PLUS any future status starting with "Scheduled" (future-proof)
    # CHECK BOTH Status AND SubStatus (Workiz uses SubStatus for "Next Appointment - Text" etc.)
    current_scheduling_statuses = ['Scheduled', 'Next Appointment - Text', 'Next Appointment 2 - Text', 'Send Confirmation - Text']
    
    status_starts_with_scheduled = job_status.lower().startswith('scheduled') if job_status else False
    substatus_starts_with_scheduled = job_substatus.lower().startswith('scheduled') if job_substatus else False
    
    is_scheduled = (job_status in current_scheduling_statuses or 
                   job_substatus in current_scheduling_statuses or 
                   status_starts_with_scheduled or 
                   substatus_starts_with_scheduled)
    
    if job_type != 'Reactivation Lead' and is_scheduled:
        print("[*] Job is scheduled and NOT a Reactivation Lead - checking for linked Opportunity")
        
        # Look up Opportunity by this graveyard UUID
        opportunity = find_opportunity_by_graveyard_uuid(job_uuid)
        
        if opportunity:
            opp_id = opportunity['id']
            opp_name = opportunity['name']
            
            print(f"[!] GRAVEYARD AUTO-CLOSE DETECTED!")
            print(f"[*] This was a reactivation that got manually scheduled in Workiz")
            print(f"[*] Opportunity: {opp_name} (ID: {opp_id})")
            
            # Post to Opportunity chatter
            post_opportunity_chatter(opp_id, 
                f"🔄 GRAVEYARD AUTO-CLOSE: Job manually scheduled in Workiz<br/>"
                f"JobType changed to: {job_type}<br/>"
                f"Status: {job_status} | SubStatus: {job_substatus}<br/>"
                f"Workiz UUID: {job_uuid}<br/>"
                f"Action: Marking Opportunity Won (auto-close)")
            
            # Mark Opportunity as Won (closes it)
            won_result = mark_opportunity_won(opportunity['id'])
            
            if won_result.get('success'):
                print("[OK] Opportunity marked Won")
                post_opportunity_chatter(opp_id, 
                    f"✅ Opportunity marked WON (auto-closed from manual scheduling)")
            else:
                error_msg = won_result.get('message', 'Unknown error')
                print(f"[ERROR] Failed to mark Opportunity Won: {error_msg}")
                post_opportunity_chatter(opp_id, 
                    f"❌ ERROR: Failed to mark Opportunity Won<br/>"
                    f"Error: {error_msg}")
        else:
            print("[*] No Opportunity found for this graveyard UUID")
            print("[*] This is either a normal job or graveyard job not yet created")
    else:
        print(f"[*] Not a graveyard auto-close scenario (JobType='{job_type}' or not scheduled)")
    
    print(f"\n[*] Searching for existing Sales Order with UUID: {job_uuid}")
    existing_so = search_sales_order_by_uuid(job_uuid)
    
    should_trigger_tasks = is_task_trigger_status(status, substatus)
    
    if existing_so:
        so_id = existing_so['id']
        print(f"[OK] Found existing SO: {existing_so['name']} (ID: {so_id})")
        so_state = existing_so.get('state')
        
        result = update_existing_sales_order(so_id, workiz_job, so_state=so_state)
        
        # When SO was quotation (draft) and job is now scheduled, confirm SO so tasks are created, then sync task fields.
        if so_state == 'draft' and should_trigger_tasks:
            print("[*] Quotation → scheduling: confirming SO and syncing tasks (assignee, planned date, start/end, phone).")
            job_datetime_str = workiz_job.get('JobDateTime', '')
            job_datetime_utc = convert_pacific_to_utc(job_datetime_str) if job_datetime_str else None
            confirm_sales_order(so_id, date_order_utc=job_datetime_utc)
            sync_tasks_from_so_and_job(so_id, workiz_job, job_datetime_utc)
        
        property_id = existing_so.get('partner_shipping_id')
        if property_id:
            if isinstance(property_id, list):
                property_id = property_id[0]
            update_property_from_job(property_id, workiz_job, so_id=so_id, is_done=(status.lower() == 'done'))
            # Clear next job date on contact when job is Done or Canceled
            if status.lower() in ('done', 'canceled'):
                prop_data = _odoo_search_read("res.partner", [["id", "=", property_id]], ["parent_id"], limit=1)
                if prop_data and prop_data[0].get('parent_id'):
                    c_id = prop_data[0]['parent_id']
                    clear_next_job_date_on_contact(c_id[0] if isinstance(c_id, (list, tuple)) else c_id)

        # PHASE 5: Do NOT trigger when status is Done. Phase 6 already triggers Phase 5 when it marks the job Done (payment in Odoo). If we also trigger here, we get duplicate next jobs (e.g. two jobs for same SO 004153). So only Phase 6 calls Phase 5 for "job done" flow.
        # If you ever mark a job Done manually in Workiz (without recording payment in Odoo first), you will not get the next job/activity automatically; record payment in Odoo to trigger Phase 6 → Phase 5.
        
        print("="*70)
        print("[OK] PHASE 4 COMPLETE - SALES ORDER UPDATED")
        print("="*70)
        return result
    
    else:
        # Re-check for SO before creating (another Phase 4 run may have just created it → avoids duplicate SOs)
        so_record = search_sales_order_by_uuid(job_uuid)
        if so_record:
            so_id = so_record['id']
            print(f"[*] SO found on re-check (ID {so_id}), updating instead of creating")
            so_state = so_record.get('state')
            result = update_existing_sales_order(so_id, workiz_job, so_state=so_state)
            if not result.get('success'):
                return result
            # When SO was draft and job is now scheduled, confirm and sync tasks.
            if so_state == 'draft' and should_trigger_tasks:
                print("[*] Quotation → scheduling: confirming SO and syncing tasks.")
                job_datetime_str = workiz_job.get('JobDateTime', '')
                job_datetime_utc = convert_pacific_to_utc(job_datetime_str) if job_datetime_str else None
                confirm_sales_order(so_id, date_order_utc=job_datetime_utc)
                ts = sync_tasks_from_so_and_job(so_id, workiz_job, job_datetime_utc)
                if ts:
                    result.update(ts)
            property_id = so_record.get('partner_shipping_id')
            if property_id is not None:
                if isinstance(property_id, list):
                    property_id = property_id[0] if property_id else None
                if property_id:
                    update_property_from_job(property_id, workiz_job, so_id=so_id, is_done=(workiz_job.get('Status') == 'Done'))
                    # Clear next job date on contact when job is Done or Canceled
                    if workiz_job.get('Status', '').lower() in ('done', 'canceled'):
                        prop_data = _odoo_search_read("res.partner", [["id", "=", property_id]], ["parent_id"], limit=1)
                        if prop_data and prop_data[0].get('parent_id'):
                            c_id = prop_data[0]['parent_id']
                            clear_next_job_date_on_contact(c_id[0] if isinstance(c_id, (list, tuple)) else c_id)
            print("="*70)
            print("[OK] PHASE 4 COMPLETE - SALES ORDER UPDATED (found on re-check)")
            print("="*70)
            return result
        
        print("[!] Sales Order not found - triggering Phase 3 webhook to create it")
        print("="*70)
        
        # Call Phase 3 via webhook (creates separate Zapier run for better logging)
        phase3_payload = {'job_uuid': job_uuid}
        
        try:
            print(f"[*] Sending webhook to Phase 3: {PHASE3_WEBHOOK_URL}")
            webhook_response = requests.post(PHASE3_WEBHOOK_URL, json=phase3_payload, timeout=10)
            
            if webhook_response.status_code in (200, 201):
                print("[OK] Phase 3 webhook triggered successfully")
                print("[*] Phase 3 will run as separate Zap and create the Sales Order")
                print("="*70)
                print("[OK] PHASE 4 COMPLETE - DELEGATED TO PHASE 3")
                print("="*70)
                return {
                    'success': True,
                    'delegated_to_phase3': True,
                    'job_uuid': job_uuid,
                    'message': 'SO creation delegated to Phase 3 webhook'
                }
            else:
                print(f"[ERROR] Phase 3 webhook failed: HTTP {webhook_response.status_code}")
                return {
                    'success': False,
                    'error': f'Phase 3 webhook failed: HTTP {webhook_response.status_code}'
                }
        except Exception as e:
            print(f"[ERROR] Failed to call Phase 3 webhook: {e}")
            return {'success': False, 'error': f'Phase 3 webhook error: {e}'}


# ==============================================================================
# ZAPIER ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    # For local testing
    test_input = {
        'job_uuid': 'IC3ZC9'  # Test with Done job
    }
    
    result = main(test_input)
    print("\n" + "="*70)
    print("FINAL RESULT:")
    print(result)
    print("="*70)
else:
    # For Zapier deployment
    output = main(input_data)