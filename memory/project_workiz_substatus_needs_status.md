---
name: Workiz SubStatus update requires parent Status field
description: Workiz API quirk — POSTing only SubStatus returns 400 "Could not update sub status with no parent status provided". Must also send Status="Pending". Auto-injected in workiz_post.
type: project
originSessionId: 96c7eadf-7840-4091-9290-6d3aed1806c8
---
Workiz API quirk: when updating a job's `SubStatus`, the request body MUST also include the parent `Status` field. Sending only SubStatus returns:

```
400 {'error': True, 'code': 400, 'msg': 'Validation rule exception',
     'details': {'error': 'Could not update sub status with no parent status provided'}}
```

**Workiz Status model (clarified by DJ 2026-04-26):** Only `Submitted` and `Done` are true top-level Status values we use. Everything else — Scheduled, STOP, Lead, Send Confirmation - Text, Next Appointment - Text, Next Appointment 2 - Text, **even In Progress and Canceled** — lives under `Status="Pending"` as a SubStatus. Always filter and report on SubStatus.

Hit 2026-04-26 when Render Claude tried to change Kristin Acker's job from Submitted to SubStatus="Send Confirmation - Text" via update_workiz_field — workiz_post sent only `{SubStatus: 'Send Confirmation - Text'}`.

**Fixed (commit 405a31d on saunders-render-app):** `workiz_post()` in `routers/owner/dashboard.py` now auto-injects `Status="Pending"` whenever the body contains `SubStatus` and no Status:

```python
if 'SubStatus' in data and 'Status' not in data:
    data['Status'] = 'Pending'
```

**Why:** Same defense-in-depth pattern as the UUID-in-body fix — central helper, can't be forgotten by future call sites. The invariant holds because all our SubStatuses live under Pending.

**How to apply:** When building Workiz API helpers in OTHER codebases (Zapier phases, Odoo server actions), apply the same rule: any SubStatus update must also send Status="Pending". Don't forget. This is in addition to the UUID-in-body requirement (project_workiz_update_needs_uuid_in_body.md).
