---
name: project_so_activity_breadcrumb
description: "Per-job \"Activity log\" (v2_field 🧭 button + GET /api/so_activity) reads the SO chatter into a timeline so DJ can see if the CUSTOMER pressed confirm/acknowledge (vs his own manual mark) even after clearing a flag."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0e6fb90e-8d05-4272-91a3-ed7ee21488d7
  modified: 2026-08-11T21:57:20.194Z
---

**DJ's need (2026-08-11):** he sometimes clears a confirm/acknowledge state by mistake and needs to go back and answer "did the customer actually press this button?" Wanted a durable log / breadcrumb.

**Key realization:** the customer actions are ALREADY logged durably — `appt_confirm/appt_reschedule/appt_cancel` (reminders.py) each `_post_so(...)` to the SO chatter with the source ("via page"/"via text"/"via manual"); booking.py `sched_confirm` logs the distinct b1/b2/b3 choice; text-YES logs "✅ Customer confirmed … by text"; DJ's manual marks log "✅ Marked confirmed by Dan (manual)" / "↩ Acknowledgement cleared (manual — DJ)"; sends log "📤 Sent SMS […]". **mail.message chatter is append-only — clearing a state flag never erases it.** The gap was purely visibility: nothing in the app surfaced the chatter (`/api/so_history` returns job facts + payments, NOT messages), and DJ never touches Odoo.

**Build (commits dashboard 5dff93b, v2_field 4db9cbc):**
- `GET /api/so_activity?so_id=` (dashboard.py, before api_so_history) reads `mail.message` (model sale.order, res_id) newest-first, strips HTML, skips empty field-tracking rows, converts date→PT, and classifies each line **customer / manual / send / system**. Classification checks 'manual'/'by dan' BEFORE 'customer' — because `appt_confirm(source='manual')` logs "Customer confirmed (via manual)" which is actually DJ, and must NOT read as a real customer press.
- v2_field.html: `🧭 Activity` button in the brain-row → `openActivity()` → modal timeline with colored actor tags (👤 Customer green / ✋ You manual amber / 📤 Sent blue / • system grey) + PT timestamps.

So "did the customer press it?" is now answerable in-app for any job, forever. Reuses existing chatter — no new event store, no changes to the lead's handlers. Related: [[project_send_acknowledgement_button]], [[project_maint_ack_backfill]].

**The exact-confirm-time refinement (DJ 2026-08-11):** DJ's #1 use is the EXACT moment the customer confirmed. That IS the mail.message `date` (≈ the tap time), returned as `ts`. Gotchas fixed: (1) the body sentence "Customer self-scheduled: Tuesday Aug 11 at 9:30 AM" contains the APPOINTMENT date, which DJ confused for the confirm time — the confirm time is the `ts` timestamp, separate. (2) The 🚀 launcher FAB docks top-right and was covering a right-aligned timestamp → moved the timestamp to the LEFT (next to the actor tag), bold, `var(--ink)` (theme-aware, not the nonexistent --ink-1 which would be dark-on-dark). (3) Timestamp now to the SECOND (`%-I:%M:%S %p`) since DJ wants "exact." Commits dashboard 5ba3090, v2_field 47967d5.
