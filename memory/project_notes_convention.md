---
name: project_notes_convention
description: DJ note conventions (2026-07-21) — Property Note (Permanent) = standing facts on x_studio_x_field_note; Log a touch = temporary/dated notes.
metadata:
  type: project
---

DJ decided 2026-07-21 to keep the Job Screen Property Note card (was near-dead — 1 note in whole DB) and use it deliberately:

- **Property Note (Permanent)** — card on the Job Screen, stores ONE standing note per customer in res.partner `x_studio_x_field_note` (edit/save/clear via /owner/api/partner/field_note). For permanent property facts: pets, access quirks, ring twice. Card header renamed to include "(Permanent)".
- **Log a touch** — for TEMPORARY/dated notes (calls, replies, in-person). Goes to the CRM activity log with a date.

**Why:** one field kept getting confused with the other note systems; naming + convention fixes it.
**How to apply:** never repurpose x_studio_x_field_note for dated/temporary content; point temporary note features at the touch log instead.
