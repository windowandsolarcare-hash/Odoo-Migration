---
name: project_note_scopes_field_app
description: The three note systems in the field assistant and their SCOPE (partner vs SO). Job description = SO-scoped (notes_snapshot1); customer notes = partner-scoped (persist across all jobs at a property).
metadata:
  node_type: memory
  type: project
  originSessionId: ff199142-d29c-4bba-851b-f9d45aa43d20
---

# Field assistant note systems — scope matters (clarified 2026-06-08)

There are THREE distinct "note" concepts. Getting the scope wrong matters because DJ **reuses the same property partner for every job there** — a partner-scoped note bleeds onto every future visit.

| Note | Stored | Scope | Endpoint |
|---|---|---|---|
| **Editable "field note"** (Save box in detail panel) | `res.partner.x_studio_x_field_note` | **Partner** (customer OR property) — repeats every visit | `/owner/api/partner/field_note` (dashboard.py ~4295) |
| **Notes list** (purple to-do/permanent card) | `project.task` filtered by `partner_id` | **Partner** — repeats every visit | `/owner/api/todos/for_partner?partner_id=` |
| **Job description** (Workiz JobNotes) | `sale.order.x_studio_x_studio_notes_snapshot1` (text) | **SO / per-visit** — that job only | returned by job APIs if added |

## Rule of thumb
- **Per-visit info** (e.g. "20 Panels, Wife=Millia", "Turn on the RV fridge") → belongs on the **SO** (`notes_snapshot1`). Disappears after that job. NEVER store as a customer note, or it haunts every future job at that property.
- **Recurring info about the place/customer** ("dog in yard", "gate sticks", access quirks) → belongs as a **customer note** (partner-scoped) — repeating every visit is the desired behavior.

## In progress (2026-06-08)
DJ approved a **smart-hybrid display** of the job description on the detail screen: short descriptions show inline, long ones collapse to a tappable "📝 Description ▸" bar. Source = `notes_snapshot1` (SO-scoped). Personal Time blocks created directly in Odoo should write their description into `notes_snapshot1` too (not a line_note) for one unified display. See [[project_personal_time_direct_odoo]]. Backend must add `notes_snapshot1` to the job objects in api_dashboard / api_upcoming / api_past_jobs; frontend adds a description card in openJob. (Build pending DJ confirm on display-only vs editable.)
