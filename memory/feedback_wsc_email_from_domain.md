---
name: feedback_wsc_email_from_domain
description: "CRITICAL: every Window & Solar Care CUSTOMER email must set email_from='windowandsolarcare@gmail.com'. Odoo has TWO Gmail send servers (W&SC + Saunders dan@scenicartprint.com) and routes by from-address match — a blank/wrong from can leak a W&SC email out under scenicartprint.com."
metadata:
  node_type: memory
  type: feedback
  originSessionId: 44fd339a-14fd-42e2-adef-f1ae97081400
  modified: 2026-07-26T21:50:32.291Z
---

**DJ, 2026-07-26 (explicit):** "all emails need to go out under windowandsolarcare[.com] not scenicartprint.com."

**Why (verified in Odoo):** the shared Odoo instance has **two outgoing mail servers**, both Gmail SMTP:
- **Window & Solar Care — Gmail**: user + `from_filter` = `windowandsolarcare@gmail.com`.
- **Saunders Printing — Gmail**: user + `from_filter` = `dan@scenicartprint.com`.

Odoo picks the outgoing server whose `from_filter` matches the message's `email_from`. So a W&SC email is only guaranteed to leave via the W&SC server (and appear from windowandsolarcare) if **`email_from` is exactly `windowandsolarcare@gmail.com`**. If `email_from` is blank or something that matches neither filter, Odoo can fall through to the Saunders server and the customer sees **dan@scenicartprint.com** — a cross-business leak. (There is NO windowandsolarcare.com SMTP; "windowandsolarcare.com" colloquially = the windowandsolarcare@gmail.com account. Both W&SC (company 1) and Saunders (3) have `email=windowandsolarcare@gmail.com` at the company level — don't rely on company email; rely on `email_from`.)

**How to apply:**
- Any `mail.mail` create for a W&SC customer → set `'email_from': 'Window & Solar Care <windowandsolarcare@gmail.com>'` (or bare `windowandsolarcare@gmail.com`). Never leave it blank; never let it inherit a default.
- Note: existing INTERNAL alerts to DJ use `email_from='noreply@window-solar-care.odoo.com'` (matches neither filter) — fine for self-alerts, but NOT for customer-facing mail.
- Safest for customer-facing review: create a **Gmail DRAFT** in the windowandsolarcare@gmail.com account (via the Gmail tool) — it's inherently from the right account, and DJ presses Send. See [[feedback_email_draft_first_always]], [[feedback_email_via_odoo]].
