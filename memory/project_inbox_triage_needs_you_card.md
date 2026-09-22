---
name: project_inbox_triage_needs_you_card
description: "Proactive inbound-text triage → the persistent multi-action \"Needs You\" HUD card (Patty-moved/cancel case). Two-stage classifier on the inbound path + a 2-sub-status card. Spec = 3_Documentation/INBOUND_TRIAGE_SPEC.md. Build state + the card model."
metadata: 
  node_type: memory
  type: project
  originSessionId: 11d2c5cb-9040-46fe-b04b-20ac84f0828f
  modified: 2026-09-22T18:35:02.442Z
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

## Component 1 + 3 — BUILT (compiles), held UNPUSHED (coupling) — in local /c/Users/dj/sms_live.py
Written + py_compile-clean, NOT pushed because C1 (card creation) must ship WITH the FE or cards get STUCK (only the FE's /api/triage/resolve buttons clear a card; nothing else calls _ny_resolve). Server stays safe at C2-dormant until C1+FE+C3 land together.
- In `sms.py`, added before `_inbox_ai_card`: `_STAGE_A_KW`, `_NY_WHY`, `_job_affecting_signal(body)` (keyword hit OR bare '?'), `_job_same_or_next_day(job)` (PT date vs today/tomorrow), `_ny_classify(tri, body, has_job)` (maps _triage_thread respond|schedule|reschedule|cancel + Stage-A keywords → moved|cancel|reschedule|complaint|urgent_question|None), `_ny_push(card)` (Component 3: _notify + set card.pushed, de-duped).
- `_inbox_ai_card` restructured: `_triage_thread` (Stage B Haiku) now runs ONLY when `_job_affecting_signal(body) or same/next-day job` (Stage-A gate — the A34 cost win); on a job-affecting intent + a scheduled job → `_ny_create(...)` + (same/next-day) `_ny_push`. needs_reply untouched (set upstream). `_sync_inbox_card()` still always runs.

## TODO (next focused unit) — the FE (Component 2), then push C1+FE+C3 TOGETHER
FE = `static/owner/v2_hud.html` `card(row)` (line ~285): add a branch for `it.needs_you` (the block feed_live._needs_you_cards emits). Render up to TWO buttons — [Reply] (always) + [Cancel job]/[Reschedule] (per action_type) — each showing pending or ✓-in-place from needs_you.reply_status/action_status; card stays until BOTH resolved (the live producer omits once _ny_open false) or a whole-card Dismiss. Reply → editable generated reply (fetch on-demand, A34) → Send = inbox_ai/approve (sms.py:2241) → then /api/triage/resolve {sub:reply,disp:done}. Action → confirm → inbox_ai/cancel (2452) / inbox_ai/reschedule (2415) → /api/triage/resolve {sub:action,disp:done}. Per-sub skip + whole-card Dismiss → /api/triage/resolve {sub:card}. Double-tap guards + fetch timeouts (CLAUDE #13). NOTHING auto-fires. Then push sms.py + v2_hud.html together → Lead's 6 gates.
Resume-note: my built C1+C3 lives in /c/Users/dj/sms_live.py (fetched at sms.py 3102 lines + edits); re-fetch live sms.py first per push-gate, re-apply if needed.
Component 1 (classifier hot-path hook) + the **v2_hud.html front-end**: render the `needs_you` block as TWO buttons ([Reply]→editable draft→inbox_ai/approve; [Cancel job]/[Reschedule] per action_type→inbox_ai/cancel|reschedule), each flips to ✓ IN PLACE, card stays until BOTH resolved (survives refresh — server-persisted); a per-sub skip + whole-card Dismiss → /api/triage/resolve. + Component 3 push. NOTHING auto-fires (every send/cancel/reschedule = DJ's press). Phone edge cases (double-tap guard, timeouts, idempotent). Lead's 6 QC gates. sms.py PG flag-gate stays untouched. See [[project_hud_live_derived_flip]], [[feedback_hud_cards_live_not_inbox]], [[feedback_reuse_canonical_endpoint]].
