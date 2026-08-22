---
name: project_booking_specialist
description: "Fifth specialist + FIRST AI-driven one, LIVE 2026-07-27: routers/owner/specialist_booking.py = 'Book from a text'. Separate photo-upload page (/owner/api/booking/intake) → Claude vision reads the text screenshot, decides book-vs-reply FORK, matches customer, proposes route-tight dates, drafts Dan's reply per an editable HANDBOOK, approval card. Handbook rule: >2 days late = open with a plain apology."
metadata:
  node_type: memory
  type: project
  originSessionId: 44fd339a-14fd-42e2-adef-f1ae97081400
  modified: 2026-08-10T22:49:44.878Z
---

**2026-07-27 — fifth specialist, first AI-DRIVEN (handbook + job description + model, not deterministic).** Spec: `3_Documentation/BOOKING_SPECIALIST_BRIEF.md`. `routers/owner/specialist_booking.py`, registered main.py prefix /owner.

**Flow (DJ's role = 3 touches):** (1) DJ uploads text-thread screenshots on a SEPARATE screen `/owner/api/booking/intake` (`<input accept="image/*">`, no capture → defaults to photo library; client-side resizeImage 1600px q0.85). (2) `POST /api/booking/process` (multipart field `photo`) runs Claude **vision** (`get_anthropic_client().messages.create(model=CLAUDE_MODEL, image blocks)`) → JSON {customer_name, phone, service, proposed_times, last_customer_message_date, intent:book|reply, intent_reason, transcript}. Matches customer (`_find_customer` phone-first, else res.partner name ilike + `company_id in [1,False]`). Proposes route-tight dates via `scheduler._city_centroid`+`_rank_days_at` (no SO needed, from the customer's city). Drafts the reply via a second Claude call using JD+HANDBOOK. Submits ONE `approval` card (source booking, urgency interrupt, id `booking:<partner_id|phone>`). Returns the result so the intake page shows it immediately (editable draft + Copy + Book/Reply + a FLIP toggle). (3) DJ approves.

**THE FORK (DJ's core requirement):** vision classifies **book** (customer committed — 'book me'/accepts a time/'next availability') vs **reply** (asks a question / wants options / uncommitted; default when unsure). Book card → approve books the job; Reply card → approve just gives the reply to send (NO job). DJ can FLIP either way on the page before approving (safety for a misread).

**HANDBOOK + JOB DESCRIPTION = editable governance** in `ir.config_parameter wsc.booking.job_description` / `wsc.booking.handbook` (seeded on first read; GET/POST `/api/booking/handbook`). Rules: voice=Dan first-person/brief; the fork; **LATE RULE — customer's last msg >2 days old → OPEN with a brief plain apology, no excuses** (server computes days_late from the vision-extracted last_customer_message_date; passes a NOTE into the draft prompt); only offer dates from the provided route-tight list; never sends.

**Approve** `POST /api/booking/approve`: reply → log partner chatter + delete card + return text (copy). book → canonical `dashboard.execute_write_tool('book_reactivation', {partner_id, partner_name, job_datetime:'YYYY-MM-DD HH:MM:SS', service_type})` (reuses parked graveyard job, sets date_order, confirms SO, marks CRM Won; does NOT auto-text — [[project_booking_approve_no_confirm_text]]), then log + close + return the reply text to paste. Idempotent-ish (delete_item on close).

**Twilio-proof:** screenshot intake is the temporary front end; post-port swap it for the SMS webhook and keep the extract→fork→match→propose→draft brain. Until then DJ copy-pastes the reply.

**ENTRY POINT NOW LIVE (verified 2026-08-10):** the v2 launcher (v2_apps.js) has a chip 📩 **"Book from a text"** → `/owner/api/booking/intake` (All tab). Also a 📥 "Booking Requests" chip → v2_booking.html (the online-booking review, different thing). So DJ reaches it from the 🚀 launcher, not just a raw URL anymore. Vision + draft quality still want real-screenshot testing. Touched shared files: main.py (additive). See [[project_operating_system_vision]], [[project_agent_mail_channel]], [[project_billing_specialist]], [[project_reschedule_specialist]], [[feedback_reuse_canonical_endpoint]].
