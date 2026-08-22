---
name: project_calendly_booking_alert
description: "What fires when a customer books via Calendly online, and the 2026-06-25 rebuild that added a reliable My Day reminder (the old alert was a passive Booking-Requests hub card with no notification)."
metadata: 
  node_type: memory
  type: project
  originSessionId: 8794a0de-b651-444b-8ec4-52ed56f6927d
---

**Calendly online booking → handler = `zapier_calendly_booking_FLATTENED_FINAL.py`** (Zapier "Code by Zapier"; fetched from GitHub Odoo-Migration `1_Production_Code/` on every run, so push to main = deploy). It's the REACTIVATION booking path (customer got a reactivation text → booked a city Calendly link → there's already a Workiz "Reactivation Lead" job + crm.lead with the UUID). Flow: 3A find property/contact by `street ilike` → 3B find opp w/ UUID → 3C update Workiz job (JobDateTime, type; **SubStatus left BLANK on purpose** — DJ confirms manually) → 3D lead Won → 3E create+confirm Odoo SO → 3F update email. SubStatus blank = **customer NOT auto-confirmed**; DJ must open Workiz, add line items, set SubStatus "Send Confirmation - Text".

## The alert problem (found via Dennis Gladu, booked 2026-06-24)
The live flow only called `add_calendly_incoming()` → queues the booking into `ir.config_parameter 'booking.calendly.incoming'` (JSON list) which feeds the **owner Booking Requests page** (`/owner/booking_requests`). That's a **passive page DJ doesn't watch + NO notification** → bookings sat silently. `create_odoo_activity` (mail.activity) was commented out. So for Dennis everything processed (SO 004609, Workiz LBOW7D, July 7 1pm) but DJ got no alert — only the raw Calendly email.

## Rebuild (2026-06-25, commit 8e86dc0)
Added `create_booking_alert(so_id, workiz_uuid, customer, datetime_pacific, service_type, address, contact_id)` = a **plain `project.task` My Day reminder** (My Day = the notifying list: 7am digest + due-time push). Bulletproof — only core fields (name, description, project_id False, user_ids [(4,2)], date_deadline=today, partner_id); NO custom x_myday_* fields (avoids a bad-field create failure); due today so it surfaces immediately. Workiz link front-and-center. Deduped by UUID (Calendly retries 25x/24h). Called right after the SO in main, alongside the (kept) hub card. ALSO: every failure path now drops a fallback task — 3A/3B already did; added 3C/3D/3E with `create_fallback_todo(..., workiz_uuid=...)` so the UUID/link rides along. Fixed fallback `user_ids` `[ODOO_USER_ID]` → `[(4, ODOO_USER_ID)]` (proven form). NOTE: Zapier picks up the new code on the NEXT booking; Dennis (old run) won't get the reminder retroactively.

## Bigger picture
Calendly + this Zapier path are LEGACY — being replaced by self-hosted booking (`/api/intake/*`, books direct, no Workiz) — and Workiz leaves ~2026-06-29 (3C breaks then). See [[project_calendly_offzapier_odoo_webhook]], [[project_customer_portal_booking]], [[project_command_center]].
