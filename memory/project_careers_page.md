---
name: project_careers_page
description: "Careers/hiring page on the marketing site: windowandsolarcare.com/careers (Odoo website.page wsc.careers) + footer 'Careers' link + /careers-thank-you. Evergreen copy, resume-upload apply form that emails windowandsolarcare@gmail.com. Built 2026-10-08 by Web. Includes the Odoo website-form gotcha (hand-authored forms don't auto-bind the submit JS)."
metadata:
  node_type: memory
  type: project
  originSessionId: f76e5ab2-b974-4483-8681-cf3a298418b6
  modified: 2026-10-08T21:25:08.499Z
---

**Built 2026-10-08 by Web (DJ via Cheryl's idea: add a hiring link, evergreen, form → email, resume attachable).**

**Pages (Odoo website, website_id=1):**
- `/careers` — view key `wsc.careers` (id 3856), `<t t-call="wsc.page">`, uses site classes (phead/wrapx/split/card/ticks). Evergreen copy ("always glad to meet good people") + a swappable **"Right now we're hiring a Lead Technician"** line. `website_indexed=True`, published.
- `/careers-thank-you` — view `wsc.careers_ty` (id 3857), page 23. `website_indexed=False`.
- **Footer "Careers" link** lives in `website.footer_custom` **id 2337** (the website_id=1 extension, Company column) — NOT id 1627 (that's the generic website=False one). Two views share the key; edit 2337.

**Apply form → email:** fields Full name / Phone / Email / experience textarea / **resume file upload**. Submits to **`POST /website/form/mail.mail`** (Odoo's "Send an Email" website-form action, model mail.mail). Result: an email to **windowandsolarcare@gmail.com**, subject **"JOB APPLICATION (Careers page) - windowandsolarcare.com"**, body lines prefixed **"JOB APPLICANT - ..."** (DJ wanted it unmistakably a job app in multiple places; the leading "This message has been posted on your website!" line is Odoo-hardcoded, can't remove). **Resume attaches** to the email AND persists in Odoo as an `ir.attachment` on the mail.mail (safety net if email ever fails). hr_recruitment IS installed but website_hr_recruitment is NOT (so no native /jobs board).

**★ GOTCHA — Odoo website-form JS does NOT auto-bind on a hand-authored (API-created) page.** Two traps hit here:
1. The controller **requires a `website_form_signature`** hidden input (Odoo injects it server-side at render for any `.s_website_form` form — present in the rendered DOM, NOT in the stored arch). A POST without it → **HTTP 500** (generic page, no traceback in prod). The `csrf_token` (from `odoo.csrf_token`, format `<40hex>o<timestamp>` — do NOT truncate the `o...` suffix) is also required.
2. The `website.form` public interaction (selector `.s_website_form form`) **did not bind the submit button** on the hand-authored page even though the module loaded and the selector matched — clicking the `<a.s_website_form_send>` did nothing (no POST). Cause never fully root-caused; editor-created forms (e.g. /contactus) bind, hand-authored ones don't.
**FIX (what shipped):** dropped `s_website_form_send` and added a **self-wired inline `<script>` (in CDATA)** on the careers page: on submit-button click it validates required fields, builds `FormData(form)` (which includes the injected signature + the file input), sets `csrf_token` from `odoo.csrf_token`, `fetch('/website/form/mail.mail')`, and on a JSON `{id}` success redirects to `/careers-thank-you`. Inline scripts in a website.page arch render + run fine (use `<![CDATA[ ]]>` to avoid XML-escaping the JS). This is more reliable than fighting the interaction binding.

**Testing:** submit via a real browser OR a signed JS `fetch` from the page context (grab `website_form_signature` input value + `odoo.csrf_token`). A raw curl POST can't easily get a session-valid signature. Clean up test mail.mail after — BUT the API user (uid 2) **cannot unlink mail.mail** (cascades to mail.message → security restriction); you CAN unlink the ir.attachment. Gmail connector here is **read-only** (no trash scope) — test emails must be deleted by DJ.

**OPEN — Web's next build (DECIDED 2026-10-08, non-blocking, no rush per Specialists):** Repoint the /careers form to create an **hr.applicant** natively in Odoo so new applications surface on DJ's HUD under Hiring. Decision by Lead (no app endpoint → avoids cross-origin; same Odoo instance as the applicant store). EXACT SPEC agreed with Specialists:
- Flip `ir.model` hr.applicant (id 1028) **`website_form_access=True`** (currently False — form will 403 without it). Verify the needed fields aren't website_form_blacklisted.
- Form `data-model_name="hr.applicant"`; map: Full name→**partner_name**, email→**email_from**, phone→**partner_phone**. hr.applicant has NO `description` field in this Odoo 19 — figure out where the experience text lands (chatter note / a field); verify before relying on it.
- Stamp hidden **source_id=15** (utm.source "Careers Page" — CREATED 2026-10-08), **job_id=1** ("Window Cleaner" — the only hr.job, what the pipeline filters on). Records land at **stage_id=1** ("New"). Public forms may not allow setting m2o source/job directly → if blocked, stamp via a base.automation on create.
- Resume file field → **ir.attachment** on the applicant (hr.applicant is a mail.thread → works).
- **Keep the email-to-gmail** too (Lead: "if easy") — e.g. a base.automation/server action on hr.applicant create (source_id=15) emailing windowandsolarcare@gmail.com.
- Repoint the inline submit script's fetch from `/website/form/mail.mail` → **`/website/form/hr.applicant`** (same signature+csrf mechanism).
- **Specialists' HUD filter** (their deploy #2, after interview-roster card): `hr.applicant where source_id==15 AND stage_id==1` via /api/hiring/applicants; they add `{15:'Careers Page'}` to hiring.py SOURCE_LABELS. **PING Specialists when real careers applicants start landing** so they verify the filter end-to-end.
- Until this ships, the form still works via mail.mail (emails DJ); no broken state.

Related: [[project_del_webb_landing_page]], [[project_website_cutover_dns]], [[feedback_verify_limits_before_declaring]], [[project_hiring_applicant_shadow_partners]].
