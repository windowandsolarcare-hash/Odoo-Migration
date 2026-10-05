---
name: feedback_no_ai_offered_dates_use_link
description: "DJ standing rule (2026-10-05, approved): no AI-written customer text may EVER offer/suggest an open date or time in free text — real offers go through an offer link (Reserve→slot_offers) or the booking link so the slot is HELD. Exception: an already-booked job's date in a confirmation/reminder. Applies to the VOICE assistant + Cheryl's app too."
metadata:
  node_type: memory
  type: feedback
  originSessionId: c357000c-2b48-423f-90ce-2e1b8f1f9669
  modified: 2026-10-05T10:22:01.587Z
---

**DJ 2026-10-05 (approved, relayed via Dispatcher).** No AI-generated customer-facing text may EVER state, offer, or suggest a specific OPEN / available date or time in free text. Every real offer of a time must go through an **offer link** (Reserve → `slot_offers`) or the **booking link**, so the slot is actually HELD for that customer. A raw time in free text is an **unreserved double-offer** waiting to happen — two customers can grab the same slot. The message INVITES (tap the link to pick a time); it never schedules.

**Exception:** a text about an ALREADY-BOOKED job (confirmation / reminder) MAY state that job's date/time **from the real job record** — that's a fact about a held appointment, not an offer.

**Also never imply the visit is already arranged** ("booked / set up / have you down / all set / reserved you") unless it IS a confirmed job. Pairs with the never-one-tap-send rule and the no-inventing-customer-lines rule.

**Scope:** every customer-text generator — inbox rewrite (`followups.ai_rewrite`), inbox suggest/drafter, `sms.ai_sched_message`, follow-up / reactivation drafters, AND the **VOICE assistant** (`/owner/ask` in dashboard.py — its SYSTEM_PROMPT + every tool). Applies to **Cheryl's app** too (her customers).

**The leak class (know it):** availability GROUNDING force-fed into a FREE rewrite surfaces real open slots the model then frames as offers. Verified 2026-10-05: `sms._grounded_context` (~l.1156) force-appends `availability` whenever scheduling is implied → `_inbox_ai_facts(['availability'],pid)` returns real open slots (Oct 9 11:00 / Oct 23 8:00) → fed into `followups.ai_rewrite` (l.441) → the model stated them as offers ("I've got you down... two open slots..."). Real availability, surfaced where it must not be. Fix: a free rewrite must NOT receive bookable slot times (suppress availability grounding for rewrite via an `allow_availability=False` arg); availability grounding belongs ONLY to paths that emit offer-LINKS, never raw times. `sms.ai_sched_message` already got a prompt rule + deterministic guardrail (rejects "set up / have you down / all set / booked you" → safe template, intent!='confirm' only); shipped live 2026-10-05 (sms.py c25522b6).

**Why:** DJ built the whole offer/booking-link system precisely so a slot is reserved the moment it's offered. An AI that free-texts "I've got Oct 9 at 11 open" bypasses that reservation → double-books. It also often implies the job is already scheduled, which it isn't.

**How to apply:**
- Codified in `FLEET_GOVERNANCE.md` §10 (canonical, boot-durable) + role-pack QC lines (Lead/Specialists/Builder-2). CLAUDE.md edit only on DJ's explicit OK.
- **QC gate:** for ANY draft/rewrite/suggest/voice/template path that composes customer text, grep that it cannot emit a raw unreserved date/time — it outputs an offer/booking LINK or an already-booked date only. A path that receives availability data must PROVE it renders LINKS, not times.
- **Recording (open DJ ask, 2026-10-05):** DJ wants a record of everything he and the AI said (voice assistant + inbox rewrite/suggest). `ai_rewrite` logs latency only (no instruction/output). Proposal: one bounded audit log {instruction, partner_id, thread_len, output}, capped ~500 chars, Render PG, short retention, no secrets — being audited/built.

Links: [[feedback_no_inventing_customer_lines_hud_confirm]], [[feedback_root_cause_not_just_instance]], [[project_slot_offers_double_offer]].
