---
name: project_workiz_exit_field_editability
description: KEY future requirement — when Workiz is dropped (soon), the Render field assistant detail screen must become EDITABLE (add/edit job fields, descriptions, notes). Today it's read-only feedback. DJ refuses to edit in the Odoo UI; everything must be on Render.
metadata:
  node_type: memory
  type: project
  originSessionId: ff199142-d29c-4bba-851b-f9d45aa43d20
---

# Workiz exit → field app must become editable (DJ, 2026-06-08)

**The core requirement DJ defined:** Today the field assistant detail screen is **mostly read-only — "just feedback, spinning back what's in the field."** The only edits today are narrow (field_note save, customer to-do notes, payment, timer, quote). Job data itself (description, job type, time, services, etc.) is **created/edited in Workiz** and synced to Odoo.

**When Workiz is dropped (DJ says "shortly"), that input path disappears.** DJ will then have **no way to add or edit job fields** — and he explicitly **will NOT go into the Odoo web UI to do it** ("I don't want to head out to Odoo and have to change Odoo in Odoo UI; I want to have it all on Render").

So the Workiz-exit project MUST include: **add + edit job fields directly from the Render detail screen** — create a job, edit description/notes, job type, date/time, services/line items, etc. — all in the field app, writing straight to Odoo via the existing odoo_rpc layer.

## What got TABLED until this project (2026-06-08)
DJ tabled these because they're really one decision inside the bigger editability project, not one-offs:
- **Job description display + editing** on the detail screen (smart-hybrid display was approved, source = SO `notes_snapshot1`, SO-scoped). [[project_note_scopes_field_app]]
- **Personal Time blocks created directly in Odoo** (proven working — [[project_personal_time_direct_odoo]]) instead of via Workiz. For now DJ keeps making these in Workiz the normal way.
- The whole question of **personal jobs vs job descriptions vs SO notes vs partner/customer notes** — resolve holistically when editability lands.

## Related
- [[project_zapier_to_render_migration]] — moving Phases 3/4/5/6 off Zapier (prerequisite-ish; both are part of de-Workiz-ing).
- [[project_note_scopes_field_app]] — the note-scope map (SO vs partner) that must inform the editing UI.
- [[project_personal_time_direct_odoo]] — direct-create recipe + the action_confirm external-tax bug to work around when creating SOs from Render.
