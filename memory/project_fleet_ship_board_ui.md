---
name: project_fleet_ship_board_ui
description: "Fleet Ship System S2 dashboard = static/owner/v2_ship_board.html (DJ's deploy-control board on GET /owner/api/ship/board). Flagged cards dedup rule: a false-done must never show under 'Recently live'."
metadata: 
  node_type: memory
  type: project
  originSessionId: 93ae5c9a-b2db-49a9-8fa8-84d13000c2ae
  modified: 2026-09-28T00:40:41.559Z
---

**What (shipped 2026-09-27, commit 6786fdc7):** `static/owner/v2_ship_board.html` — DJ's deploy-control tower, the productized version of the stage-and-trigger "ready board" ([[feedback_dj_deploy_control_stage_and_trigger]]). Reachable via the 🚀 launcher entry "Ship Board" in `v2_apps.js`. Owner: **Builder-2** owns the UI; **Specialists** owns the API (`routers/owner/ship.py`).

**Data source:** `GET /owner/api/ship/board` (owner-gated cookie; the static page itself is public, the DATA is gated — standard pattern). Per card: `{id,title,state,stored_state,owner_role,branch,branch_live,root_cause_ref,dj_confirmed,dep_on,shipped_at,flags[],created_at,state_changed_at}` + top-level `{ok,cards,as_of}`. `state` is git-derived (Shipped WINS over stored via a `card-<id>`/`ships #<id>` commit on main); middle states (Building/QC/Ready) are stored. `?refresh=1` forces a fresh git read (else server SWR ~60s).

**UI shape (DJ-priority vertical sections, NOT a literal kanban — it's a phone):** ⚠️ Needs-attention (flags) → 🟢 Ready to deploy → 🔨 In progress (Building+QC) → 💡 Captured (fold) → ✅ Recently live (fold). Client SWR (instant last-known from localStorage → bg refresh), 12s fetch timeout, 401/403→"sign in" banner, catch keeps cached view, Pacific 12h times, `overscroll-behavior-y:none` (no pull-to-refresh, [[feedback_disable_pull_to_refresh]]). Lead blessed the action-first ordering over strict pipeline order.

**★ Non-obvious design rule — FLAGGED-CARD DEDUP:** a card with any `flags[]` renders ONLY under "Needs attention," and is EXCLUDED from its normal state section. **Why:** the self-check flag `claimed_shipped_no_commit` sets `state='Shipped'` (stored wins when no git commit) — so without dedup a **false-done** card would appear under "✅ Recently live" as if it actually shipped, which is exactly the lie the flag exists to catch. Dedup also de-clutters (a flagged Building card isn't shown twice). Flags surfaced as red per-card banners with plain-English meaning (`building_no_branch`, `claimed_shipped_no_commit`). Caught in a mock-data render pass before ship — see [[feedback_render_design_before_presenting]] (look at a new UI before calling it done).

**Contract stability:** S3 (aging timer + latch-shipped-persist + outage flags + orphan sweep) adds a `git_ok` signal to `_git_signals` but does NOT change the `/board` card fields — the UI stays valid. Unknown future flag values fall back to their raw string (`FLAG_TEXT[f]||f`); add friendly text when S3's new flag names land. It **dogfoods** — the system's own card (`shipsys`, "Build the Fleet Ship System") is on the board.

**How to apply:** touching the board UI → keep the flagged-dedup rule (never let a flagged/false-done card into the normal flow); card WRITES are headless NOTIFY_SECRET (`/card`, `/card/state`) — the board is READ/display only. Ties to [[feedback_hud_cards_live_not_inbox]] (live-derived, not a stored inbox).
