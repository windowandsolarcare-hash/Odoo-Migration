---
name: project_inbox_triage_needs_you_card
description: "Proactive inbound-text triage → the persistent multi-action \"Needs You\" HUD card (Patty-moved/cancel case). Two-stage classifier on the inbound path + a 2-sub-status card. Spec = 3_Documentation/INBOUND_TRIAGE_SPEC.md. Build state + the card model."
metadata: 
  node_type: memory
  type: project
  originSessionId: 11d2c5cb-9040-46fe-b04b-20ac84f0828f
  modified: 2026-09-22T16:59:05.375Z
---

**Inbox-triage / "Needs You" card (building 2026-09-22, spec INBOUND_TRIAGE_SPEC.md).** Goal: catch a job-affecting inbound (moved/cancel/reschedule/complaint/urgent) BEFORE the drive (Patty Lindquist texted "moved to N.California" at 6pm, DJ saw it next morning, drove anyway).

## QC-gate-1 finding (verify-first)
A proactive classifier ALREADY runs on the inbound path: `sms_incoming` (sms.py, POST /api/sms/incoming) → on every NON-QUIET inbound calls `_inbox_ai_card` → `_triage_thread` (Haiku classify, sms.py ~1313). A34 dropped only the on-demand DRAFT; it KEPT this classify running on every non-quiet inbound. The per-customer `inbox_ai:<norm>` intent cards are DEAD (superseded by the inbox rollup; `_sync_inbox_card(); return` at ~1329). So Component 1 EXTENDS this classify (adds Stage-A gating), never adds a second one.

## Design (Lead-approved 2026-09-22)
- **needs_reply stays exactly as-is** (non-quiet ⇒ needs_reply, set at sms.py ~1619) — err-toward-true, DECOUPLED from the cost-gated Haiku, so no reply goes dark. Stage-A only gates the Stage-B Haiku (a bonus A34 cost win — today Haiku runs on all chit-chat).
- **Component 1 (TODO — hot path):** in sms_incoming, Stage-A free keyword/pattern scan (mov/relocat/sold/cancel/don't come/reschedul/can't make/not home/no longer/complaint/bare "?") + same/next-day-SO check (reuse `_find_upcoming_job`). Only Stage-A passers OR same/next-day-job inbound run Stage-B (`_triage_thread`); job-affecting intent on a scheduled SO ⇒ `_ny_create` a card. Non-job-affecting ⇒ unchanged.
- **Component 3 (TODO):** same/next-day job-affecting ⇒ PushNotification, de-duped via the card's `pushed` flag.

## Component 2 backend — SHIPPED & LIVE (dormant), commit c40e2071
- Store `wsc.triage.card.<norm>` (sms.py `_NY_PREFIX`). Card = {name,phone,partner_id, so_id/so_name/so_date, same_day/next_day, text, why, intent, confidence, action_type∈cancel|reschedule|none, reply_status, action_status ∈ pending|done|dismissed, created, pushed}.
- Helpers: `_ny_get/_ny_set/_ny_create/_ny_resolve` + `_ny_open` (card_status DERIVED: OPEN while any APPLICABLE sub pending — the action sub applies ONLY when action_type∈cancel/reschedule, so a reply-only card clears on the reply alone). `_ny_create` is idempotent per thread (refresh content, PRESERVE resolved subs). intent→action_type via `_NY_ACTION_FOR`.
- `POST /api/triage/resolve {c|norm, sub∈reply|action|card, disp∈done|dismissed}` — records STATUS ONLY (never sends/cancels/reschedules); idempotent (missing card ⇒ ok/gone).
- `feed_live._needs_you_cards` live producer: emits while `_ny_open`, carries a `needs_you` block {norm, reply_status, action_status, action_type, so_id, intent} for the FE. Per-thread id `needs_you:<norm>` (auto-owned). DORMANT — no cards until Component 1 populates.

## TODO (next focused unit)
Component 1 (classifier hot-path hook) + the **v2_hud.html front-end**: render the `needs_you` block as TWO buttons ([Reply]→editable draft→inbox_ai/approve; [Cancel job]/[Reschedule] per action_type→inbox_ai/cancel|reschedule), each flips to ✓ IN PLACE, card stays until BOTH resolved (survives refresh — server-persisted); a per-sub skip + whole-card Dismiss → /api/triage/resolve. + Component 3 push. NOTHING auto-fires (every send/cancel/reschedule = DJ's press). Phone edge cases (double-tap guard, timeouts, idempotent). Lead's 6 QC gates. sms.py PG flag-gate stays untouched. See [[project_hud_live_derived_flip]], [[feedback_hud_cards_live_not_inbox]], [[feedback_reuse_canonical_endpoint]].
