---
name: project_hud_optimistic_approve
description: HUD Approve (v2_hud.html doApprove) is now OPTIMISTIC — clears the card instantly and runs the (30s+) work in the background; restores the card only on a definitive failure. Feed refresh is the safety net.
metadata: 
  node_type: memory
  type: project
  originSessionId: 0e6fb90e-8d05-4272-91a3-ed7ee21488d7
  modified: 2026-08-13T22:41:06.752Z
---

**DJ (2026-08-13):** a paywatch Approve took 30s+ (the full invoice→post→pay→Done→next-job cascade against Odoo cloud — ~30 sequential RPCs, several heavy). DJ: "clear it right away."

**Fix (v2_hud.html, commit 4c041ea):** `doApprove` is now optimistic —
1. `removeCard(id)` + toast **"✅ Approved — finishing up…"** the instant DJ taps (no more watching a 30s spinner).
2. The on_approve POST runs in a background IIFE (still 45s timeout).
3. **Restore only on a DEFINITIVE failure:** `d.ok===false` → `_restoreCard(row)` + "tap Approve again". On `null`/network-error it re-checks `_cardCleared(id)` (feed no longer has the card = it went through, idempotent) — restores only if the card is STILL present server-side.
- New helper `_restoreCard(row)`: pushes the row back into ITEMS + `_byId`, resets `_busy`, re-renders.
- Safety net: these approve endpoints delete their own card on success and are idempotent, and the HUD re-reads `/api/feed/list` on refresh — so if a background op silently failed, the card reappears on next load anyway.

Applies to ALL approval cards, not just paywatch. NOTE: v2_hud.html is the lead's HUD-redesign file (live-projection) — this is a client-UX change to the existing store-backed HUD; flagged to lead. The 30s itself is inherent to the Odoo cascade (not the disabled Workiz sync — that returns instantly). A future option = server backgrounds the closeout tail (Done+snapshot+next-job) after the payment records. Related: [[project_hud_approve_false_failure_slow_op]] (the earlier null≠fail fix this builds on), [[project_paywatch_auto_tip]].
