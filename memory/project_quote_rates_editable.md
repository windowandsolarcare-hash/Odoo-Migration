---
name: project_quote_rates_editable
description: "Quote per-pane/slider prices are now DJ-editable at /owner/quote-rates (editable table + last-changed date). Saved as ir.config_parameter 'quote.rates.override' merged over the hardcoded QUOTE_RATES/QUOTE_DIFFICULTY defaults in dashboard.py via _get_quote_config()."
metadata: 
  node_type: memory
  type: project
  originSessionId: 67954fc8-a6c6-48fa-88c2-cfe13d71df3d
  modified: 2026-07-30T19:06:48.756Z
---

# Editable quote prices (2026-07-30)

DJ wanted the hardcoded window-quote prices in a link/table he can view + edit himself,
with the change date shown.

**Page:** `/owner/quote-rates` (route in dashboard.py `quote_rates_page`, serves
`static/owner/quote_rates.html`). Theme-aware brand page: table of the 6 rate rows (dollars)
+ 3 difficulty rows (shown/edited as **percent markup**, converted to/from the multiplier),
a "Last changed: <date> by <who>" line, and a Save button. Reachable at
https://wsc-field-assistant.onrender.com/owner/quote-rates

**How it works (dashboard.py, ~line 5773+):**
- `QUOTE_RATES` (reg_panes 8, over_panes 9, ss_panes 10.5, reg_sliders 29, over_sliders 34.5,
  triple_sliders 40.5) and `QUOTE_DIFFICULTY` (standard 1.0, hard 1.15, very_hard 1.30) are now
  the **DEFAULTS / fallback** — NOT removed.
- `_get_quote_config()` merges a saved override blob (`ir.config_parameter` key
  **`quote.rates.override`** = `{rates, difficulty, updated_at, updated_by}`) on top of the
  defaults; only known keys honored, negatives clamped. Returns (rates, diff, updated_at, updated_by).
- `_calc_quote_total` and `_quote_breakdown_text` now read the EFFECTIVE config, so an edit takes
  effect instantly for the calculator AND the saved server total AND the on-phone rates fetch —
  no code push, no drift.
- `GET /api/quote/rates` returns effective config + updated_at/by. `POST /api/quote/rates/save`
  writes the override, stamping Pacific `updated_at` (that's the table's "date changed"). If the
  param is missing/empty → pristine defaults, page shows "no edits saved yet".

**NOT editable here (still hardcoded in _calc_quote_total):** Outside-Only mode = total ÷2 then
×1.10. Offered to make it editable; DJ hasn't asked yet.

**Why:** prices were only changeable by editing Python + deploying. Now DJ self-serves.
Verified end-to-end 2026-07-30 (save reg_panes=8.5 round-tripped, over_panes stayed 9, timestamp
stamped) then the test override was deleted to leave defaults pristine.
