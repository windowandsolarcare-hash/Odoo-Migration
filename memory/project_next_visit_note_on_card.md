---
name: project_next_visit_note_on_card
description: "The ⭐ \"next-visit note\" (Log a touch) now shows on Command Center schedule cards. Field = res.partner.x_next_visit_note."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-08-19T13:57:25.176Z
---

**Field:** the ⭐ next-visit note (set via "📣 Log a touch" → check "Flag for the next visit") is stored on **`res.partner.x_next_visit_note`** (ttype text, field id 21371). Written by `reactivation.py api_touch` (`POST /api/touch`, `next_visit=true`) to the partner passed in (the job's CONTACT partner). The field assistant reads it into the `#next-visit-banner` on the job detail (`field.py loadNextVisitNote`).

**Built 2026-08-19 (DJ):** DJ logs a touch note on a customer (e.g. Nancy Tohl = "Bring CLR") but it never surfaced on the **Command Center** schedule card — he could only see it inside the job detail. (His first description sounded like the field job-detail banner being "covered by the green confirmed bar"; the screenshot showed it was actually the Command Center card, which simply had NO note indicator — the green ✓ CONFIRMED strip is a top ribbon, it wasn't covering anything.) Fix:
- **Backend** `dashboard.api_calendar_jobs`: added `x_next_visit_note` to the parent_map read + a per-job `'note'` field (from the card's parent contact, same parent resolution as `last_contacted`). Commit dashboard b13bcda.
- **Frontend** `v2_command.html`: both row builders (on-schedule ~720 + mapJob ~571) carry `note:j.note`; the card renders `<div class="j-note">⭐ <note></div>` right under the address — **amber (#fff3cd/#f0c000)** on purpose so it stands apart from the green CONFIRMED bar. Commit e65ff3d.

Lesson: when DJ says a UI element is "covered," get a SCREENSHOT before assuming the screen — his "job detail / covered by confirmed bar" was really "Command Center card / note not shown at all." See [[project_blower_banner_gutter]] (same v2_command card file + amber banner style) and [[feedback_field_readability_sunlight]].
