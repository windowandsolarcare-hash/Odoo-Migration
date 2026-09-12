# WORKIZ LEGACY — archived from CLAUDE.md (2026-09-12)

Workiz went dark **2026-08-03**. Odoo is the single source of truth. This content is **history/reference only** — do NOT act on it as current. Moved out of CLAUDE.md to keep the governing doc small enough to reliably honor. See CLAUDE.md's top "WORKIZ IS RETIRED" section for what replaced it.

---

## WORKIZ API ACCESS — HOW TO CALL FROM SCRIPTS

**Workiz GET calls work directly from anywhere** — local machines, Render, Odoo server actions. No IP restriction. No proxy needed.

**Workiz API URL format:**
```
GET:    https://api.workiz.com/api/v1/{TOKEN}/job/get/{UUID}/
UPDATE: https://api.workiz.com/api/v1/{TOKEN}/job/update/{UUID}/
DELETE: https://api.workiz.com/api/v1/{TOKEN}/job/delete/{UUID}/
```
- Token: `[RETIRED — Workiz dead 2026-08-03]`
- Auth Secret: `[RETIRED — Workiz dead 2026-08-03]` — needed for POST/UPDATE/DELETE, **NOT for GET**
- In Odoo server actions: use `requests.get(url)` — `requests` is available in Odoo eval context
- **Rate limit:** ~30 calls before hitting HTTP 429 — sleep 15-30 seconds between batches

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
Only **Submitted** and **Done** are true top-level Status values that we use. **Everything else lives under Status="Pending" as a SubStatus** — Scheduled, STOP, Lead, Send Confirmation - Text, Next Appointment - Text, Next Appointment 2 - Text, In Progress, Canceled, all of them.
ALWAYS filter on SubStatus, not Status.
When updating SubStatus via the API, the body MUST include the parent Status="Pending" too — otherwise Workiz returns 400 "Could not update sub status with no parent status provided". `workiz_post` in the Render app auto-injects this; if you write Workiz API code in Zapier or Odoo server actions, replicate the rule.

**Workiz API quirks:**
- ClientId: use numeric (e.g. 1040) not "CL-xxx"
- JobDateTime: omit entirely for unscheduled jobs
- All string fields: must be str() — reject None/numbers
- Job create response: returns list `[{UUID: '...'}]` or HTTP 204
- Job GET response: `{"data": [{...job...}]}` — job is inside a list. Always parse: `data = raw['data']; job = data[0] if isinstance(data, list) else data`
- Job GET on deleted job: returns **HTTP 204** (no content), NOT 404. Treat both 204 and 404 as "job is gone"
- type_of_service_2 is the custom field name (NOT type_of_service)

---

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
