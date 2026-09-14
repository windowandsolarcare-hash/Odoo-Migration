---
name: project_wsc_busy_async_feedback_component
description: "ONE shared async-in-flight-feedback component static/owner/wsc_busy.js (WSCBusy.btn/shimmerRow/removeRow/skeleton) — reuse it, don't reinvent per-screen"
metadata: 
  node_type: memory
  type: project
  originSessionId: fd3d7991-aec7-45dc-97e5-4f403efbe28b
  modified: 2026-09-14T08:45:15.425Z
---

There is ONE shared async-feedback component: **`static/owner/wsc_busy.js`**, exposing `window.WSCBusy` with four primitives. Include it (`<script src="/static/owner/wsc_busy.js"></script>` BEFORE the page's inline `<script>`) and call it — never rebuild per-screen (rule 9 / [[feedback_question_when_big_picture_wrong]]). It self-injects its own CSS once, no deps.

- **`btn(el[, busyLabel])`** → returns `done(ok)`: pulses a button brand-blue while its POST runs, ✓-flash on success then restore, plain restore on fail. For standalone button taps.
- **`shimmerRow(container, text[, {before,append,minMs}])`** → `{el, remove, fail, settle}`: optimistic full-width shimmer placeholder row (shows the name) for LIST INSERTIONS. `settle(cb)` runs cb (the reload) only after ≥minMs(520) so a fast API can't blank it before it paints; the reload should swap-not-blank.
- **`removeRow(el)`** → `{restore}`: optimistic DELETE — fades the row now (`.wscb-removing`), `restore()` on failure.
- **`skeleton(container[, {rows,widths}])`** → `{restore}`: fills a section with shimmering placeholder bars the instant a tap fires, for SECTION/PANEL LOADS (the worst blank pauses). Caller sets real innerHTML when data arrives (smooth swap).

**Why:** DJ (2026-09-14) hit taps that felt like they "didn't register" (flagship: tap a Project → milestones took ~5-6s, screen sat blank). Audit catalogued 19 gaps (`3_Documentation/CHERYL_BUSY_FEEDBACK_SWEEP.md`); Specialists built the component + wired 18 of them (Tiers 1-3): v2_goals openGoal/list, cheryl clients (list+setStage), floatnotes (openNote/list/search/delNote), cheryl tasks (snooze/edit/pin/reassign/reopen — via a local `busyBtn` helper), v2_memory (add/save-reg/log-decision/action-item-done/delete-card/delete-meeting + per-view & Ask skeletons), documents (list+modals). #6 plan-views deferred (cloud-synced + semi-retired).

**How to apply:** any new mutating tap or section load on an owner/cheryl screen → reuse WSCBusy, and PAIR the indicator with a rule-13 fetch timeout (10s reads / 30s heavy). Restyle the look in ONE place (the keyframes/colors in wsc_busy.js) — Design owns it. Optimistic actions MUST reconcile on failure (restore/toggle back).
