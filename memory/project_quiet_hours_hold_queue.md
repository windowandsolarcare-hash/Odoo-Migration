---
name: project_quiet_hours_hold_queue
description: "★ STANDING COMMS RULE (DJ 2026-08-02): NO customer text sends 8pm–8am PT. Not a block — a HOLD queue that auto-releases at 8am. Override = force_now per-send + a global pause toggle. messaging.py."
metadata: 
  node_type: memory
  type: project
  originSessionId: 1e80ea0d-78f5-4aa2-bc1d-25aace876ab5
  modified: 2026-08-03T07:18:58.626Z
---

**DJ, 2026-08-02: every customer text is held during night hours and released in the morning.**
- **Quiet window = after 8:00 PM and before 8:00 AM Pacific.** messaging.py already has `QUIET_START_HOUR=8` / `QUIET_END_HOUR` — set END to **20** (was 21/9pm).
- **HOLD, don't block, don't send.** Default flips: `messaging.send` today defaults `ignore_quiet=True` (off) and merely blocks when on. New behavior: during quiet hours, **queue the full send args** (to/body/partner_id/so_id/kind/idem/queued_at) to a hold param (e.g. `wsc.msg.holdqueue`) and return `{'ok':True,'held':True}`. Applies to EVERYTHING (reminders, reactivation, booking confirms, inbox-assistant, DJ-approved sends) — quiet applies unless explicitly overridden.
- **Release:** a scheduler tick (reuse `reminders_tick`) drains the queue when it's NOT quiet hours → sends each (force_now); dedupe by idem (`already_sent`) so no double-send. So DJ approving things at 2am → they all go out at 8:00 AM.
- **Override (2 ways):** (a) per-send `force_now=True` so a text DJ deliberately fires at night goes now (confirm "after hours — send now?"); (b) global pause toggle `wsc.msg.quiet_pause` DJ flips to text freely, auto-resets at the next quiet-window start (can't be left on forever).
- STOP / Do-Not-Contact / idempotency still evaluated FIRST (unchanged). Rationale: compliance (don't text customers overnight) + DJ preference to work at night without waking customers.
- Ownership: messaging.py (specialist). Spec'd via AGENT_MAIL 2026-08-02. Ties into [[project_reminder_texts_build]] (messaging.send = the ONE send fn) + [[project_inbox_assistant]].

**✅ BUILT + VERIFIED LIVE 2026-08-03 (specialist).** messaging.py: `QUIET_END_HOUR` 21→20; `_hold`/`_hold_queue` (param `wsc.msg.holdqueue`, cap 500, deduped by idem); `send()` gained **`force_now`** and now holds by default (guard order: empty/bad#/already_sent/opted_out/DNC FIRST, then `if not force_now and not quiet_paused() and in_quiet_hours(): _hold(...)`). `ignore_quiet` param kept in signature but NO LONGER bypasses (deprecated). `quiet_paused()`/`set_quiet_pause` (param `wsc.msg.quiet_pause` = `{until:<next 8pm PT>}`, auto-expires via `_next_window_start`). `release_holds()` = no-op during quiet, else replays each via `send(force_now=True)`, requeues twilio_failed; **wired into `reminders_tick()`** (one line) so 8am drains it. Endpoints: `GET /api/messaging/quiet_status`, `POST /api/messaging/quiet_pause`, `POST /api/messaging/release_holds` (all CRON_SECRET-guarded except status). **Manual `/api/inbox/send` bypasses entirely** (uses `_send_sms` directly, never messaging.send) — DJ's deliberate taps always send now. 8-point live test during quiet hours all passed. See [[project_inbox_assistant_p1]].

## Holding-screen management endpoints (2026-08-04, messaging.py)
DJ wanted a screen to see/manage the queue (lead building `v2_holding.html`; I own the endpoints):
- **GET `/api/messaging/holds`** → `{ok, held, paused, quiet_now, items:[{key, idem, to, name, body, queued_at, so_id, partner_id, kind, sends_at}]}`. Name resolved from partner_id (else phone).
- **POST `/api/messaging/hold_send_now` {key}** → sends that one now (`send(..., force_now=True)`), removes from queue; re-queues on transient fail.
- **POST `/api/messaging/hold_cancel` {key}** → removes, never sends → `{ok, held}`.
- **POST `/api/messaging/hold_edit` {key, body}** → changes the body before release.
- **`key`** = per-item handle from the list = `idem` when the held send has one, else synthetic `to|queued_at` (`_hold_key`). Mutations accept `key` OR `idem`. Real held items often have NO idem (e.g. the reschedule confirm), which is why the synthetic key exists.
- Per-item endpoints are OPEN (no token), like the followups owner actions. Send-all + pause still reuse `/release_holds` + `/quiet_pause` (token=CRON_SECRET) + `/quiet_status` (open).

## HUD "holding" card (2026-08-04, messaging.py)
`_sync_hold_card()` keeps ONE feed card `holding:queue` (source 'holding', kind attention, badge=count, title "🌙 N text(s) holding for morning", action→/static/owner/v2_holding.html) in sync — called after EVERY queue change (`_hold`, `release_holds`, `hold_send_now`, `hold_cancel`, `hold_edit`); deletes the card when the queue empties. NOTE: `submit_item` returns `{ok:False,errors}` (does NOT raise) so validation issues fail silently — card fields must satisfy feed.validate_item (urgency ∈ interrupt/today/glance). Lead built v2_holding.html + launcher tile.
