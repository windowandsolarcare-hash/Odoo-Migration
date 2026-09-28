---
name: project_quote_line_clobber_fix
description: "Quote-line writes must target ONLY the windows/quote line (product_id ∈ {141 IN_OUT, 103 OUTSIDE}) and PRESERVE sibling priced lines — never blanket-clear/zero all priced lines. Fixed 2026-09-28 (money/data-integrity): _replace_quote_line + accept_to_job_core were dropping added services (e.g. a $130 Pressure Wash) + mis-recomputing the total. DJ's rule: accept-quote-onto-job PRESERVES existing lines (he deletes unwanted manually)."
metadata: 
  node_type: memory
  type: project
  originSessionId: d847a036-234d-4c73-9eca-62500cfee8a7
  modified: 2026-09-28T20:55:11.386Z
---

**The bug (found during Bruce Karp SO 17698 cleanup, 2026-09-28 — money/data-integrity):** two quote-line write paths clobbered sibling service lines on a multi-line SO:
- **EDIT path** — `_replace_quote_line` (dashboard.py, behind LIVE `/owner/api/quote/update`) soft-deleted (qty+price→0) **every** non-display priced line, then added one windows line recomputed from `_calc_quote_total(counts)`. On a job with windows + an added service, the sibling vanished and the total recomputed wrong ($350→~$221). This was the live bug DJ hit.
- **ACCEPT path** — `accept_to_job_core` (quotes.py) used `[(5,0,0)]` (clear-all) + `_quote_line_creates`. Latent only, because GUARD (a) refused accept if the SO already had any priced line.

**The fix (2026-09-28, both paths — closes the class):**
- `_replace_quote_line` now reads `product_id`, finds the WINDOWS/quote line by membership in `{QUOTE_PRODUCT_IN_OUT=141, QUOTE_PRODUCT_OUTSIDE=103}`, **updates it IN PLACE** (product+qty+price=total+clean label) — adds a windows line only if none exists; note line refreshed in place. **Every other priced line is left untouched.** Confirmed-SO safe (in-place writes, no unlink).
- `accept_to_job_core`: per DJ ("preserve; don't wipe; I'll delete unwanted manually") GUARD (a)'s block was RELAXED block→proceed (INVOICE guard kept), it now reuses `_replace_quote_line`, and the old `cancel→draft→reconfirm→restore-date` dance was DROPPED (proven unneeded — the edit path already runs `_replace_quote_line` in-place on confirmed SOs; keeping the dance would re-confirm a multi-line job + disturb `date_order` = a new risk). Verify guard = windows line present at `total` AND `priced_count≥1` (no longer "exactly 1").
- Proven by a confirmed-SO scratch test (windows $200 + $130 sibling → accept total 250 → sibling preserved, windows→250, total 380, job_type correct, state stayed 'sale').

**Rule / how to apply:** any quote-line write must target ONLY the windows/quote line (`product_id ∈ {141,103}`) and preserve siblings — never blanket-zero/clear priced lines. Accept-onto-job PRESERVES existing lines (DJ's rule). SYSTEM CONSTANTS: `QUOTE_PRODUCT_IN_OUT=141`, `QUOTE_PRODUCT_OUTSIDE=103` (dashboard.py:6729-6730). Related: [[project_quote_save_endpoints_shadowed]] (dashboard.py owns the LIVE save/update; quotes.py twins are dead), [[feedback_reuse_function_follow_full_logic]].
