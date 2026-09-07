---
name: project_phase2_workspace_verified
description: "Phase-2 workspace (WSC-WORKSPACE-PHASE-2-PLAN.md) is LIVE. Specialists pieces: #1 authorship (authz.session_actor keys off session partner p, switcher retired), #2 links layer (goals.py wsc.goals.links), #3 goals dependencies (next_slots after= + _critical_path), #5 card-first comms (ideas.html Board is now the default surface, flat chat demoted to 'General/history'), #6 card→goal links (promoted-only). #4 Gantt/board = Cheryl's cloud (view contract /cheryl/api/view/plan + /api/goals/critical)."
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-07T08:10:38.022Z
---

**DJ-approved 2026-09-07 (WSC-WORKSPACE-PHASE-2-PLAN.md). Extend Goals + Ideas + a links layer — NO rebuilds, no canvas, no second store.** Most of the Specialists backend was already built in an earlier same-session pass; when Lead relayed "build it" (from compaction-truncated context), I VERIFIED live instead of duplicating (Rule 9) — pieces 1/2/3/6 were already live + spec-matching; only #5 needed a surgical delta.

**Specialists pieces (all LIVE):**
- **#1 Authorship** — `authz.session_actor(request)` returns 'dan'|'cheryl'|None from the SESSION token's partner id `p` (+ role `r`; p==23243 or r=='cheryl' → cheryl), NEVER the request body. Wired into ideas.py add/promote/`card_msg`. Frontend switcher RETIRED (library.html `switchMe()` no-op + reads `/api/ideas/me`; v2_apps.js byline read-only). Old messages keep their names. See [[project_author_identity_session]] if present.
- **#2 Links layer** — goals.py `_LINKS_KEY='wsc.goals.links'` ir.config_parameter blob (`_load_links`/`_save_links`, same pattern as feed/decision-log) + `GET /api/goals/links`, `POST /api/goals/link`, `POST /api/goals/link_delete` (kinds blocks|part_of|about|realises).
- **#3 Dependencies** — `next_slots(after=…)` resolves a predecessor TASK-ID → its date_deadline+1 (capacity-aware, reads real sale.order jobs); `_critical_path` (Kahn topo, cycle-safe, longest-duration, in-memory capacity scheduling) at `GET /api/goals/critical`; feeds `GET /api/view/plan`.
- **#5 Card-first comms** — ideas.html now DEFAULTS to the **Board** (cards) view, not the flat chat (`_view='board'`; Board tab is primary/leftmost). The prominent compose is New-Idea (a card) + per-card sub-threads (`#cd-input` → `/api/ideas/card_msg`, session author) + the Ideas HUD lane (`_sync_one_card_feed`/`build_ideas_cards` push into the canonical feed source='ideas'). The old flat group chat is NOT deleted — demoted to a low-prominence **"💬 General"** tab with a "🗄️ Earlier & general chat — new thoughts go on the Board" hint; it's the ONE low-prominence "general" path so a not-about-anything message doesn't force a fake card. Outcome: a new message is about something by default; flat chat = readable archive.
- **#6 Card→goal earned structure** — `POST /api/ideas/card_link` enforces PROMOTED-ONLY (non-promoted card → "not a promoted card (only a card can carry a link)"), kinds about|part_of|realises, dedup; `promote()` can pass goal_id → part_of link. Decay stays the filter (raw/un-promoted can't link).

**#4 Gantt + board views = Cheryl's cloud** (piece 4), rendered at [[project_cheryl_plan_views_sync]] (`/cheryl/plan`). The view contract it consumes is already serving: `/cheryl/api/view/plan` + `/api/goals/critical`.

**Files:** authz.py, goals.py, ideas.py (Specialists-exclusive), static/owner/ideas.html + library.html + v2_apps.js. All additive; DJ's HUD regression-safe. `progress` reads/writes `x_manual_progress` (native project.task.progress recomputes off hours — see [[project_job_type_autoderive]] discipline / behavioral verification).
