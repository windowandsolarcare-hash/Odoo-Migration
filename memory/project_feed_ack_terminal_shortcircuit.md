---
name: project_feed_ack_terminal_shortcircuit
description: "The recurring HUD 'errored but actually worked' bug (red 'Couldn't mark done' though the server succeeded) + intermittent instance health-restarts = POST /owner/api/feed/ack re-ran ALL ~18 live producers FRESH-vs-Odoo (uncached) on a terminal ack, blowing the client 12s timeout. Fixed 2026-09-28 by short-circuiting terminal acks past the scan. Covers the feed.py ack/merge/SWR-cache architecture."
metadata:
  node_type: memory
  type: project
  originSessionId: 7f93eb62-ab56-4528-a75a-3a6b108e7612
  modified: 2026-09-28T15:11:49.879Z
---

**Fixed 2026-09-28 (Specialists, Lead QC-hard green). File: `routers/owner/feed.py` + `static/owner/v2_hud.html`.** DJ's recurring red "Couldn't mark done — try again" on HUD cards that HAD actually been marked done server-side (Render logged /feed/ack→200), plus intermittent instance auto-restarts blamed on "overload" (CPU was idle).

## Root cause — the ack path had NO SWR cache
The SWR cache lives ONLY on the LIST path (`_assemble_live` / `_assemble_live_build` @ feed.py ~554-676, writes `_LIVE_CACHE`). The ACK path (`POST /api/feed/ack`, `api_feed_ack`) had a branch: when a LIVE-DERIVED card has no stored entry yet, it called `feed_live.live_cards()` — running ALL ~18 Lane-A producers FRESH against Odoo, UNCACHED — just to synthesize a status holder. On a terminal op (✓done / dismiss / decline) under Odoo latency that blew the client's 12s timeout (v2_hud `doDone`/`doDecline`, `jfetch` 12s default) → client ABORTS → red false-fail, though the server persisted status='done'. The same heavy synchronous scan bogged an instance → `/healthz` 5s timeout → auto-restart (the phantom "overload"). Hit EVERY live-derived HUD card's terminal op, intermittently.

## The fix — short-circuit TERMINAL acks past the scan
In `api_feed_ack`, when there's no stored entry: if `op in _TERMINAL` (`('approved','declined','done')`) → persist a MINIMAL status holder (`{'item':{'id':iid}, 'status':'new', ...}`) by id and skip `live_cards()` entirely. **Why safe (proven):** `_merge_live_card(card, stored, ...)` reads ONLY `stored['status']` + `snooze_until` — ALL displayed content comes from the FRESH live card each build — and `list_items()` DROPS terminal cards in EVERY view, so a terminal card's stored `item` is never read. After-state holds two ways: fast ack → client `removeCard(id)` immediately; AND `_save` busts the live cache → next `live_list` re-derives → `_merge_live_card` sees stored 'done' → returns None → suppressed persistently.
- ★ **SNOOZE is EXCLUDED from the short-circuit** (Lead caught this): the `include_snoozed=1` view DOES render a snoozed card's content, so its item IS needed → snooze stays on the content-preserving `live_cards()` fetch. Short-circuiting it would show a contentless snoozed card. Only truly-terminal ops (dropped in every view) are content-never-needed. seen/unsnooze also keep the fetch (not the timeout-prone path).
- **Belt:** v2_hud terminal ack timeouts 12s→30s (done/declined/snooze/unsnooze) to match approve's window — covers snooze's timeout on the scan path it stayed on.
- Accepted trade-off: the short-circuit skips the 404-unknown-id check on terminal ops → a bogus terminal id makes a harmless orphan status row (dropped from base, never rendered; real ids only come from cards the user acted on).

## Rule for the future
Never run the full `live_cards()` producer scan on a WRITE/terminal path — it belongs to the LIST path (which is SWR-cached). If an ack must return a derived view, reuse the existing `_assemble_live` cache, never a fresh scan. On this stack a client abort ≠ server failure: /feed/ack→200 in Render logs means it WORKED even when the HUD showed an error.

Related: [[feedback_hud_cards_live_not_inbox]], [[project_fleet_ship_system]].
