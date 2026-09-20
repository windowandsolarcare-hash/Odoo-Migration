---
name: project_modal_inline_display_defeats_hide_class
description: "A modal/sheet toggled by the `.hide` class but carrying an INLINE display (display:flex/block) is broken — inline beats the class, so `.hide{display:none}` (no !important) never applies → the panel can't hide / can't be dismissed. Drive visibility by ONE mechanism."
metadata: 
  node_type: memory
  type: project
  originSessionId: 11d2c5cb-9040-46fe-b04b-20ac84f0828f
  modified: 2026-09-20T06:37:10.050Z
---

**Bug class (A42, 2026-09-19):** an owner-screen modal/bottom-sheet whose show/hide is toggled via the `.hide` CSS class (`el.classList.add('hide')`) but which ALSO has an **inline `display:flex`/`display:block`** in its markup is BROKEN. **Inline styles beat a CSS class**, and these files define `.hide{display:none}` WITHOUT `!important` — so `.hide` can never override the inline `display`. Result: the element is effectively always visible, the ✕/backdrop-tap (which only add the class) do nothing, and it can overlay/trap the screen.

**Confirmed instances:**
- `static/owner/v2_vault.html` `#shmodal` (the "Document" viewer) — **was stuck + undismissable, overlaying Shortcuts** (DJ hit it live, board A42). Fixed in commit a01c70b7: initial inline `display:none`; `openShared` → `m.style.display='flex'`; `closeShared` → `m.style.display='none'` (single mechanism).
- `static/owner/v2_field.html` `#ack-pill` (line ~583, class="hide" + inline `display:flex`; toggled in `_job_detail_panel.js::loadAckState`). LESS severe — `loadAckState` sets `pill.style.display` on every branch so it's not stuck — but the mismatch can **flash the green "✓ Acknowledged" pill on job-open** before the async `/owner/api/maint/state` resolves. Trivial fix = change that element's inline `display:flex` → `display:none` (the show path already sets `display='flex'` unconditionally). (Flagged to Lead 2026-09-19; sibling `#mark-ack-btn` is SAFE — class="hide" with NO inline display, so `.hide` works.)

**Why:** CSS specificity/cascade — an inline style (specificity 1000) always beats a class rule (10), and an id rule (100) beats a class too; only `!important` on the class (or an id+class selector like `#x.hide`) can override inline. A "hide utility" that a caller defeats with inline `display` is a latent trap.

**How to apply:**
1. When adding OR reviewing any modal/sheet/toast, ensure visibility is driven by **ONE** mechanism — either `style.display` toggling (preferred, self-contained) OR the `.hide` class, **never both**. If the element needs `display:flex` when shown, set that in JS on show (`el.style.display='flex'`) and start it `display:none`; do NOT bake `display:flex` into the markup while toggling a class.
2. Grep to find the trap: `class="[^"]*hide[^"]*"[^>]*style="[^"]*display:(flex|block|grid)` (and the style-then-class inverse) across `static/owner/*.html`.
3. Scoped fix beats a shared-class change: switch that element to `style.display` toggling rather than adding `!important` to the shared `.hide` (avoids touching every other `.hide` user). Related: [[feedback_removing_element_leaves_dangling_ref]], [[project_clockin_bar_customer_overlay]].
