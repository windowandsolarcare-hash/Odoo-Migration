---
name: project_lead_source_valid_values
description: "Valid selection values for sale.order.x_studio_x_studio_lead_source — 'Reactivation' is NOT valid"
metadata: 
  node_type: memory
  type: project
  originSessionId: 3b84512f-52f2-41f6-b8e7-d6c6919c44ee
---

`sale.order.x_studio_x_studio_lead_source` is a selection field. Valid values (verified 2026-05-24):

Angi, Calendly, EDDM, Google, Herald, Home Advisor, Magnet/Drive By, NextDoor App, Note Card, Referral, Repeat Client, Ryan Fewster, Springtime Del Webb, Thumbtack, WASC Web Site, Web Site, Yelp

**Why:** Used in book_reactivation tool. 'Reactivation' was used by mistake — caused ValueError on SO create.

**How to apply:** For reactivation bookings, use `'Repeat Client'`. For Calendly bookings (zapier_calendly_booking), use `'Calendly'`.

---

`sale.order.x_studio_x_studio_x_studio_job_type` is also a selection field. Valid values (verified 2026-05-24):

Annual Gutter Flush, Cobweb Clean, Combination of Services, Commercial Inside & Out, Commercial Outside, Dr. Appointment, Gutter - Inspect and Clean, Inside Only Windows, Install Downspout, Outside Windows and Screens, Personal Time, Pressure Washing, Quote, Reactivation Lead, Repair, Screen Repair, Screen(s) - New, Service, Solar Panel Cleaning, Touch up, Windows Full - IV, Windows Inside & Out - No Screens, Windows Inside & Outside - Larger Home, Windows Inside & Outside Plus Screens

**Why:** Workiz `type_of_service_2` values (e.g. 'On Request') do NOT map to Odoo job type selection values — caused ValueError on SO create in book_reactivation.

**How to apply:** Only set this field if the value is in the known list above. Omit it otherwise — leave blank and set manually. The valid list is hardcoded in the book_reactivation handler (`_VALID_JOB_TYPES` set).
