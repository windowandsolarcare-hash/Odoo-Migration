---
name: reference_odoo19_unlink_tracking_bypass
description: "Odoo 19 XML-RPC unlink/action_cancel throwing 'unhashable type: list' on mail-tracked records → fix by passing context tracking_disable. Also: sale.order has no 'active' field."
metadata: 
  node_type: memory
  type: reference
  originSessionId: ce7b153f-3bb6-4e33-a982-35d4d7a9f4ba
---

# Deleting Odoo records via XML-RPC that throw "unhashable type: list"

**Symptom:** `execute_kw(..., 'sale.order', 'unlink', [[so_id]])` or `'action_cancel'` fails with `TypeError: unhashable type: 'list'` deep in the ORM (`mail_thread._track_discard`: `initial_values[id_] = None`, or field-cache `__get__`). Happens on OLD/real records that have **mail-tracking history** (chatter, tracked field changes). Fresh records (e.g. just-created Personal Time blocks) unlink fine — which is why some deletes work and others don't.

**FIX (verified 2026-07-05 deleting SO 003785 id 16020):** pass a **context that disables mail tracking** as the execute_kw kwargs:
```python
ctx = {'context': {'tracking_disable': True, 'mail_notrack': True, 'mail_create_nolog': True}}
M.execute_kw(DB, UID, KEY, 'sale.order', 'action_cancel', [[so_id]], ctx)
M.execute_kw(DB, UID, KEY, 'sale.order', 'unlink',        [[so_id]], ctx)   # → deletes cleanly
```
Cancel first, then unlink. This supersedes the old "don't unlink, it always throws" workaround — you CAN unlink, just disable tracking. (Different blocker from a POSTED-invoice SO, which genuinely can't be deleted — see [[project_workiz_jobs_not_in_odoo]].)

**Also:** `sale.order` has **NO `active` field** in this Odoo 19 — `write {'active': False}` errors `Invalid field 'active'`. So you can't "archive" an SO to hide it; unlink (with the context above) or state='cancel' are the options. NOTE: the Customer Brain now shows ALL states incl `cancel` ([[project_customer_brain_job_actions]]), so to truly remove an orphan SO from view you must UNLINK it, not just cancel.

**Workiz delete (for the same job):** `POST /job/delete/{UUID}/` body `{"ID":"<uuid>","auth_secret":"sec_..."}` + `User-Agent` header → `{flag:true, msg:'Job deleted'}`. (delete needs **ID** in body; update needs **UUID** in body.) Local calls need a browser UA or 403.
