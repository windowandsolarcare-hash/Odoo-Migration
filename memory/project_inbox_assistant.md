---
name: project_inbox_assistant
description: "★ NEXT PROJECT (DJ 2026-08-02): Inbox triage assistant — Claude reads each incoming text, classifies into 4 intents (respond/schedule/reschedule/cancel), proposes ONE action card to the HUD (approve/edit/reject), Odoo-native. Replaces the parked Workiz field assistant. Spec in repo."
metadata: 
  node_type: memory
  type: project
  originSessionId: 1e80ea0d-78f5-4aa2-bc1d-25aace876ab5
  modified: 2026-08-03T10:03:27.750Z
---

**DJ's capstone project (2026-08-02): the Inbox Assistant.** Full spec + build plan = **`3_Documentation/INBOX_ASSISTANT_SPEC.md`** in the saunders-render-app repo (link: github.com/windowandsolarcare-hash/saunders-render-app/blob/main/3_Documentation/INBOX_ASSISTANT_SPEC.md).

## The vision
A text hits the inbox → Claude reads the WHOLE thread → does exactly ONE of four things: (1) **Respond** (answer with REAL looked-up data — pricing, next open days, "we take Zelle" — never invent a price/date), (2) **Schedule**, (3) **Reschedule/edit**, (4) **Cancel/delete**. In the beginning it does NOT act — it posts ONE "here's what I'll do" **approval card to the HUD**; DJ **Approves** (sends/acts), **Edits**, or **Rejects** → gets 3 numbered options. Approval-gated now, **auto per-intent later**. This REPLACES the parked Workiz-era field assistant ([[project_workiz_retirement]]) — DJ never used the chat one; this passive inbox triage is the useful shape. Base prompt = field.py SYSTEM_PROMPT (the detailed 192-line one, > dashboard.py's 111-line twin) — keep the Odoo data model/relationships/multi-company/date rules, CUT all Workiz scheduling, ADD the 4-intent brain.

## DJ's locked decisions (2026-08-02)
1. **Every** incoming text is triaged/carded in the beginning (keeps DJ in the loop). "Thanks"/no-response → card says **"No response needed" + Done button** (don't draft). Auto-Done later.
2. Availability = reuse the EXISTING scheduler (so-suggest/day-plan); **show 3** options.
3. Model: Haiku classify+draft, escalate to the big model only on hard threads.

## Reuse map — every action is already Odoo-native (built the Workiz-retirement weekend)
- Respond: `_draft_reply` (sms.py, thread-aware, no invented facts) + `/api/ai/rewrite`; send via `messaging.send` (ONLY outbound path).
- Schedule: `book_fresh_odoo_job(partner_id, when, job_type, service)` (new_job.py). Reschedule: `schedule_odoo_so(so_id, dt_pt, set_status=True)` (scheduler.py). Cancel (the twin, NO delete): **`cancel_job(so_id, reason='')`** (scheduler.py, LIVE 2026-08-03) — status Canceled + action_cancel(state→cancel) + chatter, keeps record. Hard delete only if asked: `/api/delete_job`. Mark-done: `set_block_status`.
- **thread_tail RENDERS on the HUD** (v2_hud.html `tailHtml`, LIVE 2026-08-03): every inbox_ai approval card shows the last ~3 msgs as chat bubbles above the draft. sms.py `_thread_tail`/`_inbox_ai_card` already supply `thread_tail` — reschedule/cancel cards get it free.
- Data: pricing → quote config `_get_quote_config` (dashboard.py); availability → `/api/scheduler/so-suggest`; payments = Zelle/cash/check/card (static).
- Entry point: sms.py inbound (already guards STOP/START/robocall-IVR/lead-service before triage).

## Build phases + ownership
P1 Respond-only, approval-gated (assigned to the SPECIALIST — sms.py triage + inbox card + drafter; lead supplies action/data hooks). P2 Schedule. P3 Reschedule+Cancel. P4 per-intent auto-graduation. Spans sms.py (specialist) + new_job/scheduler action fns (lead) + HUD feed. Phase-1 assigned via AGENT_MAIL 2026-08-02.
