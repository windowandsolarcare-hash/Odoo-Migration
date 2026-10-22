---
name: customer-email-field-job-detail
description: "Customer EMAIL is editable in the job-detail 'Customer & Order Details' dropdown (so_full + brain_job_save cust_email→both_targets). Adding a text customer field there is SERVER-ONLY + lights both owner + /tech/field."
metadata:
  node_type: memory
  type: project
  modified: 2026-10-22T19:28:56.935Z
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
---

The job-detail **"📋 Customer & Order Details"** dropdown (DJ's "Customer Order Information") is **data-driven**: `api_so_full` (dashboard.py:8872) returns `groups→rows` (`_sect` stamps `editable=bool(key)`), the client renders each row, and "💾 Save Changes" POSTs changed `[data-key]` values to `/owner/api/brain/job` (`brain_job_save`, brain.py:201). **Email added 2026-10-22** (dashboard.py `50ec16b0` + brain.py `e3689993`, §15 Lead+Audit GREEN): `_CF` reads `email`, a `{'label':'Email','key':'cust_email'}` row sits under Phone, and `brain_job_save._CUST_BOTH` maps `cust_email→email`.

**Pattern — adding a plain text customer field here is SERVER-ONLY (no client edit):** add the row to the `api_so_full` group + (for a res.partner field) a `cust_*` entry in `brain_job_save`'s `_CUST_BOTH`/`_CUST_PROP`/`_CUST_PERSON`. A type-less editable row hits the generic `if(r.editable)` plain-input branch on BOTH renderers — `_job_detail_panel.js:494` (owner → v2_job.html, the LIVE owner job screen; NOT a `v2_field.html` file — that never shipped) AND `field.html:3010` (tech, served LIVE at /tech/field, see [[field-html-served-live-at-tech-field]]). One server change lights up both surfaces.

**Load-bearing nuance (Lead firsthand, 2026-10-22):** the EMAIL consumers read the **PARENT contact** (`partner_id`), not the property child — the payment-link sender (dashboard.py:~6561-6568) reads email off the SO's `partner_id` and HARD-ERRORS "No email address on file" if absent; the reactivation writer (~:2102) likewise. That is WHY `cust_email` lives in `_CUST_BOTH` (writes to `both_targets` = Property child + parent Contact, brain.py:331-333) — writing both lands it where the senders read. `_CUST_BOTH` is also how `cust_phone/street/city/zip` behave.

**Parked (Lead declined as gold-plating):** display reads the property child's email via `_pg('email')`; senders read the parent — 6/935 kids blank-while-parent-has-email (self-heals on first save since the write syncs both). **Trigger to add a 1-line parent-email display fallback** (`'email'` into the `_psn` parent read ~:8990, display `_pg('email') or _person_email`): DJ reports an email showing blank when the customer has one. Also LOW/not done: no email-format validation (plain Char); the compact contact-card widget (`_fdContactCards`) shows only phone, not email. Related: [[nav-addr-canonical-source]] neighbors in the same editor; [[feedback_display_implies_crud_parity]].
