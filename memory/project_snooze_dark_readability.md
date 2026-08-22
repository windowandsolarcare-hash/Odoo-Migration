---
name: project_snooze_dark_readability
description: "Shared snooze picker (v2_snooze.js / WSCSnooze) rows were unreadable on dark pages (Follow-ups): light --ink text on white rows. Root: rows used background:var(--surface-2) but some dark pages leave --surface-2 light while --ink is light → white-on-white. Fixed 2026-08-05 with translucent grey bg."
metadata:
  type: project
---

**Symptom (DJ 2026-08-05):** pressing Snooze on Follow-ups → the option labels ("In 1 hour", "This evening", day rows, pick-a-date) were near-invisible — light-grey text on white rows. Header + green "Xh free" + close-X were fine.

**Root cause:** `v2_snooze.js` `.wsc-snz-row/.wsc-snz-slot` (and the date input) used `background:var(--surface-2,#f4f8fc)` + `color:var(--ink,#0f2036)`. On the Follow-ups dark theme, `--surface-2` renders LIGHT (page leaves it light / falls back to #f4f8fc) while `--ink` renders LIGHT (dark-theme text) → light-on-white = invisible. The sheet itself was dark (`--surface`), so the mismatch was only the rows/date-input. (The close-X used `--ink-2`, which resolved dark, so it stayed visible — that's why only the rows broke.)

**Fix:** rows + date input now use a **translucent grey** background `rgba(127,140,160,.16)` (+ border `rgba(127,140,160,.30)`) instead of `var(--surface-2)`, keeping `color:var(--ink)`. A grey overlay is readable on ANY host sheet — light `--ink` on dark sheet, dark `--ink` on light sheet. Verified live.

**Lesson:** shared overlay components must NOT assume a host page defines a CONSISTENT theme token set. If a component's bg comes from one host var and its text from another, a partially-themed page (light --surface-2 + light --ink) breaks it. Use self-contained translucent bg + `var(--ink)` text, OR set the component's own complete palette. See [[feedback_field_readability_sunlight]].
