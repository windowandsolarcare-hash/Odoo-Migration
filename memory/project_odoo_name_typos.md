---
name: Odoo customer names sometimes differ from how DJ pronounces them
description: Real example — DJ refers to customer as "Jon Hamm" but Odoo has him stored as "John Ham". Search must handle this fuzziness.
type: project
originSessionId: 96c7eadf-7840-4091-9290-6d3aed1806c8
---
DJ's mental model of a customer's name doesn't always match what's stored in Odoo. Real example discovered 2026-04-27:

- DJ says: "Jon Hamm"
- Odoo stored: "John Ham" (partner_id 23052)

This is a data-entry quirk — the original creation likely had a typo, and DJ didn't notice (or did but the record stuck). It's not a bug in DJ's memory, and it's not worth fixing the data (might break Workiz sync history). Search has to handle it.

**Why:** Plain `ilike "Jon Hamm"` doesn't match "John Ham" — the substring isn't there. Even per-word `ilike "Jon"` doesn't match "John" because "Jon" isn't a substring of "John" (the `h` is between `o` and `n`).

**How to apply:**
- `tool_search_customers` in `saunders-render-app/routers/owner/dashboard.py` now does progressive fuzzy: full → AND words → AND with last-char truncation (Hamm→Ham, Jon→Jo) → OR fallback. The `>=3` threshold for truncation is the key — handles both trailing-letter typos and interior-letter substring failures.
- When debugging "Render Claude can't find X", first check Odoo for variant spellings: `name ilike '<part of name>'` with a short prefix.
- If a typo causes ongoing confusion, fix the contact name in Odoo (and verify Workiz sync still works) — but only when the customer's actual job records are stable.
- DON'T add Levenshtein/trigram unless we see real cases the truncation logic misses. Premature optimization.
