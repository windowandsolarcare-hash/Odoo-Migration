---
name: feedback_display_implies_crud_parity
description: Any field/list the app DISPLAYS ships with edit/add/delete (full CRUD parity) in the SAME build; a display-only build fails QC unless DJ explicitly said read-only.
metadata:
  node_type: memory
  type: feedback
  originSessionId: c357000c-2b48-423f-90ce-2e1b8f1f9669
  modified: 2026-10-11T18:07:45.420Z
---

★ (DJ 2026-10-11, FLEET_GOVERNANCE §13) Any field / list / value the app SHOWS a user must ship WITH its edit + add + delete path (full CRUD parity) in the SAME build — never a "display now, make it editable later" follow-up. DJ's words: "I don't need it just as a display... everything I display I need to be able to edit... that should just be automatically assumed and picked up as a full build."

**Why:** DJ (and Cheryl) run the business entirely through the app, never Odoo directly — a value they can see but not change is a dead end that sends them hunting for another interface. A display-only surface is an incomplete build, not a milestone.

**How to apply:** Build add/edit/delete alongside any new display from the start. Default = full CRUD; read-only is the exception that needs DJ's EXPLICIT say-so (derived/computed values, an audit log, or another system's record → ask via the §11 picker, don't silently ship view-only). Lead QC FAILS a display-only feature unless DJ scoped it read-only. Owner app AND Cheryl's app. Extends [[feedback_existing_odoo_field_build_ui_dont_ask]] (existing Odoo field → build the UI) and [[feedback_never_send_dj_to_odoo]] (the app is THE UI; every field needs an in-app pathway). Origin: the Cheryl task-checklist shipped tick-only; DJ wanted add/edit/delete of the steps too.
