---
name: project_field_detail_collapse
description: "Field assistant — when a job detail panel is open on phone, the schedule collapses to ONLY the selected customer row so the panel is larger. Selection gotchas."
metadata: 
  node_type: memory
  type: project
  originSessionId: 52666f46-c84b-4f55-ad04-3ed2f2d38410
---

2026-06-07: DJ wanted the field assistant detail panel (`#active-panel`) larger, showing only the open customer as a single row above it. Implemented in `static/owner/field.html`:

- **CSS (phone only, `@media (max-width:599px)`):** when `body.panel-open`, hide every direct child of `#schedule-section` except the selected job row, and set `#active-panel { max-height: 80vh }` (was 62vh). Selector: `body.panel-open #schedule-section > *:not(.job-row){display:none}` + `> .job-row:not(.selected){display:none}`. (Desktop split-view / resize is untouched — resize is desktop-only, ≥600px.)

**Two non-obvious gotchas (both fixed — don't reintroduce):**
1. **Future-job rows weren't `.selected`.** Only the today-loop row template computed `sel` from `activeJob`; future-day rows didn't. Opening a future job (e.g. Steve, a Mon job) selected nothing → collapse hid everything → empty black void. Fix: every row now carries `data-soid="${j.so_id}"` and `openJob` selects by `String(r.dataset.soid)===String(job.so_id)` across ALL `.job-row`s.
2. **Re-render dropped the highlight on first open.** On fresh entry the schedule renders from cache, you open a job, then ~1s later the fresh fetch re-renders `renderSchedule` (`sec.innerHTML = html`). The today template re-applies `sel`, but future rows don't → first-opened future job's row blanked after ~1s (subsequent opens fine, no more re-render). Fix: at the END of `renderSchedule`, re-apply selection to `activeJob` across all rows by `data-soid`.

**Why:** any future edit to the schedule row templates or `renderSchedule` that rebuilds rows must preserve `data-soid` and keep the post-render re-apply, or the collapse view blanks out for the open job. The today-loop `sel` var alone is NOT enough — it misses future rows.

**How to apply:** When touching field.html schedule rendering, keep `data-soid` on both row templates and the post-`innerHTML` selection re-apply. Related: [[feedback_removing_element_leaves_dangling_ref]], [[feedback_field_html_js_syntax_check]].
