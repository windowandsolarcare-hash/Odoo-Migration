---
name: project_inbox_intent_buttons
description: "Inbox reply now has INTENT BUTTONS (DJ: 'a button I push to say what I'm looking for'): 📅 Booking link · ✅ Confirm · 💬 Reply. DJ picks intent, AI drafts, he edits + sends. Specialist built the UI + POST /api/inbox/intent; lead fixed the shared _draft_reply so booking links are REAL (no [booking tool link] placeholder). 2026-08-07."
metadata:
  node_type: memory
  type: project
  originSessionId: 1e80ea0d-78f5-4aa2-bc1d-25aace876ab5
  modified: 2026-08-07T16:35:53.762Z
---

**DJ (2026-08-07, re customer Dana Zusman's VM asking to book):** "I want to respond with a booking link. AI can decide but I'd also like a BUTTON I push to say what I'm looking for." He wants to pick the INTENT; AI does wording; the SYSTEM sends (not Claude Code manually). Routed to the specialist (their inbox/reply surface) per the don't-duplicate rule; lead took the shared drafter fix.

## Shipped (specialist — v2_inbox + sms.py)
- Inbox reply has a 3-button intent row **📅 Booking link · ✅ Confirm · 💬 Reply** (above ✨ Ask-Claude-to-rewrite). NEW **`POST /owner/api/inbox/intent {c, intent}`**:
  - **booking** → resolve thread partner → `ai_sched_message(pid, phone, first, wscare.pro/c/<make_token(pid)>, ...)` → warm booking invite w/ the REAL link. PARTNER-scoped, works with NO SO (Dana's case).
  - **confirm** → `_find_upcoming_job(pid)`; scheduled SO → opens **WSCSendBox mode:'confirm'** (branded ?c=1). No job → friendly error.
  - **reply** → thread-aware `_draft_reply` into the box.
- Tap → drafts into the editable box (or opens WSCSendBox) → DJ edits → Send (canonical inbox send / sched-launch → thread). `wsc_sendbox.js` included on v2_inbox.

## Shipped (lead — the shared drafter fix, sms.py)
- `_draft_reply(..., booking_link='')`: if not passed, resolves `from_number → _find_customer → https://wscare.pro/c/<make_token(cid)>`; prompt now says "use EXACTLY this link, NEVER a placeholder like [booking tool link]" (or, no link → don't write a placeholder). Kills the `[booking tool link]` bug in the general ✨ Suggest / 💬 Reply everywhere (inbox + follow-ups). (Specialist's booking INTENT already forced the real link; this covers the free-reply path.)
- Canonical customer booking link = **`https://wscare.pro/c/<make_token(contact_id)>`** (booking.py `make_token` = `<pid>-<10hex hmac(BOOKING_TOKEN_SECRET, pid)>`; default secret `wsc-portal-2026`).

See [[project_wsc_sendbox_shared]] [[project_auto_confirm_branded_page]] [[feedback_reuse_canonical_endpoint]].
