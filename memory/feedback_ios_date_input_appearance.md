---
name: feedback_ios_date_input_appearance
description: "iOS bug: a styled <input type=date> with -webkit-appearance:none won't open/change. Never put appearance:none on a shared input class that date fields use."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 8794a0de-b651-444b-8ec4-52ed56f6927d
---

**Bug (DJ reported 2026-06-24, New Order → existing customer → New Job):** the Date field couldn't be changed on the phone.

**Why:** `new_job.html` `.field-input` set `appearance:none; -webkit-appearance:none;` on the BASE class, and `#job-date` (`<input type="date">`) used that class. On iOS Safari a `type=date` input with `-webkit-appearance:none` renders but the **native date picker won't open / the value is uneditable**. (Selects need appearance:none for a custom arrow; date inputs must NOT have it.)

**How to apply:** Never put `appearance:none` on a shared input class that `type=date`/`type=time` also use. Scope it to `select.field-input` only. Fix (commit 36bb9ae): moved `appearance:none` off base `.field-input` → onto `select.field-input`; added `input[type=date].field-input{min-height:46px}` + visible `::-webkit-calendar-picker-indicator`. **TODO/sweep:** other owner pages with a styled `type=date` on an appearance:none class likely have the same bug — check before shipping date pickers.

**Also fixed same screen:** the back button was a faint `‹` (24px, `var(--text-muted)`, no label) → invisible in sun. Changed to **"‹ Back"**, 17px bold, `var(--text-primary)`. Ties to [[feedback_field_readability_sunlight]] — back/nav controls need a label + contrast, not a bare low-contrast glyph.
