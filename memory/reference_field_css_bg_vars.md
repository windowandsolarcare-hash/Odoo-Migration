---
name: reference_field_css_bg_vars
description: "field.html CSS trap: --card-bg is TRANSLUCENT (rgba white 3%), --bg-card is OPAQUE. Use --bg-card for modal/sheet backgrounds or content bleeds through."
metadata:
  node_type: memory
  type: reference
  originSessionId: 6f63b0d4-dd6a-4dd1-aac3-e533a99e7526
---

**field.html (and other owner screens sharing the theme) have TWO near-identical CSS vars that are easy to confuse:**
- `--card-bg` = **`rgba(255,255,255,0.03)`** — a TRANSLUCENT 3%-white overlay tint (for subtle raised surfaces ON an already-opaque parent).
- `--bg-card` = **`#1e293b`** (dark) / `#f1f5f9` (light) — a SOLID/OPAQUE card color.

★ **For any full-screen modal / bottom-sheet background, use `--bg-card` (opaque), NOT `--card-bg`** — otherwise the page content behind the sheet bleeds through even when the overlay backdrop dims it. Bit us 2026-07-09: the "Log a touch" sheet (`.out-sheet`) used `var(--card-bg,#161b22)` and was see-through over the Customer Brain; fixed to `var(--bg-card,#1e293b)`. The `.out-ov` overlay backdrop (`rgba(0,0,0,.55)`) was fine — the leak was the sheet's own background. When adding a new sheet, double-check its `background:` var name.
