---
name: project_button_color_inherit_darkmode
description: "GOTCHA: text inside a <button> does NOT inherit `color` (or font-family) from ancestors — it uses the UA default (black). Uncolored text in a button card looks fine in light mode (black on white) but is INVISIBLE in dark mode (black on dark). Fix: set color:var(--ink);font-family:inherit on the button."
metadata:
  node_type: memory
  type: project
  originSessionId: 44fd339a-14fd-42e2-adef-f1ae97081400
  modified: 2026-07-26T01:51:40.708Z
---

**2026-07-25 (DJ: "type is black and can't see it" — Customer Analytics page, v2_analytics.html).** The big KPI stat numbers (492, $432,443, etc.) rendered pure black and vanished on the dark cards. Labels were fine.

**Root cause:** the KPI cards are `<button class="kpi">` elements. **Form controls (`<button>`, `<input>`, `<select>`) do NOT inherit `color` or `font-family` from their parent — they use the User-Agent default (`color: ButtonText` ≈ black).** `.kpi .n` (the number) set no explicit color, so it fell to button-black instead of `var(--ink)`. The label `.l` set `color:var(--ink-3)` explicitly, so it stayed visible. In LIGHT mode black-on-white looked correct, hiding the bug; in DARK mode (DJ's phone, system dark → `data-theme="dark"`, `--ink` flips to light `#eaf2fb`) the button ignored `--ink` and stayed black on the dark card = invisible. Confirmed in-browser: `.kpi .n` computed `rgb(0,0,0)` in BOTH themes while `--ink` was `#0f2036`/`#eaf2fb`.

**Fix (commit c148538):** add `color:var(--ink);font-family:inherit` to the `.kpi` button rule → the number now inherits the theme text color (verified rgb(234,242,251) on the dark card, luminance 241, readable). NOT a regression from my recent edits — pre-existing, only visible once viewing in dark mode.

**Scope:** v2_analytics was the ONLY v2 page using `<button>`-based stat cards (all other `.kpi`/`class="n"` stat pages use `<div>`/`<a>`, which inherit color fine). Spot-scanned v2_command in dark mode: 0 dark-on-dark text elements. So isolated.

**Reusable rule:** any time text lives inside a `<button>` (or input/select) and must follow the theme, set `color:var(--ink)` (or `color:inherit`) AND `font-family:inherit` on that control — don't rely on inheritance. Test dark mode by setting `document.documentElement.setAttribute('data-theme','dark')`; light-mode-only testing hides this class of bug. See [[feedback_field_readability_sunlight]], [[project_readability_rollout]].
