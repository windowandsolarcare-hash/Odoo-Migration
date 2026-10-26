---
name: project_v2_job_is_live_job_detail_screen
description: "v2_field.html is GONE (404). The LIVE owner job-detail screen is v2_job.html (every v2 page deep-links v2_job.html?open_so=...). It loads the shared _job_detail_panel.js. Canonical invoice-send = POST /owner/api/job/send_invoice (brain.py:767). Supersedes CLAUDE.md §10's stale 'v2_field.html is the LIVE field screen'. Confirmed 2026-10-25."
metadata:
  node_type: memory
  type: project
  originSessionId: 4e67b763-0811-48ad-9309-a03b9da13378
  modified: 2026-10-26T02:42:12.468Z
---

**`v2_field.html` no longer exists** — `GET .../static/owner/v2_field.html` is 404 and it's absent from the `static/owner` listing (confirmed firsthand by Specialists + Lead, 2026-10-25). The **live owner job-detail screen is `static/owner/v2_job.html`** (its header comment: "COPY of v2_field.html that opens a single job INSTANTLY via ?open_so"). The whole app deep-links `v2_job.html?open_so=<SO>`. **Edit the owner job-detail screen in `v2_job.html`, NOT `v2_field.html`** (which is gone) — this SUPERSEDES CLAUDE.md §10's 2026-09-12 line "v2_field.html is the LIVE field screen" (stale; flagged to Lead for the §10 update).

- **Shared panel:** `v2_job.html` loads `static/owner/_job_detail_panel.js` (money/timer/photos/so_full/notes/confirm/brain). The panel "loads in the SAME global scope as its host page," so its functions/globals (`fdInvOpen`, `activeJob`, `$`, …) resolve from v2_job's own inline `<script>` and inline `onclick`s. `v2_job.html` is the ONLY loader of that panel.
- **V1 `field.html`** is served ONLY to techs at `/tech/field` (not the owner screen; owner `/owner/field` retired 2026-09-27) and does **NOT** load `_job_detail_panel.js` or any `fdInv*`/`send_invoice` path — so it's not a consumer of the invoice flow (Audit, 2026-10-25).

**Canonical invoice-send endpoint = `POST /owner/api/job/send_invoice`** (`routers/owner/brain.py:767`, `job_send_invoice`). Body `{so_id, method:'email'|'text', send:bool, message?, force_now?}`. `send=false` → **PREVIEW** (returns pay-link url, email, phone, customer, amount, sms_body, has_email, has_phone — DJ reviews before it goes). `send=true` → emails (Odoo `mail.mail`) or texts (`messaging.send`, STOP/DNC guard) the customer an itemized **wscare.pro pay-by-card page**. It reuses `dashboard._create_stripe_tip_link` (builds the Odoo draft invoice via the `sale.advance.payment.inv` wizard + the pay page). **Do NOT duplicate invoice-creation logic — call this endpoint.**

- **UI entry points** (both drive `fdInvOpen(soId, tgt)` → this endpoint, review-first): (1) the surfaced top-level "📧 Send Invoice" button on `v2_job.html` (payment-actions card, next to Record Payment / Zelle), preview renders into `#fd-inv-top`; (2) the older "📧 Send invoice / pay-link" button buried at the bottom of the line-items editor inside the collapsed "📋 Customer & Order Details" card (`_renderFdLines`), preview → `#fd-inv-panel`. `fdInvOpen` takes an optional 2nd arg `tgt` (panel id; defaults to `'fd-inv-panel'`); `fdInvSend` scopes its `#fd-inv-msg`/`#fd-inv-msg-out` lookups to `_fdInvPanel` (the last-opened panel). Shipped 2026-10-25, commit 3b80e4a9, dual byte-QC GREEN.

**How to apply:** owner job-detail work → `v2_job.html` (+ shared `_job_detail_panel.js`); never reach for `v2_field.html`. Any "invoice / bill / pay-link to the customer for this job" need → the `/owner/api/job/send_invoice` endpoint (review-first). See [[feedback_reuse_canonical_endpoint]], [[project_field_deeplink_return_latch]].
