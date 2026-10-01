---
name: project_quote_save_endpoints_shadowed
description: "[RESOLVED 2026-10-01: dead twins RETIRED from quotes.py, ENDPOINT_MAP current] Route-shadow map for quote-save endpoints (2026-09-28): /owner/api/quote/save and /owner/api/quote/update exist in BOTH quotes.py and dashboard.py — dashboard.py's copies are LIVE (included first, main.py:1038 before quotes at 1045); quotes.py's are DEAD twins. Edit the dashboard.py copies for the live save/update path. accept_to_job_core (quotes.py) IS live. Verify before editing quote-save code."
metadata: 
  node_type: memory
  type: project
  originSessionId: d847a036-234d-4c73-9eca-62500cfee8a7
  modified: 2026-09-28T20:05:50.964Z
---

**The shadow map (verified 2026-09-28 during the Bruce Karp "[Render Quote Tool]" blob-name fix):**
- `api_quote_save` (`@router.post('/api/quote/save')`) and `api_quote_update` (`/api/quote/update`) are each defined **twice** — in `routers/owner/quotes.py` AND `routers/owner/dashboard.py`.
- **dashboard.py's copies are LIVE; quotes.py's are DEAD twins.** Both routers mount at `prefix="/owner"`, and `main.py` includes `owner_dashboard.router` (L1038) **before** `owner_quotes.router` (L1045) → for the identical path, FastAPI matches dashboard's handler first. quotes.py's `api_quote_save`/`api_quote_update` never run. This is the same dashboard-shadows-later-routers class as `/api/hemet/*` and `/owner/ask`.
- **`accept_to_job_core` (quotes.py) IS live** — reached by the live route `/api/quote/accept_to_job` (quotes.py) AND the voice tool (`dashboard.py:2553`); both call the same quotes.py function. This is the "Quote-and-Get-It" flow added 2026-09-05 and was the actual source of Bruce's blob-name bug (fixed via `_quote_line_creates`).

**Why it matters:** editing quotes.py's `api_quote_save`/`api_quote_update` to fix a *live* save-path bug does NOTHING (dead twin) — you must edit the **dashboard.py** copies. During the 2026-09-28 fix, the dashboard.py LIVE copies were already correct (the original 2026-08-01 clean-name fix), so only `accept_to_job_core` + a `_zelle_service_lines` display defense were the real live fix.

**How to apply:** before editing any quote-save/update endpoint, confirm which file serves it (dashboard wins) — or check `ENDPOINT_MAP.md`'s LIVE column. FOLLOW-UP flagged 2026-09-28: retire quotes.py's dead `/api/quote/save`+`/api/quote/update` twins so a future edit can't land on dead code. See [[feedback_check_endpoint_map_first]].

**RESOLVED 2026-10-01:** the dead `api_quote_save`/`api_quote_update` twins were RETIRED from quotes.py (leaving RETIRED breadcrumbs pointing to dashboard.py) and ENDPOINT_MAP regenerated — it now lists only the dashboard.py copies (LIVE). Only one copy exists, so the edit-the-wrong-file trap is closed for these two routes. The general dashboard-shadows-later-routers class remains for OTHER paths (check ENDPOINT_MAP).
