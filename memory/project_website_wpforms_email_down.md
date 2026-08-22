---
name: project_website_wpforms_email_down
description: windowandsolarcare.com WPForms leads are SAVED but email notifications were dead (WP Mail SMTP Gmail connection broken) — quote alerts never delivered; plus the new-customer intake creation recipe
metadata: 
  node_type: memory
  type: project
  originSessionId: 43ecbb04-6bcc-42b6-aae3-303ecce01b59
---

**Discovered 2026-07-07: the website's outgoing email is BROKEN, so form-submission notifications were never delivered.** windowandsolarcare.com (WordPress + WPForms) uses **WP Mail SMTP** with the **Gmail** mailer, and it logged **`invalid_grant / Bad Request`** — the Google OAuth send-connection is dead (same fragile Google-token pattern as the Vault/notes app, see [[project_vault_evernote_drive]]). So for however long it's been broken, the site sent NO email → nobody got "new quote" alerts. **Compounding:** the WP admin/notification email is **`dan@scenicartprint.com`** (Saunders Printing), NOT windowandsolarcare@gmail.com — so even when it did send, alerts went to the wrong inbox.

**★ Nothing was lost — WPForms SAVES every submission to the DB regardless of email.** View/export at wp-admin → WPForms → Entries (or Tools → Export → xlsx). WPForms entries are NOT reachable via the WP REST API (no wpforms namespace; only pages/posts/media/settings are). So to analyze: DJ exports xlsx → Claude reads with openpyxl.

**What the Free Quote form (id 2893, /free-quote/) actually held (30 entries, exported w/ Entry Date):** ~ everything from Nov 2025→Jan 2026 was lead-gen SPAM (thevirtualsalesgroup.com / smartassistanthub.com, fake "122 Main St New York"); newest REAL lead = July 2024; real leads span Apr 2021–Jul 2024; 2020 rows = DJ's own tests (dj@mirrokoat.com, dreamhosttest, dansyourrealtor, dan.markethouses) + Cheryl. Newsletter form (id 2889, 70 entries) = ~all bot spam (sigismail.com, alabamahomenetwoks.com). Cross-checked 12 real Free-Quote leads vs Odoo by PHONE (emails aren't stored on Odoo partners; res.partner has NO `mobile` field in Odoo 19): already-customers = Helen Stuart="Helen Tom Stewart"(7 jobs), Myra Lang="Myra Lane"(11), Robin Elder(7), prob Sandy="Santya Parker".

**8 never-served real leads ADDED as new customers 2026-07-07** (DJ: "still worth reaching out, they still have windows and solar panels"). Contact IDs **27110 Beth Swango, 27112 Ron Barlass, 27114 Alicia Parrill, 27116 Sheri Dettman, 27118 Gilberto Rebolledo, 27120 Tom Stone, 27122 Kristi McCreary, 27124 Kenya Washington** (+ a Property child each). Each comment tagged `[Web Lead - Free Quote form] {date} - {service} - never contacted...`. City missing for Sheri (Damascus Dr) + Tom (zip 92270=Rancho Mirage). NEXT (DJ will ask): draft a friendly outreach EMAIL + SMS version for all 8.

**★ NEW-CUSTOMER INTAKE RECIPE (from routers/owner/new_job.py — the "New Order → New customer" flow):** a customer = a **Contact** res.partner + a **Property** res.partner child. Create via `res.partner create` (pass the vals DICT directly — my xmlrpc helper double-wraps `[vals]` → returns a LIST id → breaks parent_id; call create(vals) not create([vals])).
- Contact vals: name, phone, email, street, city, `state_id=13` (California, hardcoded), zip, is_company=False, x_studio_x_studio_first_name, x_studio_x_studio_last_name, `x_studio_activelead='Active'`.
- Property vals: name=street, parent_id=<contact id INT>, phone, street, city, state_id=13, zip, is_company=False, **`type='delivery'`** (NOT 'contact' — avoids Odoo address-inheritance forcing all a customer's properties to share one street), `x_studio_x_studio_record_category='Property'`, x_studio_activelead='Active', x_studio_x_type_of_service, x_studio_has_window_service (bool), x_studio_has_solar_service (bool), optional x_studio_x_gate_code / x_studio_x_frequency / comment='<p>[Job Notes]...'.
Endpoints: POST /owner/api/intake/contact, /api/intake/property, /api/intake/create-job.

**Why:** broken form email = silently lost leads; a real business risk. **How to apply:** FIX the email (either re-authorize the Gmail mailer in WP Mail SMTP, OR — durable — switch to "Other SMTP" = smtp.gmail.com:465 SSL with a windowandsolarcare@gmail.com App Password, which doesn't expire) AND set each form's notification "Send To Email Address" to windowandsolarcare@gmail.com. Add anti-spam (CAPTCHA) to the Newsletter form. See [[project_twilio_a2p_and_entity]] (the SMS-consent checkbox was just added to this same Free Quote form).
