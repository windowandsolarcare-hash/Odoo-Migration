---
name: project_workiz_canceled_is_status
description: "'Canceled' is a TOP-LEVEL Workiz Status, not a SubStatus — corrects CLAUDE.md. To cancel a job set Status='Canceled' (no SubStatus)."
metadata:
  node_type: memory
  type: project
  originSessionId: ed913ff2
---

**To cancel a Workiz job: `workiz_post('job/update/{UUID}/', {'Status': 'Canceled'})`** — `Canceled` is a **top-level Status**, NOT a SubStatus.

Verified 2026-06-29 (live): setting `SubStatus='Canceled'` returns HTTP 400 `"Could not find matching value for SubStatus - Canceled"`. Setting `Status='Canceled'` succeeds (job then reads back `Status='Canceled'`, `SubStatus=''`).

**Why:** CLAUDE.md's WORKIZ section lists "Canceled" among the SubStatus values under Status="Pending" — that is WRONG for this account. The render app's `_TOP_LEVEL_STATUSES = {'submitted','done','canceled','in progress'}` (dashboard.py ~L1451 / field.py ~L638) is the correct model: Submitted, Done, Canceled, In Progress are all top-level Statuses; the Pending SubStatuses are Scheduled / STOP / Lead / Send Confirmation - Text / Next Appointment - Text / Next Appointment 2 - Text / Re-engagement Trigger / etc.

**How to apply:** When cancelling a Workiz job (e.g. an orphaned re-engagement lead), set top-level `Status='Canceled'` and do NOT pass a SubStatus (so `workiz_post`'s auto-inject of `Status='Pending'` is avoided — it only injects when `SubStatus` is present). Direct API calls from a script need the `auth_secret` + `UUID` in the JSON body + a non-default `User-Agent` header (default `Python-urllib` gets HTTP 403). See [[project_calendly_booking_alert]], [[project_reengagement_vs_reactivation]].
