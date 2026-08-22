---
name: feedback_never_send_dj_to_odoo
description: "★ GOVERNING RULE: DJ (and every user) NEVER touches Odoo. Odoo = invisible backend DB. The Render app is THE complete UI. 'Go into Odoo' is a bug, not an answer — every field needs a Render UI pathway (automation or manual)."
metadata:
  node_type: memory
  type: feedback
  originSessionId: 0e6fb90e-8d05-4272-91a3-ed7ee21488d7
  modified: 2026-08-04T00:44:11.620Z
---

**DJ, 2026-08-03 (stated as the core problem):** "I'd never want to go to Odoo. That is why we created the app. The app sits on top, is the UI for Odoo. I have no desire ever to go to Odoo — that's the app's job. It's strictly a backend database, not to be viewed by me, not to be viewed by any user. So we must build channels/pathways to each field either through automation or through manual entry, but we need to build it through the Render UI."

**Why:** Workiz used to be the single UI where DJ could see/edit EVERY field of a job/customer. Post-Workiz, big chunks of that data have NO UI pathway in the Render app — and the team kept implicitly assuming DJ can "just edit it in Odoo." He can't and won't. Odoo is a database, not a screen. Every gap where the only way to change a value is the Odoo web client is a HOLE to close.

**How to apply:**
- NEVER answer "you'd change that in Odoo" / "go into Odoo and…". If a field has no Render UI path, that is a GAP to build, and I say so + offer to build the pathway.
- Every job/customer field must be reachable in the Render UI — read AND write — via a screen (manual entry) or an automation. The [[project_so_full_start_time_edit]] editor (Customer & Order Detail on the job screen) is the main manual-entry surface for a job; extend it to cover the customer/property record too (address, phone, gate, pricing, frequency, service area) — those live on res.partner and had no UI (2026-08-03 Ella-address incident: DJ asked how to update a texted address; there was no in-app way — exactly the hole).
- When surveying/architecting, treat "which fields still require Odoo" as a first-class gap list. See the lifecycle map + [[project_north_star_comprehensive_crm.md]].
- This is the same spirit as [[feedback_question_when_big_picture_wrong]]: hold the whole-system view, don't leave a field stranded in the DB with no door.
