---
name: project_messaging_idempotency_cas
description: "messaging.send() SMS idempotency is now an ATOMIC Render-PG claim-before-fire ledger (wsc_msg_sent, UNIQUE idem PK) — replaced the RMW JSON-blob (wsc.msg.sent in ir.config_parameter) that had a check-then-act double-send race. Covers the claim/confirm/release flow, at-most-once-on-crash semantics, PG-down fallback, and the stuck-claimed HUD visibility."
metadata:
  node_type: memory
  type: project
  originSessionId: 7f93eb62-ab56-4528-a75a-3a6b108e7612
  modified: 2026-09-28T03:29:14.349Z
---

**Shipped 2026-09-27 (Specialists, Lead QC-hard green). CAS #3 of the messaging-clarity cluster.** File: `routers/owner/messaging.py`.

## The bug it fixed
The old idempotency ledger was a JSON dict `wsc.msg.sent` in Odoo `ir.config_parameter` (`_sent_ledger`/`_mark_sent`): a READ at send-start (`already_sent`) then a read-modify-write MARK after a successful fire. That's **check-then-act, not atomic** — a concurrent double-tap / two tabs / **numInstances=2** could both pass the check and both fire = a double-text (DJ's exact fear). The RMW blob write was also lossy (last-writer-wins could drop a mark). Per [[feedback_data_location_odoo_vs_postgres]] this high-write operational ledger belongs in Render PG, not Odoo.

## The fix — atomic PG claim-before-fire
Authoritative ledger = Render-PG table **`wsc_msg_sent (idem text PRIMARY KEY, kind, to_norm, sid, status, created_at)`** (short-lived autocommit psycopg conns via a local `_pg()`; once-per-process `_ensure_ledger(cur)` guarded by module flag `_ledger_ready`). In `send()`, AFTER all guards + the quiet-hold RETURN (a held msg must NOT claim), right before the Twilio fire:
- **`_claim_send(idem, kind, norm)`** = `INSERT ... ON CONFLICT (idem) DO NOTHING RETURNING idem`; `fetchone() is not None` ⇒ we won the claim (proceed). Conflict ⇒ already claimed/sent ⇒ return `{'ok':False,'reason':'already_sent'}`, DON'T fire. The UNIQUE PK serializes concurrent callers on the index — race-proof by construction across tabs + instances.
- success ⇒ **`_confirm_sent(idem, sid)`** (UPDATE status='sent', sid). failure ⇒ **`_release_claim(idem)`** (DELETE only a `status='claimed'` row, never a 'sent' one) so a legit retry can go (retry-on-failure preserved).

## Semantics (deliberate)
- **At-most-once on crash:** a crash between claim and confirm leaves the row `'claimed'` ⇒ that idem stays blocked ⇒ a SILENT MISS, never a double-text. This is STRICTLY SAFER than the old mark-after-success (crash between fire and mark ⇒ unmarked ⇒ could re-send = double). For customer SMS, at-most-once > at-least-once = DJ's priority (never double). Lead endorsed.
- **PG-DOWN degrade:** `_claim_send` on any PG error falls back to a legacy blob CHECK (return `not already_sent`; the mark happens in `_confirm_sent` via `_mark_sent_legacy`) ⇒ comms never blocked, retry-on-failure preserved. `already_sent` reads PG then falls back to the old blob ⇒ catches pre-cutover idems (no double-send at cutover). `_sent_ledger`/`_mark_sent_legacy` kept as the read/write fallback ONLY.

## Stuck-claimed visibility (the at-most-once safety net)
`messaging.stuck_claimed(minutes=15)` (read-only) returns `{count, oldest_min}` of `status='claimed'` rows older than N min with no sid. A `feed_live._msg_stuck_claimed` HUD producer surfaces one card "⚠️ N texts may not have sent" (links to v2_inbox) so a crash-caused silent miss is DETECTABLE + DJ can MANUALLY re-send. **Never auto-retried** (auto-retry reintroduces double-send risk).

Related: [[feedback_data_location_odoo_vs_postgres]], [[feedback_hud_cards_live_not_inbox]], [[project_fleet_ship_system]].
