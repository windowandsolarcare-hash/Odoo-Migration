---
name: project_booking_is_book_only_no_reply
description: "DJ's booking-from-text workflow is BOOK-ONLY — the tool books the job, it does NOT draft a customer reply. Confirmation texts auto-fire from Workiz when DJ sets the job STATUS."
metadata: 
  node_type: memory
  type: project
  originSessionId: 4ab12b63-cc8f-44de-b410-58b38aa2a6c9
  modified: 2026-07-30T19:01:35.642Z
---

DJ, on the booking-from-text specialist (2026-07-29): "there is no reply to Kevin. simply book the job. when I link over to Workiz I'll change the job status to automate the text."

**The workflow — the tool DECIDES reply-vs-book per conversation (refined 2026-07-29):**
- **Settled / customer already agreed / just a scheduling action** (like Kevin — said yes, only needs to be put on the books) → **skip the reply, go straight to BOOK** (Odoo → Workiz). The customer confirmation **text fires automatically from Workiz** when DJ sets the job STATUS (Scheduled / Send Confirmation - Text / Next Appointment - Text — existing Workiz status→text automation, Phase 4). No draft needed.
- **Still needs back-and-forth** (a question, price inquiry, negotiation, anything unresolved) → **draft the reply** (keep this — DJ: "there are still times we want a reply").
- So the reply machinery STAYS; it just must NOT force a reply when the deal is done. Add a "ready to book — no reply needed" branch. The intelligence to add = detect "is there anything left to say, or just book it?"
- **End-to-end success for a settled thread (Kevin) = the screenshot results in a BOOKED job, no reply.**

**Why:** the original booking specialist FORCED a draft-a-reply-for-DJ-to-copy/paste flow on every thread. But when the customer already agreed, DJ doesn't text back — he books, and the text is Workiz-status-automated. Forcing a reply there is wrong; forcing book-only everywhere is ALSO wrong (some threads need a reply).

**How to apply:** any "AI reads a text and acts" feature for DJ should DO THE ACTION (book/reschedule/etc.), not produce text for him to send. Customer messaging = Workiz status automation. See [[feedback_route_work_to_claude_code]] and the booking bug (tool also once conflated PAYMENT timing "pay in fall" with SERVICE timing "clean next week" — a real customer commitment to do the job next week is a NEXT-WEEK booking, not a fall one).

**Validation stance (DJ, same day):** DJ does NOT want the lead session to hand-book jobs as a workaround — "you doing it isn't proving the specialist works end to end." Fix the specialist, then prove it by running the REAL screenshot through the tool. Kevin Armintrout / 17 Stonecrest thread = the regression test case.
