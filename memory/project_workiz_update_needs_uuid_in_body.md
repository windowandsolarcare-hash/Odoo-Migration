---
name: Workiz update/delete endpoints require UUID in request body
description: Workiz API quirk — job/update/ needs "UUID" in body, job/delete/ needs "ID" in body. URL path is not enough. Fixed via auto-injection in workiz_post.
type: project
originSessionId: 96c7eadf-7840-4091-9290-6d3aed1806c8
---
Workiz API quirk: `POST /job/update/{UUID}/` and `POST /job/delete/{UUID}/` both require the UUID **in the request body**, not just the URL path. The two endpoints use **different keys**:

- `job/update/{UUID}/` → body must contain `{"UUID": "<uuid>"}`
- `job/delete/{UUID}/` → body must contain `{"ID": "<uuid>"}`

Without the body field, Workiz returns:
```
400 {'error': True, 'code': 400, 'msg': 'Error Validating Fields',
     'details': {'UUID': 'Field is Required'}}
```

Hit 2026-04-26 when Render Claude called `update_workiz_field` to add a note — `workiz_post()` only put UUID in the URL path.

**Fixed (commit 7cbd848 on saunders-render-app):** `workiz_post()` in `routers/owner/dashboard.py` now auto-injects the UUID into the body using a regex on the endpoint:

```python
m = re.match(r'^job/(update|delete)/([^/]+)/?$', endpoint)
if m:
    action, juuid = m.group(1), m.group(2)
    body_key = 'UUID' if action == 'update' else 'ID'
    if body_key not in data:
        data[body_key] = juuid
```

**Why:** Two call sites already had this bug latent (`update_workiz_field`, `mark_job_done`), and any future code calling `workiz_post` for update/delete would hit it. Centralizing the fix in `workiz_post` eliminates the entire class of errors.

**How to apply:** When building Workiz API helpers in OTHER codebases (Zapier phases, Odoo server actions), apply the same rule: include UUID in body for update, ID in body for delete. Don't rely on URL path alone. Best to centralize the helper and bake in the rule.
