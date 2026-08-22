---
name: Odoo has no fuzzy/similar search operator — only ilike substring
description: DJ asked if there's a "fuzzy LIKE" command. Answer: no. Manual truncation+OR is the available solution. PostgreSQL pg_trgm exists but isn't exposed through Odoo's domain RPC.
type: project
originSessionId: 96c7eadf-7840-4091-9290-6d3aed1806c8
---
DJ asked 2026-04-27 whether Odoo has a fuzzy/similar search operator (something more relaxed than `ilike`). Honest answer: **no**.

Available domain operators on `res.partner.search_read` (and other models):
- `=`, `!=` — exact equality
- `like`, `ilike` — case-(in)sensitive substring (auto-wrapped with `%`)
- `=like`, `=ilike` — same but no auto-wrap (provide your own `%`/`_` wildcards)
- `not like`, `not ilike`
- `in`, `not in`
- `child_of`, `parent_of`, `=?`

None of these do edit-distance, phonetic, or trigram matching. They're all literal substring or pattern.

**True fuzzy options that exist but aren't accessible via Odoo's RPC domain:**
- PostgreSQL `pg_trgm` (trigram similarity) — needs raw SQL
- Levenshtein/edit-distance — same
- Soundex/Metaphone — same

**The `=ilike` skeleton trick** (e.g. `=ilike 'J%n%H%m%'` to match "John Ham") works but produces lots of false positives ("Joan Hamilton", "Johnathan Bingham", etc.). Not worth it.

**Why:** Knowing this saves time when someone asks "can't we just use the fuzzy command?" — there isn't one. Don't go hunting for it.

**How to apply:**
- If a user asks for fuzzy search, the answer is: build it manually (truncation + OR conditions) like `tool_search_customers` does, OR build a custom Render endpoint that pulls names and scores them with Python `difflib.get_close_matches`.
- For the W&SC project, current truncation logic in `tool_search_customers` handles ~90% of typos. Don't add server-side fuzzy without concrete failing cases.
- Odoo server actions block imports, so `difflib` etc. can't run there. The fuzzy endpoint would have to live on Render (Python full library access).
